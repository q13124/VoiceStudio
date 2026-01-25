"""
Tool Gateway

Central gateway for all agent tool invocations.
Enforces policy, handles approvals, and logs all actions.
"""

import time
from dataclasses import dataclass
from typing import Any, Callable, Dict, Optional, Type

from .audit_logger import AuditLogger
from .identity import AgentIdentity, AgentState
from .policy_engine import PolicyDecision, PolicyEngine, PolicyResult
from .tools.base_tool import BaseTool, ToolResult


@dataclass
class GatewayResult:
    """
    Result from the tool gateway.
    
    Attributes:
        success: Whether the action completed successfully
        tool_result: Result from the tool if executed
        policy_result: Policy evaluation result
        denied: Whether the action was denied by policy
        approval_required: Whether approval is pending
        approval_id: ID of the approval request if pending
        error: Error message if failed
    """
    
    success: bool
    tool_result: Optional[ToolResult] = None
    policy_result: Optional[PolicyResult] = None
    denied: bool = False
    approval_required: bool = False
    approval_id: Optional[str] = None
    error: Optional[str] = None


class ToolGateway:
    """
    Central gateway for all agent tool invocations.
    
    This is the ONLY place where side effects should happen.
    All tool invocations are:
    1. Checked against policy
    2. Queued for approval if required
    3. Executed if allowed
    4. Logged to audit trail
    """
    
    def __init__(
        self,
        policy_engine: Optional[PolicyEngine] = None,
        audit_logger: Optional[AuditLogger] = None,
        on_approval_required: Optional[Callable[[str, AgentIdentity, str, dict], bool]] = None,
    ):
        """
        Initialize the tool gateway.
        
        Args:
            policy_engine: Policy engine for access control
            audit_logger: Audit logger for action logging
            on_approval_required: Callback for approval requests.
                                 Returns True if approved, False if denied.
        """
        self._policy = policy_engine or PolicyEngine()
        self._audit = audit_logger or AuditLogger()
        self._on_approval_required = on_approval_required
        
        # Registered tools
        self._tools: Dict[str, BaseTool] = {}
        
        # Register built-in tools
        self._register_builtin_tools()
    
    def _register_builtin_tools(self) -> None:
        """Register built-in tool implementations."""
        from .tools.file_tools import ReadFileTool, WriteFileTool, DeleteFileTool
        from .tools.process_tools import RunProcessTool
        from .tools.network_tools import HttpRequestTool
        
        for tool_class in [
            ReadFileTool,
            WriteFileTool,
            DeleteFileTool,
            RunProcessTool,
            HttpRequestTool,
        ]:
            tool = tool_class()
            self._tools[tool.name] = tool
    
    def register_tool(self, tool: BaseTool) -> None:
        """
        Register a custom tool.
        
        Args:
            tool: The tool to register
        """
        self._tools[tool.name] = tool
    
    def get_tool(self, name: str) -> Optional[BaseTool]:
        """Get a registered tool by name."""
        return self._tools.get(name)
    
    def list_tools(self) -> list:
        """List all registered tools."""
        return list(self._tools.keys())
    
    def execute(
        self,
        agent: AgentIdentity,
        tool_name: str,
        parameters: Dict[str, Any],
        skip_policy: bool = False,
    ) -> GatewayResult:
        """
        Execute a tool through the gateway.
        
        Args:
            agent: The agent requesting the action
            tool_name: Name of the tool to execute
            parameters: Tool parameters
            skip_policy: If True, skip policy check (use with caution)
            
        Returns:
            GatewayResult with execution outcome
        """
        start_time = time.time()
        
        # Check agent state
        if agent.state == AgentState.QUARANTINED:
            self._audit.log_denied(
                agent=agent,
                tool_name=tool_name,
                parameters=parameters,
                reason="Agent is quarantined",
            )
            return GatewayResult(
                success=False,
                denied=True,
                error="Agent is quarantined and cannot perform actions",
            )
        
        if agent.state == AgentState.TERMINATED:
            return GatewayResult(
                success=False,
                denied=True,
                error="Agent is terminated",
            )
        
        # Get tool
        tool = self._tools.get(tool_name)
        if tool is None:
            self._audit.log_denied(
                agent=agent,
                tool_name=tool_name,
                parameters=parameters,
                reason=f"Unknown tool: {tool_name}",
            )
            return GatewayResult(
                success=False,
                error=f"Unknown tool: {tool_name}",
            )
        
        # Validate parameters
        validation_error = tool.validate_params(parameters)
        if validation_error:
            self._audit.log_denied(
                agent=agent,
                tool_name=tool_name,
                parameters=parameters,
                reason=f"Parameter validation failed: {validation_error}",
            )
            return GatewayResult(
                success=False,
                error=validation_error,
            )
        
        # Evaluate policy
        policy_result = None
        if not skip_policy:
            policy_result = self._policy.evaluate(agent, tool_name, parameters)
            
            if policy_result.decision == PolicyDecision.DENY:
                self._audit.log_denied(
                    agent=agent,
                    tool_name=tool_name,
                    parameters=parameters,
                    reason=policy_result.reason,
                    risk_tier=policy_result.risk_tier,
                )
                return GatewayResult(
                    success=False,
                    policy_result=policy_result,
                    denied=True,
                    error=policy_result.reason,
                )
            
            if policy_result.decision == PolicyDecision.REQUIRE_APPROVAL:
                # Handle approval
                approved = self._handle_approval(
                    agent, tool_name, parameters, policy_result
                )
                
                if not approved:
                    self._audit.log_denied(
                        agent=agent,
                        tool_name=tool_name,
                        parameters=parameters,
                        reason="Approval denied or not granted",
                        risk_tier=policy_result.risk_tier,
                    )
                    return GatewayResult(
                        success=False,
                        policy_result=policy_result,
                        denied=True,
                        error="Action requires approval which was not granted",
                    )
        
        # Execute tool
        try:
            with self._audit.track(
                agent=agent,
                tool_name=tool_name,
                parameters=parameters,
                risk_tier=policy_result.risk_tier if policy_result else "low",
            ) as ctx:
                tool_result = tool.execute(**parameters)
                ctx.set_output(tool_result.output if tool_result.success else None)
            
            return GatewayResult(
                success=tool_result.success,
                tool_result=tool_result,
                policy_result=policy_result,
                error=tool_result.error if not tool_result.success else None,
            )
            
        except Exception as e:
            duration_ms = int((time.time() - start_time) * 1000)
            self._audit.log_failure(
                agent=agent,
                tool_name=tool_name,
                parameters=parameters,
                error=e,
                duration_ms=duration_ms,
                risk_tier=policy_result.risk_tier if policy_result else "low",
            )
            return GatewayResult(
                success=False,
                policy_result=policy_result,
                error=str(e),
            )
    
    def _handle_approval(
        self,
        agent: AgentIdentity,
        tool_name: str,
        parameters: Dict[str, Any],
        policy_result: PolicyResult,
    ) -> bool:
        """
        Handle approval flow for high-risk actions.
        
        Returns True if approved, False otherwise.
        """
        if self._on_approval_required is None:
            # No approval handler - deny by default
            return False
        
        # Update agent state
        original_state = agent.state
        agent.state = AgentState.AWAITING_APPROVAL
        
        try:
            # Request approval
            import uuid
            approval_id = str(uuid.uuid4())
            
            approved = self._on_approval_required(
                approval_id,
                agent,
                tool_name,
                parameters,
            )
            
            return approved
            
        finally:
            # Restore agent state
            if agent.state == AgentState.AWAITING_APPROVAL:
                agent.state = original_state
    
    def check_policy(
        self,
        agent: AgentIdentity,
        tool_name: str,
        parameters: Dict[str, Any],
    ) -> PolicyResult:
        """
        Check policy without executing.
        
        Useful for UI to show what would happen.
        """
        return self._policy.evaluate(agent, tool_name, parameters)
    
    def get_audit_store(self):
        """Get the audit store for querying logs."""
        return self._audit.get_store()

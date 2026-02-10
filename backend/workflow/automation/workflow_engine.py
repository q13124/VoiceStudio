"""
Phase 6: Workflow Automation
Task 6.4: Workflow automation engine for batch processing.
"""

import asyncio
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Optional
import json
import logging
import uuid

logger = logging.getLogger(__name__)


class WorkflowStatus(Enum):
    """Workflow execution status."""
    PENDING = "pending"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class StepType(Enum):
    """Types of workflow steps."""
    SYNTHESIZE = "synthesize"
    CLONE_VOICE = "clone_voice"
    APPLY_EFFECTS = "apply_effects"
    EXPORT = "export"
    IMPORT = "import"
    TRANSFORM = "transform"
    CONDITION = "condition"
    LOOP = "loop"
    PARALLEL = "parallel"
    CUSTOM = "custom"


@dataclass
class StepResult:
    """Result of a workflow step."""
    success: bool
    output: Any = None
    error: Optional[str] = None
    duration_seconds: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class WorkflowStep:
    """A single workflow step."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    step_type: StepType = StepType.CUSTOM
    config: dict[str, Any] = field(default_factory=dict)
    inputs: dict[str, str] = field(default_factory=dict)  # variable mappings
    outputs: dict[str, str] = field(default_factory=dict)  # variable mappings
    on_error: str = "fail"  # fail, skip, retry
    retry_count: int = 0
    condition: Optional[str] = None  # expression to evaluate


@dataclass
class WorkflowDefinition:
    """Definition of a complete workflow."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    description: str = ""
    version: str = "1.0"
    steps: list[WorkflowStep] = field(default_factory=list)
    variables: dict[str, Any] = field(default_factory=dict)
    triggers: list[dict[str, Any]] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)


@dataclass
class WorkflowExecution:
    """State of a workflow execution."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    workflow_id: str = ""
    status: WorkflowStatus = WorkflowStatus.PENDING
    current_step_index: int = 0
    variables: dict[str, Any] = field(default_factory=dict)
    step_results: list[StepResult] = field(default_factory=list)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error: Optional[str] = None


class StepExecutor(ABC):
    """Abstract base class for step executors."""
    
    @property
    @abstractmethod
    def step_type(self) -> StepType:
        """Get the step type this executor handles."""
        pass
    
    @abstractmethod
    async def execute(
        self,
        step: WorkflowStep,
        context: dict[str, Any]
    ) -> StepResult:
        """Execute the step."""
        pass


class SynthesizeStepExecutor(StepExecutor):
    """Executor for synthesis steps."""
    
    @property
    def step_type(self) -> StepType:
        return StepType.SYNTHESIZE
    
    async def execute(
        self,
        step: WorkflowStep,
        context: dict[str, Any]
    ) -> StepResult:
        """Execute synthesis step."""
        start_time = datetime.now()
        
        try:
            text = step.config.get("text", "")
            voice = step.config.get("voice", "default")
            engine = step.config.get("engine", "xtts")
            
            # Resolve variables
            if text.startswith("$"):
                text = context.get(text[1:], "")
            
            # Simulate synthesis
            await asyncio.sleep(0.5)
            
            output_path = Path("temp") / f"synthesis_{step.id}.wav"
            
            return StepResult(
                success=True,
                output={"audio_path": str(output_path)},
                duration_seconds=(datetime.now() - start_time).total_seconds()
            )
            
        except Exception as e:
            return StepResult(
                success=False,
                error=str(e),
                duration_seconds=(datetime.now() - start_time).total_seconds()
            )


class ApplyEffectsStepExecutor(StepExecutor):
    """Executor for applying audio effects."""
    
    @property
    def step_type(self) -> StepType:
        return StepType.APPLY_EFFECTS
    
    async def execute(
        self,
        step: WorkflowStep,
        context: dict[str, Any]
    ) -> StepResult:
        """Execute effects step."""
        start_time = datetime.now()
        
        try:
            audio_path = step.config.get("audio_path", "")
            effects = step.config.get("effects", [])
            
            # Resolve variables
            if audio_path.startswith("$"):
                audio_path = context.get(audio_path[1:], "")
            
            # Simulate effects processing
            await asyncio.sleep(0.3)
            
            output_path = Path("temp") / f"effects_{step.id}.wav"
            
            return StepResult(
                success=True,
                output={"audio_path": str(output_path)},
                metadata={"effects_applied": effects},
                duration_seconds=(datetime.now() - start_time).total_seconds()
            )
            
        except Exception as e:
            return StepResult(
                success=False,
                error=str(e),
                duration_seconds=(datetime.now() - start_time).total_seconds()
            )


class ExportStepExecutor(StepExecutor):
    """Executor for export steps."""
    
    @property
    def step_type(self) -> StepType:
        return StepType.EXPORT
    
    async def execute(
        self,
        step: WorkflowStep,
        context: dict[str, Any]
    ) -> StepResult:
        """Execute export step."""
        start_time = datetime.now()
        
        try:
            audio_path = step.config.get("audio_path", "")
            output_format = step.config.get("format", "wav")
            output_dir = step.config.get("output_dir", "output")
            
            # Resolve variables
            if audio_path.startswith("$"):
                audio_path = context.get(audio_path[1:], "")
            
            # Simulate export
            await asyncio.sleep(0.2)
            
            output_path = Path(output_dir) / f"export_{step.id}.{output_format}"
            
            return StepResult(
                success=True,
                output={"output_path": str(output_path)},
                duration_seconds=(datetime.now() - start_time).total_seconds()
            )
            
        except Exception as e:
            return StepResult(
                success=False,
                error=str(e),
                duration_seconds=(datetime.now() - start_time).total_seconds()
            )


class WorkflowEngine:
    """Engine for executing workflows."""
    
    def __init__(self):
        self._executors: dict[StepType, StepExecutor] = {}
        self._workflows: dict[str, WorkflowDefinition] = {}
        self._executions: dict[str, WorkflowExecution] = {}
        self._running: dict[str, asyncio.Task] = {}
        
        # Register default executors
        self.register_executor(SynthesizeStepExecutor())
        self.register_executor(ApplyEffectsStepExecutor())
        self.register_executor(ExportStepExecutor())
    
    def register_executor(self, executor: StepExecutor) -> None:
        """Register a step executor."""
        self._executors[executor.step_type] = executor
    
    def register_workflow(self, workflow: WorkflowDefinition) -> None:
        """Register a workflow definition."""
        self._workflows[workflow.id] = workflow
    
    def get_workflow(self, workflow_id: str) -> Optional[WorkflowDefinition]:
        """Get a workflow by ID."""
        return self._workflows.get(workflow_id)
    
    async def start_workflow(
        self,
        workflow_id: str,
        variables: Optional[dict[str, Any]] = None
    ) -> str:
        """Start a workflow execution."""
        workflow = self._workflows.get(workflow_id)
        if not workflow:
            raise ValueError(f"Workflow not found: {workflow_id}")
        
        # Create execution
        execution = WorkflowExecution(
            workflow_id=workflow_id,
            variables={**workflow.variables, **(variables or {})},
        )
        
        self._executions[execution.id] = execution
        
        # Start execution task
        task = asyncio.create_task(self._execute_workflow(execution, workflow))
        self._running[execution.id] = task
        
        return execution.id
    
    async def pause_workflow(self, execution_id: str) -> bool:
        """Pause a workflow execution."""
        execution = self._executions.get(execution_id)
        if execution and execution.status == WorkflowStatus.RUNNING:
            execution.status = WorkflowStatus.PAUSED
            return True
        return False
    
    async def resume_workflow(self, execution_id: str) -> bool:
        """Resume a paused workflow execution."""
        execution = self._executions.get(execution_id)
        if execution and execution.status == WorkflowStatus.PAUSED:
            workflow = self._workflows.get(execution.workflow_id)
            if workflow:
                execution.status = WorkflowStatus.RUNNING
                task = asyncio.create_task(self._execute_workflow(execution, workflow))
                self._running[execution_id] = task
                return True
        return False
    
    async def cancel_workflow(self, execution_id: str) -> bool:
        """Cancel a workflow execution."""
        if execution_id in self._running:
            self._running[execution_id].cancel()
            del self._running[execution_id]
        
        execution = self._executions.get(execution_id)
        if execution:
            execution.status = WorkflowStatus.CANCELLED
            return True
        
        return False
    
    def get_execution(self, execution_id: str) -> Optional[WorkflowExecution]:
        """Get an execution by ID."""
        return self._executions.get(execution_id)
    
    async def _execute_workflow(
        self,
        execution: WorkflowExecution,
        workflow: WorkflowDefinition
    ) -> None:
        """Execute a workflow."""
        execution.status = WorkflowStatus.RUNNING
        execution.started_at = datetime.now()
        
        try:
            while execution.current_step_index < len(workflow.steps):
                # Check for pause/cancel
                if execution.status == WorkflowStatus.PAUSED:
                    return
                
                if execution.status == WorkflowStatus.CANCELLED:
                    return
                
                step = workflow.steps[execution.current_step_index]
                
                # Check condition
                if step.condition:
                    if not self._evaluate_condition(step.condition, execution.variables):
                        execution.current_step_index += 1
                        continue
                
                # Execute step
                result = await self._execute_step(step, execution.variables)
                execution.step_results.append(result)
                
                if result.success:
                    # Update variables from outputs
                    if result.output:
                        for key, var_name in step.outputs.items():
                            if key in result.output:
                                execution.variables[var_name] = result.output[key]
                    
                    execution.current_step_index += 1
                else:
                    if step.on_error == "skip":
                        execution.current_step_index += 1
                    elif step.on_error == "retry" and step.retry_count > 0:
                        step.retry_count -= 1
                        # Don't increment index - retry same step
                    else:
                        execution.status = WorkflowStatus.FAILED
                        execution.error = result.error
                        return
            
            execution.status = WorkflowStatus.COMPLETED
            
        except asyncio.CancelledError:
            execution.status = WorkflowStatus.CANCELLED
        except Exception as e:
            execution.status = WorkflowStatus.FAILED
            execution.error = str(e)
            logger.error(f"Workflow error: {e}")
        finally:
            execution.completed_at = datetime.now()
            if execution.id in self._running:
                del self._running[execution.id]
    
    async def _execute_step(
        self,
        step: WorkflowStep,
        context: dict[str, Any]
    ) -> StepResult:
        """Execute a single step."""
        executor = self._executors.get(step.step_type)
        if not executor:
            return StepResult(
                success=False,
                error=f"No executor for step type: {step.step_type}"
            )
        
        # Resolve input variables
        resolved_config = step.config.copy()
        for key, var_name in step.inputs.items():
            if var_name in context:
                resolved_config[key] = context[var_name]
        
        step_with_resolved = WorkflowStep(
            id=step.id,
            name=step.name,
            step_type=step.step_type,
            config=resolved_config,
            inputs=step.inputs,
            outputs=step.outputs,
            on_error=step.on_error,
            retry_count=step.retry_count,
        )
        
        return await executor.execute(step_with_resolved, context)
    
    def _evaluate_condition(self, condition: str, variables: dict[str, Any]) -> bool:
        """Evaluate a condition expression."""
        # Simple evaluation - in production use a safe expression evaluator
        try:
            return bool(eval(condition, {"__builtins__": {}}, variables))
        except Exception:
            return False
    
    def save_workflow(self, workflow: WorkflowDefinition, path: Path) -> None:
        """Save a workflow to file."""
        data = {
            "id": workflow.id,
            "name": workflow.name,
            "description": workflow.description,
            "version": workflow.version,
            "steps": [
                {
                    "id": s.id,
                    "name": s.name,
                    "step_type": s.step_type.value,
                    "config": s.config,
                    "inputs": s.inputs,
                    "outputs": s.outputs,
                    "on_error": s.on_error,
                    "retry_count": s.retry_count,
                    "condition": s.condition,
                }
                for s in workflow.steps
            ],
            "variables": workflow.variables,
            "triggers": workflow.triggers,
        }
        
        path.write_text(json.dumps(data, indent=2))
    
    def load_workflow(self, path: Path) -> WorkflowDefinition:
        """Load a workflow from file."""
        data = json.loads(path.read_text())
        
        steps = [
            WorkflowStep(
                id=s["id"],
                name=s["name"],
                step_type=StepType(s["step_type"]),
                config=s["config"],
                inputs=s.get("inputs", {}),
                outputs=s.get("outputs", {}),
                on_error=s.get("on_error", "fail"),
                retry_count=s.get("retry_count", 0),
                condition=s.get("condition"),
            )
            for s in data["steps"]
        ]
        
        return WorkflowDefinition(
            id=data["id"],
            name=data["name"],
            description=data.get("description", ""),
            version=data.get("version", "1.0"),
            steps=steps,
            variables=data.get("variables", {}),
            triggers=data.get("triggers", []),
        )

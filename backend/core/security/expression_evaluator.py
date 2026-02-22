"""
Safe Expression Evaluator.

Replaces dangerous eval() calls with a restricted, safe expression evaluator.
Only allows simple comparison and logical operations on provided variables.

Security fixes for:
- lip_sync_service.py (frame rate parsing)
- workflow_engine.py (condition evaluation)
- workflows.py (condition evaluation)
"""

from __future__ import annotations

import ast
import logging
import operator
from collections.abc import Callable
from typing import Any

logger = logging.getLogger(__name__)


class ExpressionError(Exception):
    """Raised when expression evaluation fails."""

    def __init__(self, message: str, expression: str):
        super().__init__(message)
        self.expression = expression


# Safe operators for condition evaluation
SAFE_OPERATORS: dict[type[ast.AST], Callable[..., Any]] = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos,
    ast.Eq: operator.eq,
    ast.NotEq: operator.ne,
    ast.Lt: operator.lt,
    ast.LtE: operator.le,
    ast.Gt: operator.gt,
    ast.GtE: operator.ge,
    ast.And: lambda a, b: a and b,
    ast.Or: lambda a, b: a or b,
    ast.Not: operator.not_,
    ast.In: lambda a, b: a in b,
    ast.NotIn: lambda a, b: a not in b,
    ast.Is: operator.is_,
    ast.IsNot: operator.is_not,
}


class SafeExpressionEvaluator:
    """
    Evaluates simple expressions without using eval().

    Supports:
    - Arithmetic: +, -, *, /, //, %, **
    - Comparisons: ==, !=, <, <=, >, >=, in, not in, is, is not
    - Logical: and, or, not
    - Literals: numbers, strings, booleans, None, lists, dicts
    - Variables: from provided context
    - Attribute access: limited to one level (e.g., obj.attr)
    """

    def __init__(self, max_complexity: int = 100):
        """
        Initialize evaluator.

        Args:
            max_complexity: Maximum AST node count to prevent DoS
        """
        self.max_complexity = max_complexity

    def evaluate(
        self,
        expression: str,
        variables: dict[str, Any] | None = None,
    ) -> Any:
        """
        Safely evaluate an expression.

        Args:
            expression: Expression string to evaluate
            variables: Variable context for name resolution

        Returns:
            Evaluated result

        Raises:
            ExpressionError: If expression is invalid or too complex
        """
        if not expression or not expression.strip():
            raise ExpressionError("Empty expression", expression)

        variables = variables or {}

        try:
            tree = ast.parse(expression, mode="eval")
        except SyntaxError as e:
            raise ExpressionError(f"Syntax error: {e}", expression)

        # Check complexity
        node_count = sum(1 for _ in ast.walk(tree))
        if node_count > self.max_complexity:
            raise ExpressionError(
                f"Expression too complex ({node_count} nodes)",
                expression,
            )

        try:
            return self._eval_node(tree.body, variables)
        except ExpressionError:
            raise
        except Exception as e:
            raise ExpressionError(f"Evaluation error: {e}", expression)

    def _eval_node(self, node: ast.AST, variables: dict[str, Any]) -> Any:
        """Evaluate an AST node."""
        # Constants (Python 3.8+)
        if isinstance(node, ast.Constant):
            return node.value

        # Numbers (Python 3.7 compatibility)
        if isinstance(node, ast.Num):
            return node.n

        # Strings (Python 3.7 compatibility)
        if isinstance(node, ast.Str):
            return node.s

        # Names (variables)
        if isinstance(node, ast.Name):
            name = node.id
            if name in variables:
                return variables[name]
            # Allow True, False, None
            if name == "True":
                return True
            if name == "False":
                return False
            if name == "None":
                return None
            raise ExpressionError(f"Unknown variable: {name}", "")

        # Binary operations
        if isinstance(node, ast.BinOp):
            op_type: type[ast.AST] = type(node.op)
            if op_type not in SAFE_OPERATORS:
                raise ExpressionError(f"Unsupported operator: {op_type.__name__}", "")
            left = self._eval_node(node.left, variables)
            right = self._eval_node(node.right, variables)
            return SAFE_OPERATORS[op_type](left, right)

        # Unary operations
        if isinstance(node, ast.UnaryOp):
            op_type = type(node.op)
            if op_type not in SAFE_OPERATORS:
                raise ExpressionError(f"Unsupported unary operator: {op_type.__name__}", "")
            operand = self._eval_node(node.operand, variables)
            return SAFE_OPERATORS[op_type](operand)

        # Comparisons
        if isinstance(node, ast.Compare):
            left = self._eval_node(node.left, variables)
            for op, comparator in zip(node.ops, node.comparators):
                op_type = type(op)
                if op_type not in SAFE_OPERATORS:
                    raise ExpressionError(f"Unsupported comparison: {op_type.__name__}", "")
                right = self._eval_node(comparator, variables)
                if not SAFE_OPERATORS[op_type](left, right):
                    return False
                left = right
            return True

        # Boolean operations
        if isinstance(node, ast.BoolOp):
            op_type = type(node.op)
            if op_type == ast.And:
                result = True
                for value in node.values:
                    result = self._eval_node(value, variables)
                    if not result:
                        return result
                return result
            elif op_type == ast.Or:
                result = False
                for value in node.values:
                    result = self._eval_node(value, variables)
                    if result:
                        return result
                return result

        # Lists
        if isinstance(node, ast.List):
            return [self._eval_node(elt, variables) for elt in node.elts]

        # Tuples
        if isinstance(node, ast.Tuple):
            return tuple(self._eval_node(elt, variables) for elt in node.elts)

        # Dicts
        if isinstance(node, ast.Dict):
            return {
                self._eval_node(k, variables): self._eval_node(v, variables)
                for k, v in zip(node.keys, node.values)
                if k is not None
            }

        # Simple attribute access (one level only)
        if isinstance(node, ast.Attribute):
            value = self._eval_node(node.value, variables)
            attr = node.attr
            # Restrict to safe attributes (no dunder methods)
            if attr.startswith("_"):
                raise ExpressionError(f"Cannot access private attribute: {attr}", "")
            if not hasattr(value, attr):
                raise ExpressionError(f"Attribute not found: {attr}", "")
            return getattr(value, attr)

        # Subscript (indexing)
        if isinstance(node, ast.Subscript):
            value = self._eval_node(node.value, variables)
            # Python 3.9+ uses slice directly, earlier uses Index wrapper
            slice_node = node.slice
            if isinstance(slice_node, ast.Index):
                slice_node = getattr(slice_node, "value", slice_node)
            index = self._eval_node(slice_node, variables)
            return value[index]

        # IfExp (ternary)
        if isinstance(node, ast.IfExp):
            test = self._eval_node(node.test, variables)
            if test:
                return self._eval_node(node.body, variables)
            else:
                return self._eval_node(node.orelse, variables)

        raise ExpressionError(f"Unsupported expression type: {type(node).__name__}", "")


def parse_frame_rate(rate_str: str, default: float = 30.0) -> float:
    """
    Safely parse FFmpeg frame rate string.

    Handles formats like:
    - "30/1" (fraction)
    - "29.97" (decimal)
    - "30" (integer)
    - "24000/1001" (NTSC formats)

    Args:
        rate_str: Frame rate string from FFmpeg
        default: Default value if parsing fails

    Returns:
        Frame rate as float
    """
    if not rate_str:
        return default

    rate_str = rate_str.strip()

    try:
        if "/" in rate_str:
            parts = rate_str.split("/", 1)
            if len(parts) == 2:
                num = float(parts[0])
                den = float(parts[1])
                if den != 0:
                    return num / den
                logger.warning(f"Zero denominator in frame rate: {rate_str}")
                return default

        return float(rate_str)
    except (ValueError, TypeError) as e:
        logger.warning(f"Failed to parse frame rate '{rate_str}': {e}")
        return default


def evaluate_condition(
    condition: str,
    variables: dict[str, Any] | None = None,
    default: bool = False,
) -> bool:
    """
    Safely evaluate a condition expression.

    Args:
        condition: Condition expression to evaluate
        variables: Variable context
        default: Default value if evaluation fails

    Returns:
        Boolean result
    """
    if not condition:
        return default

    evaluator = SafeExpressionEvaluator()

    try:
        result = evaluator.evaluate(condition, variables)
        return bool(result)
    except ExpressionError as e:
        logger.warning(f"Failed to evaluate condition '{condition}': {e}")
        return default


# Module-level evaluator instance
_evaluator: SafeExpressionEvaluator | None = None


def get_evaluator() -> SafeExpressionEvaluator:
    """Get or create the global safe evaluator."""
    global _evaluator
    if _evaluator is None:
        _evaluator = SafeExpressionEvaluator()
    return _evaluator

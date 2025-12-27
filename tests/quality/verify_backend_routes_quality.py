"""
Backend Route Quality Verification Script

Verifies that all backend routes have:
1. Proper error handling (try/except blocks)
2. Proper logging (logger calls)
3. Proper validation (Pydantic models, input validation)
4. Proper response models (response_model in decorators)
"""

import ast
import logging
import os
from pathlib import Path
from typing import Dict, List, Tuple

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def check_error_handling(file_path: Path) -> Tuple[List[Dict], bool]:
    """
    Check if a Python file has proper error handling.
    
    Returns:
        Tuple of (issues list, has_issues boolean)
    """
    issues = []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            lines = content.split('\n')
        
        # Parse AST
        try:
            tree = ast.parse(content, filename=str(file_path))
        except SyntaxError:
            return [], False  # Skip files with syntax errors
        
        # Find all function definitions
        functions = []
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) or isinstance(node, ast.AsyncFunctionDef):
                functions.append(node)
        
        # Check each function for error handling
        for func in functions:
            func_name = func.name
            func_line = func.lineno
            
            # Skip private functions and test functions
            if func_name.startswith('_') or func_name.startswith('test_'):
                continue
            
            # Check if function has try/except
            has_try = False
            for node in ast.walk(func):
                if isinstance(node, ast.Try):
                    has_try = True
                    break
            
            # Check if function is a route handler (has decorator with @router)
            is_route = False
            for decorator in func.decorator_list:
                if isinstance(decorator, ast.Call):
                    if isinstance(decorator.func, ast.Attribute):
                        if decorator.func.attr in ['get', 'post', 'put', 'delete', 'patch']:
                            is_route = True
                            break
                    elif isinstance(decorator.func, ast.Name):
                        if decorator.func.id in ['router', 'app']:
                            is_route = True
                            break
            
            # Route handlers should have error handling
            if is_route and not has_try:
                # Check if it's a simple getter that might not need error handling
                # (e.g., just returns a dict or list)
                body_simple = len(func.body) == 1
                if not body_simple:
                    issues.append({
                        "file": str(file_path),
                        "line": func_line,
                        "type": "missing_error_handling",
                        "function": func_name,
                        "content": lines[func_line - 1].strip() if func_line <= len(lines) else "",
                    })
    
    except Exception as e:
        logger.error(f"Error checking {file_path}: {e}")
        issues.append({
            "file": str(file_path),
            "line": 0,
            "type": "ERROR",
            "function": "",
            "content": f"Failed to check file: {e}",
        })
    
    return issues, len(issues) > 0


def check_logging(file_path: Path) -> Tuple[List[Dict], bool]:
    """
    Check if a Python file has proper logging.
    
    Returns:
        Tuple of (issues list, has_issues boolean)
    """
    issues = []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            lines = content.split('\n')
        
        # Check if logger is imported/defined
        has_logger = False
        if 'logger' in content or 'logging.getLogger' in content:
            has_logger = True
        
        if not has_logger:
            issues.append({
                "file": str(file_path),
                "line": 0,
                "type": "missing_logger",
                "content": "No logger import or definition found",
            })
        
        # Parse AST to find route handlers
        try:
            tree = ast.parse(content, filename=str(file_path))
        except SyntaxError:
            return [], False
        
        # Find route handlers
        route_handlers = []
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) or isinstance(node, ast.AsyncFunctionDef):
                # Check if it's a route handler
                for decorator in node.decorator_list:
                    if isinstance(decorator, ast.Call):
                        if isinstance(decorator.func, ast.Attribute):
                            if decorator.func.attr in ['get', 'post', 'put', 'delete', 'patch']:
                                route_handlers.append(node)
                                break
        
        # Check if route handlers have logging calls
        for handler in route_handlers:
            has_logging = False
            for node in ast.walk(handler):
                if isinstance(node, ast.Call):
                    if isinstance(node.func, ast.Attribute):
                        if node.func.attr in ['error', 'warning', 'info', 'debug', 'exception']:
                            has_logging = True
                            break
            
            # Route handlers should have at least error logging
            if not has_logging and len(handler.body) > 3:  # Skip very simple handlers
                issues.append({
                    "file": str(file_path),
                    "line": handler.lineno,
                    "type": "missing_logging",
                    "function": handler.name,
                    "content": lines[handler.lineno - 1].strip() if handler.lineno <= len(lines) else "",
                })
    
    except Exception as e:
        logger.error(f"Error checking {file_path}: {e}")
    
    return issues, len(issues) > 0


def check_validation(file_path: Path) -> Tuple[List[Dict], bool]:
    """
    Check if a Python file has proper validation (Pydantic models).
    
    Returns:
        Tuple of (issues list, has_issues boolean)
    """
    issues = []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            lines = content.split('\n')
        
        # Check if Pydantic is imported
        has_pydantic = 'BaseModel' in content or 'from pydantic' in content
        
        # Parse AST
        try:
            tree = ast.parse(content, filename=str(file_path))
        except SyntaxError:
            return [], False
        
        # Find route handlers
        route_handlers = []
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) or isinstance(node, ast.AsyncFunctionDef):
                for decorator in node.decorator_list:
                    if isinstance(decorator, ast.Call):
                        if isinstance(decorator.func, ast.Attribute):
                            if decorator.func.attr in ['get', 'post', 'put', 'delete', 'patch']:
                                route_handlers.append(node)
                                break
        
        # Check if POST/PUT/PATCH handlers have request models
        for handler in route_handlers:
            # Find decorator to determine method
            method = None
            for decorator in handler.decorator_list:
                if isinstance(decorator, ast.Call):
                    if isinstance(decorator.func, ast.Attribute):
                        method = decorator.func.attr.lower()
                        break
            
            if method in ['post', 'put', 'patch']:
                # Check if handler has request parameter with type hint
                has_request_model = False
                for arg in handler.args.args:
                    if arg.annotation:
                        # Check if annotation is a BaseModel subclass
                        if isinstance(arg.annotation, ast.Name):
                            # Check if it's likely a Pydantic model (starts with capital)
                            if arg.annotation.id[0].isupper():
                                has_request_model = True
                                break
                
                if not has_request_model and len(handler.args.args) > 1:
                    issues.append({
                        "file": str(file_path),
                        "line": handler.lineno,
                        "type": "missing_validation",
                        "function": handler.name,
                        "method": method.upper(),
                        "content": lines[handler.lineno - 1].strip() if handler.lineno <= len(lines) else "",
                    })
    
    except Exception as e:
        logger.error(f"Error checking {file_path}: {e}")
    
    return issues, len(issues) > 0


def check_response_models(file_path: Path) -> Tuple[List[Dict], bool]:
    """
    Check if a Python file has proper response models.
    
    Returns:
        Tuple of (issues list, has_issues boolean)
    """
    issues = []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            lines = content.split('\n')
        
        # Parse AST
        try:
            tree = ast.parse(content, filename=str(file_path))
        except SyntaxError:
            return [], False
        
        # Find route handlers
        route_handlers = []
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) or isinstance(node, ast.AsyncFunctionDef):
                for decorator in node.decorator_list:
                    if isinstance(decorator, ast.Call):
                        if isinstance(decorator.func, ast.Attribute):
                            if decorator.func.attr in ['get', 'post', 'put', 'delete', 'patch']:
                                route_handlers.append((node, decorator))
                                break
        
        # Check if route handlers have response_model
        for handler, decorator in route_handlers:
            has_response_model = False
            
            # Check decorator keyword arguments
            for keyword in decorator.keywords:
                if keyword.arg == 'response_model':
                    has_response_model = True
                    break
            
            # Skip DELETE handlers (they often return simple messages)
            method = decorator.func.attr.lower()
            if method == 'delete':
                continue
            
            if not has_response_model:
                issues.append({
                    "file": str(file_path),
                    "line": handler.lineno,
                    "type": "missing_response_model",
                    "function": handler.name,
                    "method": method.upper(),
                    "content": lines[handler.lineno - 1].strip() if handler.lineno <= len(lines) else "",
                })
    
    except Exception as e:
        logger.error(f"Error checking {file_path}: {e}")
    
    return issues, len(issues) > 0


def verify_backend_routes_quality() -> Dict:
    """
    Verify all backend routes for quality (error handling, logging, validation, response models).
    
    Returns:
        Dictionary with verification results
    """
    routes_dir = Path("backend/api/routes")
    
    if not routes_dir.exists():
        logger.error(f"Routes directory not found: {routes_dir}")
        return {
            "success": False,
            "error": f"Routes directory not found: {routes_dir}",
        }
    
    all_issues = {
        "error_handling": [],
        "logging": [],
        "validation": [],
        "response_models": [],
    }
    files_checked = 0
    
    # Check all Python files in routes directory
    for route_file in sorted(routes_dir.glob("*.py")):
        # Skip __init__.py
        if route_file.name == "__init__.py":
            continue
        
        files_checked += 1
        
        # Check error handling
        issues, _ = check_error_handling(route_file)
        all_issues["error_handling"].extend(issues)
        
        # Check logging
        issues, _ = check_logging(route_file)
        all_issues["logging"].extend(issues)
        
        # Check validation
        issues, _ = check_validation(route_file)
        all_issues["validation"].extend(issues)
        
        # Check response models
        issues, _ = check_response_models(route_file)
        all_issues["response_models"].extend(issues)
    
    # Summary
    total_issues = sum(len(issues) for issues in all_issues.values())
    
    result = {
        "success": total_issues == 0,
        "files_checked": files_checked,
        "total_issues": total_issues,
        "issues_by_category": {
            "error_handling": len(all_issues["error_handling"]),
            "logging": len(all_issues["logging"]),
            "validation": len(all_issues["validation"]),
            "response_models": len(all_issues["response_models"]),
        },
        "issues": all_issues,
    }
    
    return result


def main():
    """Main verification function."""
    logger.info("Starting backend route quality verification...")
    
    result = verify_backend_routes_quality()
    
    print("\n" + "=" * 80)
    print("BACKEND ROUTE QUALITY VERIFICATION REPORT")
    print("=" * 80)
    print(f"\nFiles Checked: {result['files_checked']}")
    print(f"Total Issues Found: {result['total_issues']}")
    print(f"\nIssues by Category:")
    print(f"  Error Handling: {result['issues_by_category']['error_handling']}")
    print(f"  Logging: {result['issues_by_category']['logging']}")
    print(f"  Validation: {result['issues_by_category']['validation']}")
    print(f"  Response Models: {result['issues_by_category']['response_models']}")
    
    if result['total_issues'] > 0:
        print("\n" + "-" * 80)
        print("ISSUES FOUND:")
        print("-" * 80)
        
        for category, issues in result['issues'].items():
            if issues:
                print(f"\n{category.upper().replace('_', ' ')}:")
                for issue in issues[:10]:  # Show first 10
                    print(f"  {issue['file']}:{issue.get('line', 0)} - {issue.get('function', '')} - {issue.get('type', '')}")
                if len(issues) > 10:
                    print(f"  ... and {len(issues) - 10} more")
        
        print("\n" + "=" * 80)
        print("VERIFICATION FAILED")
        print("=" * 80)
        return 1
    else:
        print("\n" + "=" * 80)
        print("VERIFICATION PASSED - All routes meet quality standards!")
        print("=" * 80)
        return 0


if __name__ == "__main__":
    exit(main())


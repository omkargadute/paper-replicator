"""Syntax verification and iterative repair for generated execution harnesses."""

import ast
import re


class HarnessRepairEngine:
    """Detects and repairs syntax errors and common API deprecations in generated code."""

    @staticmethod
    def validate_syntax(code: str) -> tuple[bool, str]:
        """Validates Python syntax using AST parsing.
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            ast.parse(code)
            return True, ""
        except SyntaxError as e:
            return False, f"SyntaxError at line {e.lineno}: {e.msg}"

    @staticmethod
    def patch_common_deprecations(code: str) -> str:
        """Applies deterministic patches for common Python / PyTorch / NumPy deprecations."""
        patched = code
        # np.float -> float
        patched = re.sub(r'\bnp\.float\b', 'float', patched)
        # np.int -> int
        patched = re.sub(r'\bnp\.int\b', 'int', patched)
        # np.bool -> bool
        patched = re.sub(r'\bnp\.bool\b', 'bool', patched)
        # torch.cuda.amp.autocast() -> torch.amp.autocast('cuda') if modern PyTorch
        return patched

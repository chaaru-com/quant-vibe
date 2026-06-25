import re
import ast

class CircuitBreakerException(Exception):
    pass

class AgentDefender:
    """
    Active Defense Blue Team circuit breaker.
    Monitors AgBOM (Agent Bill of Materials) and live drawdowns to freeze/terminate risk hazards.
    """
    def __init__(self, allowed_imports=None):
        if allowed_imports is None:
            self.allowed_imports = {'pandas', 'numpy', 'matplotlib', 'sqlite3', 'json', 'sys', 'os', 'math'}
        else:
            self.allowed_imports = set(allowed_imports)

    def verify_agbom(self, script_code):
        """
        Statically inspects imports to enforce restricted dependencies.
        """
        try:
            tree = ast.parse(script_code)
        except SyntaxError as e:
            raise CircuitBreakerException(f"Syntax error in generated code: {e}")
            
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    base_mod = alias.name.split('.')[0]
                    if base_mod not in self.allowed_imports:
                        raise CircuitBreakerException(
                            f"Stateful circuit breaker tripped: unauthorized import '{base_mod}' detected in Agent Bill of Materials (AgBOM)!"
                        )
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    base_mod = node.module.split('.')[0]
                    if base_mod not in self.allowed_imports:
                        raise CircuitBreakerException(
                            f"Stateful circuit breaker tripped: unauthorized import from '{base_mod}' detected in Agent Bill of Materials (AgBOM)!"
                        )

    def audit_code_leakage(self, script_code):
        """
        Checks if shift(1) is used when calculating target positions or indicators that dictate trade actions.
        Ensures no lookahead bias.
        """
        # A simple check: if the code computes a signal column, it must contain a shift
        if ("signal" in script_code or "position" in script_code) and "shift" not in script_code:
            raise CircuitBreakerException(
                "Security Breach (Lookahead Bias): Strategy modifies signals or positions without applying .shift() to prevent data leakage!"
            )

    def monitor_drawdown(self, equity_curve):
        """
        Verifies if strategy hits a 100% drawdown, freezing execution instantly.
        """
        if not equity_curve:
            return
        
        peak = equity_curve[0]
        for val in equity_curve:
            if val > peak:
                peak = val
            if peak > 0:
                dd = (peak - val) / peak
                if dd >= 0.9999: # 100% drawdown
                    raise CircuitBreakerException(
                        "Circuit Breaker Triggered: Strategy hit a 100% drawdown (Total Ruin). Execution frozen!"
                    )

import sympy
from typing import Dict, List, Tuple
import re

class FormulaValidator:
    """Validates and parses metric formulas"""
    
    ALLOWED_FUNCTIONS = {
        'sqrt', 'abs', 'log', 'exp', 'sin', 'cos', 'tan',
        'min', 'max', 'sum', 'avg', 'count'
    }
    
    ALLOWED_OPERATORS = {'+', '-', '*', '/', '**', '(', ')'}
    
    def __init__(self):
        self.sympy_namespace = {
            'sqrt': sympy.sqrt,
            'abs': sympy.Abs,
            'log': sympy.log,
            'exp': sympy.exp,
            'sin': sympy.sin,
            'cos': sympy.cos,
            'tan': sympy.tan,
        }
    
    def validate_formula(self, formula: str, variables: List[str]) -> Tuple[bool, str, List[str]]:
        """
        Validates a formula and returns (is_valid, error_message, extracted_variables)
        """
        try:
            # Check for empty formula
            if not formula or not formula.strip():
                return False, "Formula cannot be empty", []
            
            # Extract variables from formula
            extracted_vars = self._extract_variables(formula)
            
            # Check if all variables in formula are defined
            undefined_vars = set(extracted_vars) - set(variables)
            if undefined_vars:
                return False, f"Undefined variables: {', '.join(undefined_vars)}", extracted_vars
            
            # Check for dangerous operations
            if any(dangerous in formula.lower() for dangerous in ['import', 'exec', 'eval', '__']):
                return False, "Formula contains forbidden operations", extracted_vars
            
            # Try to parse with sympy
            symbols = {var: sympy.Symbol(var) for var in variables}
            try:
                expr = sympy.sympify(formula, locals=self.sympy_namespace)
                # Verify all symbols in expression are in our variable list
                expr_symbols = {str(s) for s in expr.free_symbols}
                if expr_symbols - set(variables):
                    return False, f"Unknown variables in formula: {expr_symbols - set(variables)}", extracted_vars
            except Exception as e:
                return False, f"Invalid formula syntax: {str(e)}", extracted_vars
            
            return True, "", extracted_vars
            
        except Exception as e:
            return False, f"Validation error: {str(e)}", []
    
    def _extract_variables(self, formula: str) -> List[str]:
        """Extract variable names from formula"""
        # Remove function names using word boundaries (avoid "cos" stripping from "cost")
        cleaned = formula
        for func in self.ALLOWED_FUNCTIONS:
            cleaned = re.sub(r'\b' + re.escape(func) + r'\b', '', cleaned)
        
        # Find all alphanumeric sequences (potential variables)
        potential_vars = re.findall(r'\b[a-zA-Z_][a-zA-Z0-9_]*\b', cleaned)
        
        # Filter out numbers and function names
        variables = [v for v in potential_vars if not v.isdigit() and v not in self.ALLOWED_FUNCTIONS]
        
        return list(set(variables))
    
    def evaluate_formula(self, formula: str, variable_values: Dict[str, float]) -> float:
        """Evaluate formula with given variable values"""
        try:
            # Create sympy symbols
            symbols = {var: sympy.Symbol(var) for var in variable_values.keys()}
            
            # Parse formula
            expr = sympy.sympify(formula, locals=self.sympy_namespace)
            
            # Substitute values
            result = expr.subs(variable_values)
            
            # Convert to float
            return float(result.evalf())
            
        except Exception as e:
            raise ValueError(f"Formula evaluation failed: {str(e)}")

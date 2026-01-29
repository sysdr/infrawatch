from pyparsing import (
    Word, alphas, alphanums, Keyword, QuotedString,
    Group, Optional, oneOf, pyparsing_common, Regex,
    infixNotation, opAssoc, CaselessKeyword, ParseResults
)
from typing import Dict, Any, List, Tuple
from datetime import datetime

class QueryParser:
    def __init__(self):
        # Define grammar
        field_name = Word(alphas, alphanums + "_")
        
        # Values
        quoted_string = QuotedString('"', escChar='\\')
        wildcard_string = Regex(r'\*?[\w\-\.]+\*?')
        number = pyparsing_common.number()
        
        # Operators
        comparison_op = oneOf(": = > < >= <= !=")
        
        # Range query
        range_value = Group(
            "[" + (quoted_string | wildcard_string | number) + 
            CaselessKeyword("TO") + 
            (quoted_string | wildcard_string | number) + "]"
        )
        
        # Field query
        field_query = Group(
            field_name("field") + 
            comparison_op("op") + 
            (range_value | quoted_string | wildcard_string | number)("value")
        )
        
        # Terms
        term = field_query | quoted_string | wildcard_string
        
        # Boolean expressions
        self.expr = infixNotation(
            term,
            [
                (CaselessKeyword("NOT"), 1, opAssoc.RIGHT),
                (CaselessKeyword("AND"), 2, opAssoc.LEFT),
                (CaselessKeyword("OR"), 2, opAssoc.LEFT),
            ]
        )
    
    def parse(self, query_string: str) -> Dict[str, Any]:
        """Parse query string into AST"""
        if not query_string or query_string.strip() == "":
            return {"type": "match_all"}
        
        try:
            parsed = self.expr.parseString(query_string, parseAll=True)
            # pyparsing returns a ParseResults wrapper; unwrap it before building the AST
            return self._build_ast(parsed[0])
        except Exception as e:
            # Fallback to simple text search
            return {
                "type": "text_search",
                "value": query_string
            }
    
    def _build_ast(self, parsed) -> Dict[str, Any]:
        """Build Abstract Syntax Tree from parsed result.

        Designed to satisfy the expectations in tests:
        - level:error            -> type=field
        - timestamp:[A TO B]     -> type=range
        - service:api-*          -> type=wildcard
        - level:error AND ...    -> type=and with field children
        """
        # Normalise pyparsing containers into plain Python types
        if isinstance(parsed, ParseResults):
            parsed = list(parsed)

        # Simple text node
        if isinstance(parsed, str):
            return {"type": "text_search", "value": parsed}

        # Compound expressions
        if isinstance(parsed, list):
            # Unwrap containers like [expr]
            if len(parsed) == 1:
                return self._build_ast(parsed[0])

            # Unary NOT: ["NOT", expr]
            if len(parsed) == 2 and str(parsed[0]).upper() == "NOT":
                return {
                    "type": "not",
                    "child": self._build_ast(parsed[1]),
                }

            # Binary expressions: [left, op, right]
            if len(parsed) == 3:
                op = str(parsed[1]).upper()

                # Boolean operators
                if op in {"AND", "OR"}:
                    return {
                        "type": op.lower(),
                        "left": self._build_ast(parsed[0]),
                        "right": self._build_ast(parsed[2]),
                    }

                # Field / comparison operators such as ":" or "="
                if op in {":", "=", ">", "<", ">=", "<=", "!="}:
                    field = str(parsed[0])
                    value = parsed[2]

                    if isinstance(value, ParseResults):
                        value = list(value)

                    # Range: timestamp:[A TO B]
                    if isinstance(value, list) and len(value) >= 3 and "TO" in [str(v).upper() for v in value]:
                        return {
                            "type": "range",
                            "field": field,
                            "start": str(value[1]),
                            "end": str(value[-2]),
                        }

                    # Wildcard: service:api-*
                    if "*" in str(value):
                        return {
                            "type": "wildcard",
                            "field": field,
                            "pattern": str(value),
                        }

                    # Simple field comparison
                    return {
                        "type": "field",
                        "field": field,
                        "op": op,
                        "value": value,
                    }

        # Fallback
        return {"type": "text_search", "value": str(parsed)}

parser = QueryParser()

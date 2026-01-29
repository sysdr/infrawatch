from typing import Dict, Any, Tuple, List
from sqlalchemy import and_, or_, not_, text
from sqlalchemy.sql import Select
from app.models.log import Log

class SQLTranslator:
    def translate(self, ast: Dict[str, Any], query: Select) -> Tuple[Select, List[Any]]:
        """Translate AST to SQLAlchemy query"""
        params = []
        
        if ast["type"] == "match_all":
            return query, params
        
        condition, params = self._translate_node(ast)
        if condition is not None:
            query = query.where(condition)
        
        return query, params
    
    def _translate_node(self, node: Dict[str, Any]) -> Tuple[Any, List[Any]]:
        """Translate single AST node to SQL condition"""
        node_type = node["type"]
        
        if node_type == "field":
            return self._translate_field(node)
        
        elif node_type == "range":
            return self._translate_range(node)
        
        elif node_type == "wildcard":
            return self._translate_wildcard(node)
        
        elif node_type == "text_search":
            return self._translate_text_search(node)
        
        elif node_type == "and":
            left_cond, left_params = self._translate_node(node["left"])
            right_cond, right_params = self._translate_node(node["right"])
            return and_(left_cond, right_cond), left_params + right_params
        
        elif node_type == "or":
            left_cond, left_params = self._translate_node(node["left"])
            right_cond, right_params = self._translate_node(node["right"])
            return or_(left_cond, right_cond), left_params + right_params
        
        elif node_type == "not":
            child_cond, child_params = self._translate_node(node["child"])
            return not_(child_cond), child_params
        
        return None, []
    
    def _translate_field(self, node: Dict[str, Any]) -> Tuple[Any, List[Any]]:
        """Translate field query"""
        field = node["field"]
        op = node["op"]
        value = node["value"]
        
        column = getattr(Log, field, None)
        if column is None:
            return None, []
        
        if op in [":", "="]:
            return column == value, [value]
        elif op == ">":
            return column > value, [value]
        elif op == "<":
            return column < value, [value]
        elif op == ">=":
            return column >= value, [value]
        elif op == "<=":
            return column <= value, [value]
        elif op == "!=":
            return column != value, [value]
        
        return None, []
    
    def _translate_range(self, node: Dict[str, Any]) -> Tuple[Any, List[Any]]:
        """Translate range query"""
        field = node["field"]
        start = node["start"]
        end = node["end"]
        
        column = getattr(Log, field, None)
        if column is None:
            return None, []
        
        return and_(column >= start, column <= end), [start, end]
    
    def _translate_wildcard(self, node: Dict[str, Any]) -> Tuple[Any, List[Any]]:
        """Translate wildcard query using trigram index"""
        field = node["field"]
        pattern = node["pattern"].replace('*', '%')
        
        column = getattr(Log, field, None)
        if column is None:
            return None, []
        
        return column.like(pattern), [pattern]
    
    def _translate_text_search(self, node: Dict[str, Any]) -> Tuple[Any, List[Any]]:
        """Translate full-text search"""
        value = node["value"]
        
        # Use PostgreSQL full-text search
        condition = text(
            "search_vector @@ plainto_tsquery('english', :search_term)"
        ).bindparams(search_term=value)
        
        return condition, [value]

sql_translator = SQLTranslator()

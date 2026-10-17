"""查询DSL解析器"""
try:
    from .parser import Parser
    from .validator import Validator, DEFAULT_OPERATORS
    from .nodes import (
        FilterNode, CompareNode, AndNode, OrNode, NotNode, ASTNode
    )
    from .exceptions import (
        QueryDSLError, ParseError, ValidationError,
        UnsupportedOperatorError, InvalidFieldError
    )
except ImportError:
    from parser import Parser
    from validator import Validator, DEFAULT_OPERATORS
    from nodes import (
        FilterNode, CompareNode, AndNode, OrNode, NotNode, ASTNode
    )
    from exceptions import (
        QueryDSLError, ParseError, ValidationError,
        UnsupportedOperatorError, InvalidFieldError
    )

__version__ = '1.0.0'

__all__ = [
    'Parser',
    'Validator',
    'DEFAULT_OPERATORS',
    'FilterNode',
    'CompareNode',
    'AndNode',
    'OrNode',
    'NotNode',
    'ASTNode',
    'QueryDSLError',
    'ParseError',
    'ValidationError',
    'UnsupportedOperatorError',
    'InvalidFieldError',
]

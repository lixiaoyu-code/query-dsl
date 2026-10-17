"""查询DSL异常定义"""


class QueryDSLError(Exception):
    """DSL基础异常"""
    pass


class ParseError(QueryDSLError):
    """解析错误"""
    pass


class ValidationError(QueryDSLError):
    """验证错误"""
    pass


class UnsupportedOperatorError(ValidationError):
    """不支持的操作符"""
    pass


class InvalidFieldError(ValidationError):
    """非法字段"""
    pass

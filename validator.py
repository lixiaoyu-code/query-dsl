"""验证器和扩展机制"""
from typing import Set, Optional, Callable, Dict, Any
from exceptions import UnsupportedOperatorError, InvalidFieldError


# 默认支持的操作符
DEFAULT_OPERATORS = {
    'eq', 'ne', 'gt', 'gte', 'lt', 'lte',
    'in', 'not_in', 'like', 'ilike',
    'is_null', 'not_null', 'between'
}


class Validator:
    """验证器：支持字段和操作符校验"""
    __slots__ = ('_allowed_fields', '_operators', '_field_validators')

    def __init__(
        self,
        allowed_fields: Optional[Set[str]] = None,
        operators: Optional[Set[str]] = None
    ):
        """
        Args:
            allowed_fields: 允许的字段白名单，None表示不限制
            operators: 支持的操作符集合，默认使用DEFAULT_OPERATORS
        """
        self._allowed_fields = allowed_fields
        self._operators = operators or DEFAULT_OPERATORS.copy()
        self._field_validators: Dict[str, Callable[[Any], bool]] = {}

    def validate_field(self, field: str) -> None:
        """验证字段是否合法"""
        if self._allowed_fields is not None and field not in self._allowed_fields:
            raise InvalidFieldError(f"Field '{field}' is not allowed")

    def validate_operator(self, op: str) -> None:
        """验证操作符是否支持"""
        if op not in self._operators:
            raise UnsupportedOperatorError(
                f"Operator '{op}' not supported. Available: {sorted(self._operators)}"
            )

    def validate_value(self, field: str, value: Any) -> None:
        """验证字段值（可扩展）"""
        if field in self._field_validators:
            validator = self._field_validators[field]
            if not validator(value):
                raise ValueError(f"Invalid value for field '{field}': {value}")

    def register_operator(self, op: str) -> None:
        """注册自定义操作符"""
        self._operators.add(op)

    def register_field_validator(self, field: str, validator: Callable[[Any], bool]) -> None:
        """注册字段值验证器"""
        self._field_validators[field] = validator

    @property
    def operators(self) -> Set[str]:
        """获取所有支持的操作符"""
        return self._operators.copy()

"""验证器和扩展机制"""
from typing import Set, Optional, Callable, Dict, Any
from exceptions import UnsupportedOperatorError, InvalidFieldError
from operators import OperatorRegistry


class Validator:
    """验证器：支持字段和操作符校验"""
    __slots__ = ('_allowed_fields', '_field_validators')

    def __init__(
        self,
        allowed_fields: Optional[Set[str]] = None,
        operators: Optional[Set[str]] = None  # 保留兼容性，但不再使用
    ):
        """
        Args:
            allowed_fields: 允许的字段白名单，None表示不限制
            operators: 已废弃，操作符通过 OperatorRegistry 自动管理
        """
        self._allowed_fields = allowed_fields
        self._field_validators: Dict[str, Callable[[Any], bool]] = {}

    def validate_field(self, field: str) -> None:
        """验证字段是否合法"""
        if self._allowed_fields is not None and field not in self._allowed_fields:
            raise InvalidFieldError(f"Field '{field}' is not allowed")

    def validate_operator(self, op: str) -> None:
        """验证操作符是否支持"""
        if not OperatorRegistry.get(op):
            available = sorted(OperatorRegistry.all_names())
            raise UnsupportedOperatorError(
                f"Operator '{op}' not supported. Available: {available}"
            )

    def validate_operator_value(self, op: str, value: Any) -> None:
        """
        验证操作符的值是否符合要求

        Args:
            op: 操作符名称
            value: 待验证的值

        Raises:
            ValidationError: 值不符合操作符要求
        """
        OperatorRegistry.validate(op, value)

    def validate_value(self, field: str, value: Any) -> None:
        """验证字段值（可扩展）"""
        if field in self._field_validators:
            validator = self._field_validators[field]
            if not validator(value):
                raise ValueError(f"Invalid value for field '{field}': {value}")

    def register_operator(self, op: str) -> None:
        """
        已废弃：操作符通过 operators/ 目录自动注册
        保留此方法仅为向后兼容
        """
        pass

    def register_field_validator(self, field: str, validator: Callable[[Any], bool]) -> None:
        """注册字段值验证器"""
        self._field_validators[field] = validator

    @property
    def operators(self) -> Set[str]:
        """获取所有支持的操作符"""
        return OperatorRegistry.all_names()

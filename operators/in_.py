"""in 操作符：包含于"""
from typing import Any
from .base import Operator
from exceptions import ValidationError


class InOperator(Operator):
    """包含于操作符：field IN (value1, value2, ...)"""
    name = "in"

    @classmethod
    def validate(cls, value: Any) -> None:
        """
        in 操作符要求值必须是非空列表

        Raises:
            ValidationError: 值格式不正确
        """
        if not isinstance(value, list):
            raise ValidationError(
                f"Operator 'in' requires a list value, "
                f"got {type(value).__name__}"
            )

        if len(value) == 0:
            raise ValidationError(
                f"Operator 'in' requires a non-empty list, "
                f"got empty list"
            )

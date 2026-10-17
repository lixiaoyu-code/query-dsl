"""notIn 操作符：不包含于"""
from typing import Any
from .base import Operator
from exceptions import ValidationError


class NotInOperator(Operator):
    """不包含于操作符：field NOT IN (value1, value2, ...)"""
    name = "notIn"

    @classmethod
    def validate(cls, value: Any) -> None:
        """
        notIn 操作符要求值必须是非空列表

        Raises:
            ValidationError: 值格式不正确
        """
        if not isinstance(value, list):
            raise ValidationError(
                f"Operator 'notIn' requires a list value, "
                f"got {type(value).__name__}"
            )

        if len(value) == 0:
            raise ValidationError(
                f"Operator 'notIn' requires a non-empty list, "
                f"got empty list"
            )

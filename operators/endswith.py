"""endswith 操作符：后缀匹配"""
from typing import Any
from .base import Operator
from exceptions import ValidationError


class EndsWithOperator(Operator):
    """后缀匹配操作符：field LIKE '%suffix'"""
    name = "endswith"

    @classmethod
    def validate(cls, value: Any) -> None:
        """
        endswith 操作符要求值必须是字符串

        Raises:
            ValidationError: 值不是字符串
        """
        if not isinstance(value, str):
            raise ValidationError(
                f"Operator 'endswith' requires a string value, "
                f"got {type(value).__name__}"
            )

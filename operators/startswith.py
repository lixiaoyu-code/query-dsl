"""startswith 操作符：前缀匹配"""
from typing import Any
from .base import Operator
from exceptions import ValidationError


class StartsWithOperator(Operator):
    """前缀匹配操作符：field LIKE 'prefix%'"""
    name = "startswith"

    @classmethod
    def validate(cls, value: Any) -> None:
        """
        startswith 操作符要求值必须是字符串

        Raises:
            ValidationError: 值不是字符串
        """
        if not isinstance(value, str):
            raise ValidationError(
                f"Operator 'startswith' requires a string value, "
                f"got {type(value).__name__}"
            )

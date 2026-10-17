"""between 操作符：范围查询"""
from typing import Any
from .base import Operator
from exceptions import ValidationError


class BetweenOperator(Operator):
    """范围操作符：field BETWEEN min AND max"""
    name = "between"

    @classmethod
    def validate(cls, value: Any) -> None:
        """
        between 操作符要求值必须是长度为 2 的列表 [min, max]

        Raises:
            ValidationError: 值格式不正确
        """
        if not isinstance(value, list):
            raise ValidationError(
                f"Operator 'between' requires a list value [min, max], "
                f"got {type(value).__name__}"
            )

        if len(value) != 2:
            raise ValidationError(
                f"Operator 'between' requires exactly 2 elements [min, max], "
                f"got {len(value)} elements"
            )

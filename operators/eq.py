"""eq 操作符：等于"""
from typing import Any
from .base import Operator


class EqOperator(Operator):
    """等于操作符：field == value"""
    name = "eq"

    @classmethod
    def validate(cls, value: Any) -> None:
        """eq 操作符接受任意值，无需校验"""
        pass

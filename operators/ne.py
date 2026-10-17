"""ne 操作符：不等于"""
from typing import Any
from .base import Operator


class NeOperator(Operator):
    """不等于操作符：field != value"""
    name = "ne"

    @classmethod
    def validate(cls, value: Any) -> None:
        """ne 操作符接受任意值，无需校验"""
        pass

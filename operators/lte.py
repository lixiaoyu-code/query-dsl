"""lte 操作符：小于等于"""
from typing import Any
from .base import Operator


class LteOperator(Operator):
    """小于等于操作符：field <= value"""
    name = "lte"

    @classmethod
    def validate(cls, value: Any) -> None:
        """lte 操作符接受任意可比较值，无需校验"""
        pass

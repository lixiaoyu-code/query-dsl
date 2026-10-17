"""lt 操作符：小于"""
from typing import Any
from .base import Operator


class LtOperator(Operator):
    """小于操作符：field < value"""
    name = "lt"

    @classmethod
    def validate(cls, value: Any) -> None:
        """lt 操作符接受任意可比较值，无需校验"""
        pass

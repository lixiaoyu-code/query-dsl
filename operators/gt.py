"""gt 操作符：大于"""
from typing import Any
from .base import Operator


class GtOperator(Operator):
    """大于操作符：field > value"""
    name = "gt"

    @classmethod
    def validate(cls, value: Any) -> None:
        """gt 操作符接受任意可比较值，无需校验"""
        pass

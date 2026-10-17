"""gte 操作符：大于等于"""
from typing import Any
from .base import Operator


class GteOperator(Operator):
    """大于等于操作符：field >= value"""
    name = "gte"

    @classmethod
    def validate(cls, value: Any) -> None:
        """gte 操作符接受任意可比较值，无需校验"""
        pass

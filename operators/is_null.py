"""isNull 操作符：为空判断"""
from typing import Any
from .base import Operator


class IsNullOperator(Operator):
    """为空操作符：field IS NULL"""
    name = "isNull"

    @classmethod
    def validate(cls, value: Any) -> None:
        """
        isNull 操作符不需要 value 参数，任意值都接受
        实际使用时可以忽略 value 或将其设为 None
        """
        pass

"""isNotNull 操作符：不为空判断"""
from typing import Any
from .base import Operator


class IsNotNullOperator(Operator):
    """不为空操作符：field IS NOT NULL"""
    name = "isNotNull"

    @classmethod
    def validate(cls, value: Any) -> None:
        """
        isNotNull 操作符不需要 value 参数，任意值都接受
        实际使用时可以忽略 value 或将其设为 None
        """
        pass

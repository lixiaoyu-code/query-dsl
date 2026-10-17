"""操作符基类和注册器"""
from abc import ABC, abstractmethod
from typing import Any, Dict, Type, Optional


class Operator(ABC):
    """操作符基类"""
    name: str = ""  # 操作符名称，子类必须设置

    @classmethod
    @abstractmethod
    def validate(cls, value: Any) -> None:
        """
        校验值是否符合操作符要求（类方法，无需实例化）

        Args:
            value: 待校验的值

        Raises:
            ValidationError: 校验失败时抛出，异常信息由子类描述
        """
        pass

    def __init_subclass__(cls, **kwargs):
        """子类定义时自动注册"""
        super().__init_subclass__(**kwargs)
        if cls.name:  # 只注册设置了 name 的子类
            OperatorRegistry.register(cls)


class OperatorRegistry:
    """操作符注册器"""
    _operators: Dict[str, Type[Operator]] = {}

    @classmethod
    def register(cls, operator_class: Type[Operator]) -> None:
        """注册操作符类"""
        if not operator_class.name:
            raise ValueError(f"Operator class {operator_class.__name__} must define 'name'")
        cls._operators[operator_class.name] = operator_class

    @classmethod
    def get(cls, name: str) -> Optional[Type[Operator]]:
        """根据名称获取操作符类"""
        return cls._operators.get(name)

    @classmethod
    def all_names(cls) -> set:
        """获取所有已注册的操作符名称"""
        return set(cls._operators.keys())

    @classmethod
    def validate(cls, op_name: str, value: Any) -> None:
        """
        校验操作符的值（优化：直接调用类方法，无需实例化）

        Args:
            op_name: 操作符名称
            value: 待校验的值

        Raises:
            ValidationError: 校验失败
        """
        operator_class = cls.get(op_name)
        if operator_class:
            operator_class.validate(value)  # 直接调用类方法

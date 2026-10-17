"""AST节点定义"""
from dataclasses import dataclass
from typing import Any, List, Union
from abc import ABC, abstractmethod


class FilterNode(ABC):
    """过滤节点基类"""
    __slots__ = ()

    @abstractmethod
    def accept(self, visitor):
        """访问者模式接口"""
        pass


@dataclass(slots=True)
class CompareNode(FilterNode):
    """比较节点：字段操作"""
    field: str
    op: str
    value: Any

    def accept(self, visitor):
        return visitor.visit_compare(self)

    def __repr__(self):
        return f"CompareNode(field={self.field!r}, op={self.op!r}, value={self.value!r})"


@dataclass(slots=True)
class AndNode(FilterNode):
    """AND逻辑节点"""
    children: List[FilterNode]

    def accept(self, visitor):
        return visitor.visit_and(self)

    def __repr__(self):
        return f"AndNode({len(self.children)} children)"


@dataclass(slots=True)
class OrNode(FilterNode):
    """OR逻辑节点"""
    children: List[FilterNode]

    def accept(self, visitor):
        return visitor.visit_or(self)

    def __repr__(self):
        return f"OrNode({len(self.children)} children)"


@dataclass(slots=True)
class NotNode(FilterNode):
    """NOT逻辑节点"""
    child: FilterNode

    def accept(self, visitor):
        return visitor.visit_not(self)

    def __repr__(self):
        return f"NotNode(child={self.child!r})"


# 类型别名
ASTNode = Union[CompareNode, AndNode, OrNode, NotNode]

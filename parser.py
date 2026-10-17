"""查询DSL解析器"""
from typing import Dict, Any, Optional
from nodes import CompareNode, AndNode, OrNode, NotNode, FilterNode
from validator import Validator
from exceptions import ParseError


class Parser:
    """DSL解析器：JSON -> AST"""
    __slots__ = ('_validator',)

    def __init__(self, validator: Optional[Validator] = None):
        """
        Args:
            validator: 验证器实例，None表示使用默认验证器
        """
        self._validator = validator or Validator()

    def parse(self, data: Dict[str, Any]) -> FilterNode:
        """
        解析查询DSL

        Args:
            data: 包含'filter'键的字典

        Returns:
            AST根节点

        Raises:
            ParseError: 解析失败
        """
        if not isinstance(data, dict):
            raise ParseError(f"Expected dict, got {type(data).__name__}")

        if 'filter' not in data:
            raise ParseError("Missing 'filter' key in query")

        filter_data = data['filter']

        # 简化语法：如果filter是数组，自动包装为and
        if isinstance(filter_data, list):
            if len(filter_data) == 0:
                raise ParseError("'filter' array cannot be empty")
            filter_data = {'and': filter_data}

        return self._parse_node(filter_data)

    def _parse_node(self, node: Any) -> FilterNode:
        """递归解析节点"""
        if not isinstance(node, dict):
            raise ParseError(f"Node must be dict, got {type(node).__name__}")

        # 逻辑操作符
        if 'and' in node:
            return self._parse_and(node['and'])
        elif 'or' in node:
            return self._parse_or(node['or'])
        elif 'not' in node:
            return self._parse_not(node['not'])
        # 比较操作
        elif 'field' in node:
            return self._parse_compare(node)
        else:
            raise ParseError(f"Unknown node structure: {list(node.keys())}")

    def _parse_and(self, children: Any) -> AndNode:
        """解析AND节点"""
        if not isinstance(children, list):
            raise ParseError(f"'and' requires list, got {type(children).__name__}")

        if len(children) == 0:
            raise ParseError("'and' requires at least one child")

        parsed_children = [self._parse_node(child) for child in children]
        return AndNode(children=parsed_children)

    def _parse_or(self, children: Any) -> OrNode:
        """解析OR节点"""
        if not isinstance(children, list):
            raise ParseError(f"'or' requires list, got {type(children).__name__}")

        if len(children) == 0:
            raise ParseError("'or' requires at least one child")

        parsed_children = [self._parse_node(child) for child in children]
        return OrNode(children=parsed_children)

    def _parse_not(self, child: Any) -> NotNode:
        """解析NOT节点"""
        parsed_child = self._parse_node(child)
        return NotNode(child=parsed_child)

    def _parse_compare(self, node: Dict[str, Any]) -> CompareNode:
        """解析比较节点"""
        # 提取字段
        field = node.get('field')
        if not isinstance(field, str):
            raise ParseError(f"'field' must be string, got {type(field).__name__}")

        # 提取操作符
        op = node.get('op')
        if not isinstance(op, str):
            raise ParseError(f"'op' must be string, got {type(op).__name__}")

        # 提取值
        if 'value' not in node:
            raise ParseError(f"Missing 'value' in compare node")
        value = node['value']

        # 验证
        self._validator.validate_field(field)
        self._validator.validate_operator(op)
        self._validator.validate_value(field, value)

        return CompareNode(field=field, op=op, value=value)

    @property
    def validator(self) -> Validator:
        """获取验证器"""
        return self._validator

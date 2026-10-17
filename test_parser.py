"""查询DSL解析器测试"""
import pytest
import time
import json
from parser import Parser
from validator import Validator
from nodes import CompareNode, AndNode, OrNode, NotNode
from exceptions import (
    ParseError, ValidationError, UnsupportedOperatorError, InvalidFieldError
)


class TestBasicParsing:
    """基础解析测试"""

    def test_simple_compare(self):
        """测试简单比较"""
        parser = Parser()
        query = {
            "filter": {
                "field": "age",
                "op": "gt",
                "value": 18
            }
        }
        ast = parser.parse(query)
        assert isinstance(ast, CompareNode)
        assert ast.field == "age"
        assert ast.op == "gt"
        assert ast.value == 18

    def test_and_logic(self):
        """测试AND逻辑"""
        parser = Parser()
        query = {
            "filter": {
                "and": [
                    {"field": "age", "op": "gt", "value": 18},
                    {"field": "name", "op": "eq", "value": "tom"}
                ]
            }
        }
        ast = parser.parse(query)
        assert isinstance(ast, AndNode)
        assert len(ast.children) == 2
        assert isinstance(ast.children[0], CompareNode)
        assert isinstance(ast.children[1], CompareNode)

    def test_or_logic(self):
        """测试OR逻辑"""
        parser = Parser()
        query = {
            "filter": {
                "or": [
                    {"field": "status", "op": "eq", "value": "active"},
                    {"field": "status", "op": "eq", "value": "pending"}
                ]
            }
        }
        ast = parser.parse(query)
        assert isinstance(ast, OrNode)
        assert len(ast.children) == 2

    def test_not_logic(self):
        """测试NOT逻辑"""
        parser = Parser()
        query = {
            "filter": {
                "not": {
                    "field": "deleted",
                    "op": "eq",
                    "value": True
                }
            }
        }
        ast = parser.parse(query)
        assert isinstance(ast, NotNode)
        assert isinstance(ast.child, CompareNode)

    def test_nested_logic(self):
        """测试嵌套逻辑（用户提供的样例）"""
        parser = Parser()
        query = {
            "filter": {
                "or": [
                    {
                        "not": {
                            "and": [
                                {"field": "age", "op": "gt", "value": 18},
                                {"field": "name", "op": "eq", "value": "tom"}
                            ]
                        }
                    },
                    {
                        "field": "status",
                        "op": "in",
                        "value": ["VIP"]
                    }
                ]
            }
        }
        ast = parser.parse(query)
        assert isinstance(ast, OrNode)
        assert len(ast.children) == 2
        assert isinstance(ast.children[0], NotNode)
        assert isinstance(ast.children[0].child, AndNode)
        assert isinstance(ast.children[1], CompareNode)

    def test_array_filter_shorthand(self):
        """测试数组简化语法（自动转为AND）"""
        parser = Parser()
        query = {
            "filter": [
                {"field": "status", "op": "eq", "value": "ACTIVE"},
                {"field": "name", "op": "like", "value": "alice"},
                {"field": "priority", "op": "gte", "value": 8}
            ]
        }
        ast = parser.parse(query)
        assert isinstance(ast, AndNode)
        assert len(ast.children) == 3
        assert ast.children[0].field == "status"
        assert ast.children[0].value == "ACTIVE"
        assert ast.children[1].field == "name"
        assert ast.children[1].op == "like"
        assert ast.children[2].field == "priority"
        assert ast.children[2].op == "gte"

    def test_single_item_array_filter(self):
        """测试单个条件的数组"""
        parser = Parser()
        query = {
            "filter": [
                {"field": "age", "op": "gt", "value": 18}
            ]
        }
        ast = parser.parse(query)
        assert isinstance(ast, AndNode)
        assert len(ast.children) == 1
        assert isinstance(ast.children[0], CompareNode)


class TestValidation:
    """验证测试"""

    def test_field_whitelist(self):
        """测试字段白名单"""
        validator = Validator(allowed_fields={"age", "name"})
        parser = Parser(validator)

        # 合法字段
        query = {"filter": {"field": "age", "op": "gt", "value": 18}}
        ast = parser.parse(query)
        assert isinstance(ast, CompareNode)

        # 非法字段
        query = {"filter": {"field": "email", "op": "eq", "value": "test@example.com"}}
        with pytest.raises(InvalidFieldError) as exc:
            parser.parse(query)
        assert "email" in str(exc.value)

    def test_operator_validation(self):
        """测试操作符验证"""
        validator = Validator(operators={"eq", "gt", "lt"})
        parser = Parser(validator)

        # 合法操作符
        query = {"filter": {"field": "age", "op": "gt", "value": 18}}
        ast = parser.parse(query)
        assert isinstance(ast, CompareNode)

        # 非法操作符
        query = {"filter": {"field": "age", "op": "between", "value": [1, 10]}}
        with pytest.raises(UnsupportedOperatorError) as exc:
            parser.parse(query)
        assert "between" in str(exc.value)

    def test_custom_operator(self):
        """测试自定义操作符"""
        validator = Validator()
        validator.register_operator("regex")
        parser = Parser(validator)

        query = {"filter": {"field": "name", "op": "regex", "value": "^test.*"}}
        ast = parser.parse(query)
        assert isinstance(ast, CompareNode)
        assert ast.op == "regex"

    def test_field_value_validator(self):
        """测试字段值验证器"""
        validator = Validator()
        # 年龄必须在0-150之间
        validator.register_field_validator("age", lambda v: 0 <= v <= 150)
        parser = Parser(validator)

        # 合法值
        query = {"filter": {"field": "age", "op": "gt", "value": 18}}
        ast = parser.parse(query)
        assert isinstance(ast, CompareNode)

        # 非法值
        query = {"filter": {"field": "age", "op": "gt", "value": 200}}
        with pytest.raises(ValueError) as exc:
            parser.parse(query)
        assert "age" in str(exc.value)


class TestErrorHandling:
    """异常处理测试"""

    def test_missing_filter_key(self):
        """测试缺少filter键"""
        parser = Parser()
        with pytest.raises(ParseError) as exc:
            parser.parse({"query": {}})
        assert "filter" in str(exc.value)

    def test_invalid_input_type(self):
        """测试非法输入类型"""
        parser = Parser()
        with pytest.raises(ParseError):
            parser.parse("invalid")
        with pytest.raises(ParseError):
            parser.parse(["invalid"])

    def test_empty_and(self):
        """测试空AND"""
        parser = Parser()
        query = {"filter": {"and": []}}
        with pytest.raises(ParseError) as exc:
            parser.parse(query)
        assert "at least one" in str(exc.value)

    def test_empty_or(self):
        """测试空OR"""
        parser = Parser()
        query = {"filter": {"or": []}}
        with pytest.raises(ParseError) as exc:
            parser.parse(query)
        assert "at least one" in str(exc.value)

    def test_empty_array_filter(self):
        """测试空数组filter"""
        parser = Parser()
        query = {"filter": []}
        with pytest.raises(ParseError) as exc:
            parser.parse(query)
        assert "empty" in str(exc.value)

    def test_missing_field(self):
        """测试缺少field"""
        parser = Parser()
        query = {"filter": {"op": "eq", "value": 10}}
        with pytest.raises(ParseError) as exc:
            parser.parse(query)
        assert "Unknown" in str(exc.value) or "field" in str(exc.value)

    def test_missing_op(self):
        """测试缺少op"""
        parser = Parser()
        query = {"filter": {"field": "age", "value": 10}}
        with pytest.raises(ParseError):
            parser.parse(query)

    def test_missing_value(self):
        """测试缺少value"""
        parser = Parser()
        query = {"filter": {"field": "age", "op": "eq"}}
        with pytest.raises(ParseError) as exc:
            parser.parse(query)
        assert "value" in str(exc.value)

    def test_invalid_field_type(self):
        """测试非法字段类型"""
        parser = Parser()
        query = {"filter": {"field": 123, "op": "eq", "value": 10}}
        with pytest.raises(ParseError) as exc:
            parser.parse(query)
        assert "string" in str(exc.value)

    def test_invalid_and_type(self):
        """测试非法AND类型"""
        parser = Parser()
        query = {"filter": {"and": "invalid"}}
        with pytest.raises(ParseError) as exc:
            parser.parse(query)
        assert "list" in str(exc.value)


class TestPerformance:
    """性能测试"""

    def test_simple_parse_performance(self):
        """测试简单解析性能"""
        parser = Parser()
        query = {
            "filter": {
                "field": "age",
                "op": "gt",
                "value": 18
            }
        }

        iterations = 10000
        start = time.perf_counter()
        for _ in range(iterations):
            parser.parse(query)
        elapsed = time.perf_counter() - start

        per_op = elapsed / iterations * 1000000  # 微秒
        print(f"\n简单解析: {iterations}次耗时{elapsed:.3f}秒, 平均{per_op:.2f}μs/次")
        assert per_op < 100, f"性能不达标: {per_op:.2f}μs > 100μs"

    def test_complex_parse_performance(self):
        """测试复杂嵌套解析性能"""
        parser = Parser()
        query = {
            "filter": {
                "or": [
                    {
                        "not": {
                            "and": [
                                {"field": "age", "op": "gt", "value": 18},
                                {"field": "name", "op": "eq", "value": "tom"}
                            ]
                        }
                    },
                    {
                        "field": "status",
                        "op": "in",
                        "value": ["VIP"]
                    }
                ]
            }
        }

        iterations = 5000
        start = time.perf_counter()
        for _ in range(iterations):
            parser.parse(query)
        elapsed = time.perf_counter() - start

        per_op = elapsed / iterations * 1000000  # 微秒
        print(f"\n复杂解析: {iterations}次耗时{elapsed:.3f}秒, 平均{per_op:.2f}μs/次")
        assert per_op < 500, f"性能不达标: {per_op:.2f}μs > 500μs"

    def test_deep_nesting_performance(self):
        """测试深层嵌套性能"""
        parser = Parser()

        # 构建10层嵌套
        query = {"field": "age", "op": "eq", "value": 1}
        for i in range(10):
            query = {"and": [query, {"field": f"field{i}", "op": "eq", "value": i}]}

        query = {"filter": query}

        iterations = 1000
        start = time.perf_counter()
        for _ in range(iterations):
            parser.parse(query)
        elapsed = time.perf_counter() - start

        per_op = elapsed / iterations * 1000000  # 微秒
        print(f"\n深层嵌套: {iterations}次耗时{elapsed:.3f}秒, 平均{per_op:.2f}μs/次")
        assert per_op < 1000, f"性能不达标: {per_op:.2f}μs > 1000μs"

    def test_wide_or_performance(self):
        """测试宽OR性能（100个条件）"""
        parser = Parser()
        conditions = [
            {"field": f"field{i}", "op": "eq", "value": i}
            for i in range(100)
        ]
        query = {"filter": {"or": conditions}}

        iterations = 500
        start = time.perf_counter()
        for _ in range(iterations):
            parser.parse(query)
        elapsed = time.perf_counter() - start

        per_op = elapsed / iterations * 1000  # 毫秒
        print(f"\n宽OR(100条件): {iterations}次耗时{elapsed:.3f}秒, 平均{per_op:.2f}ms/次")
        assert per_op < 10, f"性能不达标: {per_op:.2f}ms > 10ms"


class TestEdgeCases:
    """边界情况测试"""

    def test_value_types(self):
        """测试各种值类型"""
        parser = Parser()

        # 整数
        query = {"filter": {"field": "age", "op": "eq", "value": 18}}
        ast = parser.parse(query)
        assert ast.value == 18

        # 字符串
        query = {"filter": {"field": "name", "op": "eq", "value": "tom"}}
        ast = parser.parse(query)
        assert ast.value == "tom"

        # 布尔
        query = {"filter": {"field": "active", "op": "eq", "value": True}}
        ast = parser.parse(query)
        assert ast.value is True

        # None
        query = {"filter": {"field": "deleted_at", "op": "is_null", "value": None}}
        ast = parser.parse(query)
        assert ast.value is None

        # 列表
        query = {"filter": {"field": "status", "op": "in", "value": ["a", "b", "c"]}}
        ast = parser.parse(query)
        assert ast.value == ["a", "b", "c"]

        # 字典
        query = {"filter": {"field": "meta", "op": "eq", "value": {"key": "val"}}}
        ast = parser.parse(query)
        assert ast.value == {"key": "val"}

    def test_unicode_support(self):
        """测试Unicode支持"""
        parser = Parser()
        query = {"filter": {"field": "名字", "op": "eq", "value": "测试"}}
        ast = parser.parse(query)
        assert ast.field == "名字"
        assert ast.value == "测试"

    def test_special_characters(self):
        """测试特殊字符"""
        parser = Parser()
        query = {
            "filter": {
                "field": "email",
                "op": "like",
                "value": "%@example.com"
            }
        }
        ast = parser.parse(query)
        assert ast.value == "%@example.com"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])

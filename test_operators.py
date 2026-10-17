"""测试新的操作符系统"""
import pytest
from parser import Parser
from exceptions import ValidationError, UnsupportedOperatorError


class TestOperatorSystem:
    """测试操作符系统"""

    def test_operator_auto_registration(self):
        """测试操作符自动注册"""
        from operators import OperatorRegistry

        registered_ops = OperatorRegistry.all_names()
        expected_ops = {
            'eq', 'ne', 'gt', 'gte', 'lt', 'lte',
            'between', 'in', 'notIn',
            'isNull', 'isNotNull',
            'startswith', 'endswith'
        }

        assert expected_ops.issubset(registered_ops), \
            f"Missing operators: {expected_ops - registered_ops}"

    def test_eq_operator(self):
        """测试 eq 操作符"""
        parser = Parser()
        query = {"filter": {"field": "age", "op": "eq", "value": 18}}
        ast = parser.parse(query)
        assert ast.op == "eq"
        assert ast.value == 18

    def test_ne_operator(self):
        """测试 ne 操作符"""
        parser = Parser()
        query = {"filter": {"field": "status", "op": "ne", "value": "deleted"}}
        ast = parser.parse(query)
        assert ast.op == "ne"

    def test_gt_operator(self):
        """测试 gt 操作符"""
        parser = Parser()
        query = {"filter": {"field": "age", "op": "gt", "value": 18}}
        ast = parser.parse(query)
        assert ast.op == "gt"

    def test_gte_operator(self):
        """测试 gte 操作符"""
        parser = Parser()
        query = {"filter": {"field": "score", "op": "gte", "value": 60}}
        ast = parser.parse(query)
        assert ast.op == "gte"

    def test_lt_operator(self):
        """测试 lt 操作符"""
        parser = Parser()
        query = {"filter": {"field": "age", "op": "lt", "value": 65}}
        ast = parser.parse(query)
        assert ast.op == "lt"

    def test_lte_operator(self):
        """测试 lte 操作符"""
        parser = Parser()
        query = {"filter": {"field": "price", "op": "lte", "value": 100}}
        ast = parser.parse(query)
        assert ast.op == "lte"


class TestBetweenOperator:
    """测试 between 操作符"""

    def test_between_valid(self):
        """测试 between 正确格式"""
        parser = Parser()
        query = {"filter": {"field": "age", "op": "between", "value": [18, 65]}}
        ast = parser.parse(query)
        assert ast.op == "between"
        assert ast.value == [18, 65]

    def test_between_not_list(self):
        """测试 between 值不是列表"""
        parser = Parser()
        query = {"filter": {"field": "age", "op": "between", "value": 18}}
        with pytest.raises(ValidationError) as exc:
            parser.parse(query)
        assert "between" in str(exc.value).lower()
        assert "list" in str(exc.value).lower()

    def test_between_wrong_length(self):
        """测试 between 列表长度不是 2"""
        parser = Parser()
        query = {"filter": {"field": "age", "op": "between", "value": [1, 2, 3]}}
        with pytest.raises(ValidationError) as exc:
            parser.parse(query)
        assert "between" in str(exc.value).lower()
        assert "2 elements" in str(exc.value).lower()

    def test_between_single_element(self):
        """测试 between 只有一个元素"""
        parser = Parser()
        query = {"filter": {"field": "age", "op": "between", "value": [18]}}
        with pytest.raises(ValidationError) as exc:
            parser.parse(query)
        assert "2 elements" in str(exc.value).lower()


class TestInOperator:
    """测试 in 操作符"""

    def test_in_valid(self):
        """测试 in 正确格式"""
        parser = Parser()
        query = {"filter": {"field": "status", "op": "in", "value": ["active", "pending"]}}
        ast = parser.parse(query)
        assert ast.op == "in"
        assert ast.value == ["active", "pending"]

    def test_in_not_list(self):
        """测试 in 值不是列表"""
        parser = Parser()
        query = {"filter": {"field": "status", "op": "in", "value": "active"}}
        with pytest.raises(ValidationError) as exc:
            parser.parse(query)
        assert "in" in str(exc.value).lower()
        assert "list" in str(exc.value).lower()

    def test_in_empty_list(self):
        """测试 in 空列表"""
        parser = Parser()
        query = {"filter": {"field": "status", "op": "in", "value": []}}
        with pytest.raises(ValidationError) as exc:
            parser.parse(query)
        assert "in" in str(exc.value).lower()
        assert "empty" in str(exc.value).lower()


class TestNotInOperator:
    """测试 notIn 操作符"""

    def test_notIn_valid(self):
        """测试 notIn 正确格式"""
        parser = Parser()
        query = {"filter": {"field": "status", "op": "notIn", "value": ["deleted", "archived"]}}
        ast = parser.parse(query)
        assert ast.op == "notIn"
        assert ast.value == ["deleted", "archived"]

    def test_notIn_not_list(self):
        """测试 notIn 值不是列表"""
        parser = Parser()
        query = {"filter": {"field": "status", "op": "notIn", "value": "deleted"}}
        with pytest.raises(ValidationError) as exc:
            parser.parse(query)
        assert "notIn" in str(exc.value)
        assert "list" in str(exc.value).lower()

    def test_notIn_empty_list(self):
        """测试 notIn 空列表"""
        parser = Parser()
        query = {"filter": {"field": "status", "op": "notIn", "value": []}}
        with pytest.raises(ValidationError) as exc:
            parser.parse(query)
        assert "notIn" in str(exc.value)
        assert "empty" in str(exc.value).lower()


class TestNullOperators:
    """测试 isNull 和 isNotNull 操作符"""

    def test_isNull(self):
        """测试 isNull 操作符"""
        parser = Parser()
        query = {"filter": {"field": "deleted_at", "op": "isNull", "value": None}}
        ast = parser.parse(query)
        assert ast.op == "isNull"

    def test_isNull_with_any_value(self):
        """测试 isNull 可以接受任意值"""
        parser = Parser()
        query = {"filter": {"field": "deleted_at", "op": "isNull", "value": "any"}}
        ast = parser.parse(query)
        assert ast.op == "isNull"

    def test_isNotNull(self):
        """测试 isNotNull 操作符"""
        parser = Parser()
        query = {"filter": {"field": "created_at", "op": "isNotNull", "value": None}}
        ast = parser.parse(query)
        assert ast.op == "isNotNull"


class TestStringOperators:
    """测试字符串操作符"""

    def test_startswith_valid(self):
        """测试 startswith 正确格式"""
        parser = Parser()
        query = {"filter": {"field": "name", "op": "startswith", "value": "test"}}
        ast = parser.parse(query)
        assert ast.op == "startswith"
        assert ast.value == "test"

    def test_startswith_not_string(self):
        """测试 startswith 值不是字符串"""
        parser = Parser()
        query = {"filter": {"field": "name", "op": "startswith", "value": 123}}
        with pytest.raises(ValidationError) as exc:
            parser.parse(query)
        assert "startswith" in str(exc.value).lower()
        assert "string" in str(exc.value).lower()

    def test_endswith_valid(self):
        """测试 endswith 正确格式"""
        parser = Parser()
        query = {"filter": {"field": "email", "op": "endswith", "value": "@example.com"}}
        ast = parser.parse(query)
        assert ast.op == "endswith"
        assert ast.value == "@example.com"

    def test_endswith_not_string(self):
        """测试 endswith 值不是字符串"""
        parser = Parser()
        query = {"filter": {"field": "email", "op": "endswith", "value": ["suffix"]}}
        with pytest.raises(ValidationError) as exc:
            parser.parse(query)
        assert "endswith" in str(exc.value).lower()
        assert "string" in str(exc.value).lower()


class TestUnsupportedOperator:
    """测试不支持的操作符"""

    def test_unknown_operator(self):
        """测试未知操作符"""
        parser = Parser()
        query = {"filter": {"field": "age", "op": "unknown", "value": 18}}
        with pytest.raises(UnsupportedOperatorError) as exc:
            parser.parse(query)
        assert "unknown" in str(exc.value)


class TestOperatorInNestedStructure:
    """测试嵌套结构中的操作符"""

    def test_between_in_and(self):
        """测试 between 在 AND 中"""
        parser = Parser()
        query = {
            "filter": {
                "and": [
                    {"field": "age", "op": "between", "value": [18, 65]},
                    {"field": "status", "op": "in", "value": ["active"]}
                ]
            }
        }
        ast = parser.parse(query)
        assert ast.children[0].op == "between"
        assert ast.children[1].op == "in"

    def test_startswith_in_or(self):
        """测试 startswith 在 OR 中"""
        parser = Parser()
        query = {
            "filter": {
                "or": [
                    {"field": "name", "op": "startswith", "value": "test"},
                    {"field": "name", "op": "endswith", "value": "prod"}
                ]
            }
        }
        ast = parser.parse(query)
        assert ast.children[0].op == "startswith"
        assert ast.children[1].op == "endswith"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])

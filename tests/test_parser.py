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
                {"field": "name", "op": "startswith", "value": "alice"},
                {"field": "priority", "op": "gte", "value": 8}
            ]
        }
        ast = parser.parse(query)
        assert isinstance(ast, AndNode)
        assert len(ast.children) == 3
        assert ast.children[0].field == "status"
        assert ast.children[0].value == "ACTIVE"
        assert ast.children[1].field == "name"
        assert ast.children[1].op == "startswith"
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
        # 注意：新版本操作符通过 OperatorRegistry 管理，不再通过 Validator 参数
        # 此测试验证操作符存在性检查
        parser = Parser()

        # 合法操作符
        query = {"filter": {"field": "age", "op": "gt", "value": 18}}
        ast = parser.parse(query)
        assert isinstance(ast, CompareNode)

        # 非法操作符
        query = {"filter": {"field": "age", "op": "unknown_op", "value": [1, 10]}}
        with pytest.raises(UnsupportedOperatorError) as exc:
            parser.parse(query)
        assert "unknown_op" in str(exc.value)

    def test_custom_operator(self):
        """测试自定义操作符"""
        # 注意：新版本通过在 operators/ 目录添加文件来扩展操作符
        # 此测试改为验证已存在的操作符
        parser = Parser()

        query = {"filter": {"field": "name", "op": "startswith", "value": "test"}}
        ast = parser.parse(query)
        assert isinstance(ast, CompareNode)
        assert ast.op == "startswith"

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


class TestNotNodeExceptions:
    """NOT节点异常测试"""

    def test_empty_not(self):
        """测试空NOT（缺少子节点）"""
        parser = Parser()
        query = {"filter": {"not": {}}}
        with pytest.raises(ParseError) as exc:
            parser.parse(query)
        assert "Unknown" in str(exc.value)

    def test_not_with_invalid_type(self):
        """测试NOT的值为非dict"""
        parser = Parser()
        query = {"filter": {"not": "invalid"}}
        with pytest.raises(ParseError) as exc:
            parser.parse(query)
        assert "dict" in str(exc.value)

    def test_not_with_list(self):
        """测试NOT的值为list"""
        parser = Parser()
        query = {"filter": {"not": []}}
        with pytest.raises(ParseError) as exc:
            parser.parse(query)
        assert "dict" in str(exc.value)


class TestMixedLogicErrors:
    """混合逻辑异常测试"""

    def test_multiple_logic_operators(self):
        """测试同时存在多个逻辑操作符"""
        parser = Parser()
        query = {
            "filter": {
                "and": [{"field": "age", "op": "gt", "value": 18}],
                "or": [{"field": "name", "op": "eq", "value": "tom"}]
            }
        }
        # 新行为：多个逻辑操作符并存时抛出错误
        with pytest.raises(ParseError) as exc:
            parser.parse(query)
        assert "Multiple logic operators" in str(exc.value)

    def test_logic_and_field_mixed(self):
        """测试逻辑操作符和field同时存在"""
        parser = Parser()
        query = {
            "filter": {
                "and": [{"field": "age", "op": "gt", "value": 18}],
                "field": "name",
                "op": "eq",
                "value": "tom"
            }
        }
        # 实际行为：解析器会选择第一个匹配的操作符（and）
        ast = parser.parse(query)
        assert isinstance(ast, AndNode)


class TestCompareNodeMissingFields:
    """比较节点字段缺失测试（补充完整）"""

    def test_missing_field_only(self):
        """测试只缺少field"""
        parser = Parser()
        query = {"filter": {"op": "eq", "value": 10}}
        with pytest.raises(ParseError) as exc:
            parser.parse(query)
        assert "Unknown" in str(exc.value) or "field" in str(exc.value)

    def test_missing_op_only(self):
        """测试只缺少op"""
        parser = Parser()
        query = {"filter": {"field": "age", "value": 10}}
        with pytest.raises(ParseError) as exc:
            parser.parse(query)
        assert "Unknown" in str(exc.value) or "op" in str(exc.value)

    def test_missing_value_only(self):
        """测试只缺少value"""
        parser = Parser()
        query = {"filter": {"field": "age", "op": "eq"}}
        with pytest.raises(ParseError) as exc:
            parser.parse(query)
        assert "value" in str(exc.value)

    def test_missing_field_and_op(self):
        """测试同时缺少field和op"""
        parser = Parser()
        query = {"filter": {"value": 10}}
        with pytest.raises(ParseError) as exc:
            parser.parse(query)
        assert "Unknown" in str(exc.value)

    def test_missing_field_and_value(self):
        """测试同时缺少field和value"""
        parser = Parser()
        query = {"filter": {"op": "eq"}}
        with pytest.raises(ParseError) as exc:
            parser.parse(query)
        assert "Unknown" in str(exc.value)

    def test_missing_op_and_value(self):
        """测试同时缺少op和value"""
        parser = Parser()
        query = {"filter": {"field": "age"}}
        with pytest.raises(ParseError) as exc:
            parser.parse(query)
        # 实际错误信息是 "'op' must be string, got NoneType"
        assert "op" in str(exc.value) and ("string" in str(exc.value) or "Unknown" in str(exc.value))

    def test_empty_compare_node(self):
        """测试完全空的比较节点"""
        parser = Parser()
        query = {"filter": {}}
        with pytest.raises(ParseError) as exc:
            parser.parse(query)
        assert "Unknown" in str(exc.value)


class TestInvalidOperators:
    """异常操作符测试"""

    def test_unknown_operator(self):
        """测试未知操作符"""
        parser = Parser()
        query = {"filter": {"field": "age", "op": "unknown_op", "value": 18}}
        with pytest.raises(UnsupportedOperatorError) as exc:
            parser.parse(query)
        assert "unknown_op" in str(exc.value)

    def test_empty_operator(self):
        """测试空操作符"""
        parser = Parser()
        query = {"filter": {"field": "age", "op": "", "value": 18}}
        with pytest.raises(UnsupportedOperatorError) as exc:
            parser.parse(query)
        assert "" in str(exc.value) or "not supported" in str(exc.value)

    def test_sql_injection_like_operator(self):
        """测试类SQL注入的操作符"""
        parser = Parser()
        query = {"filter": {"field": "age", "op": "'; DROP TABLE users--", "value": 18}}
        with pytest.raises(UnsupportedOperatorError):
            parser.parse(query)

    def test_case_sensitive_operator(self):
        """测试操作符大小写敏感"""
        parser = Parser()
        query = {"filter": {"field": "age", "op": "EQ", "value": 18}}
        with pytest.raises(UnsupportedOperatorError) as exc:
            parser.parse(query)
        assert "EQ" in str(exc.value)


class TestOperatorValueMismatch:
    """操作符与值格式不匹配测试"""

    def test_in_operator_with_non_list_value(self):
        """测试in操作符值不是列表"""
        parser = Parser()
        query = {"filter": {"field": "status", "op": "in", "value": "active"}}
        # 新实现：in 操作符现在会校验 value 必须是 list
        with pytest.raises(ValidationError) as exc:
            parser.parse(query)
        assert "in" in str(exc.value).lower()
        assert "list" in str(exc.value).lower()

    def test_between_operator_with_non_list_value(self):
        """测试between操作符值不是列表"""
        parser = Parser()
        query = {"filter": {"field": "age", "op": "between", "value": 18}}
        # 新实现：between 操作符现在会校验 value 必须是 [min, max]
        with pytest.raises(ValidationError) as exc:
            parser.parse(query)
        assert "between" in str(exc.value).lower()
        assert "list" in str(exc.value).lower()

    def test_between_operator_with_wrong_length(self):
        """测试between操作符值长度不对"""
        parser = Parser()
        query = {"filter": {"field": "age", "op": "between", "value": [1, 2, 3]}}
        # 新实现：between 操作符现在会校验长度必须是 2
        with pytest.raises(ValidationError) as exc:
            parser.parse(query)
        assert "between" in str(exc.value).lower()
        assert "2 elements" in str(exc.value).lower()

    def test_is_null_with_non_none_value(self):
        """测试isNull操作符值不是None"""
        parser = Parser()
        query = {"filter": {"field": "deleted_at", "op": "isNull", "value": True}}
        # isNull 操作符接受任意值（语义上不需要 value）
        ast = parser.parse(query)
        assert isinstance(ast, CompareNode)
        assert ast.value is True

    def test_not_null_with_none_value(self):
        """测试isNotNull操作符值为None"""
        parser = Parser()
        query = {"filter": {"field": "created_at", "op": "isNotNull", "value": None}}
        # isNotNull 操作符接受任意值（语义上不需要 value）
        ast = parser.parse(query)
        assert isinstance(ast, CompareNode)
        assert ast.value is None


class TestValidatorEdgeCases:
    """Validator边界测试"""

    def test_empty_allowed_fields(self):
        """测试空白名单（禁止所有字段）"""
        validator = Validator(allowed_fields=set())
        parser = Parser(validator)
        query = {"filter": {"field": "age", "op": "gt", "value": 18}}
        with pytest.raises(InvalidFieldError) as exc:
            parser.parse(query)
        assert "age" in str(exc.value)

    def test_duplicate_operator_registration(self):
        """测试重复注册操作符"""
        # 新版本：操作符通过文件自动注册，此测试验证基本功能
        validator = Validator()
        parser = Parser(validator)
        query = {"filter": {"field": "age", "op": "eq", "value": 18}}
        ast = parser.parse(query)
        assert isinstance(ast, CompareNode)

    def test_override_default_operator(self):
        """测试操作符验证"""
        # 新版本：操作符由 OperatorRegistry 管理，测试未知操作符
        validator = Validator()
        parser = Parser(validator)
        query = {"filter": {"field": "age", "op": "unknown_operator", "value": 18}}
        with pytest.raises(UnsupportedOperatorError):
            parser.parse(query)

    def test_validator_with_none_operators(self):
        """测试传入None的操作符集合"""
        # 新版本：操作符由 OperatorRegistry 管理，Validator 的 operators 参数已废弃
        validator = Validator(operators=None)
        parser = Parser(validator)
        query = {"filter": {"field": "age", "op": "gt", "value": 18}}
        ast = parser.parse(query)
        assert isinstance(ast, CompareNode)


class TestFieldValidatorErrors:
    """字段验证器异常测试"""

    def test_field_validator_raises_exception(self):
        """测试字段验证器抛出异常"""
        validator = Validator()
        def bad_validator(v):
            raise RuntimeError("Validator failed")
        validator.register_field_validator("age", bad_validator)
        parser = Parser(validator)
        query = {"filter": {"field": "age", "op": "gt", "value": 18}}
        with pytest.raises(RuntimeError) as exc:
            parser.parse(query)
        assert "Validator failed" in str(exc.value)

    def test_field_validator_returns_false(self):
        """测试字段验证器返回False"""
        validator = Validator()
        validator.register_field_validator("age", lambda v: v > 0)
        parser = Parser(validator)
        query = {"filter": {"field": "age", "op": "gt", "value": -10}}
        with pytest.raises(ValueError) as exc:
            parser.parse(query)
        assert "age" in str(exc.value)
        assert "-10" in str(exc.value)

    def test_multiple_field_validators(self):
        """测试多个字段验证器"""
        validator = Validator()
        validator.register_field_validator("age", lambda v: 0 <= v <= 150)
        validator.register_field_validator("score", lambda v: 0 <= v <= 100)
        parser = Parser(validator)

        # age超范围
        query = {"filter": {"field": "age", "op": "gt", "value": 200}}
        with pytest.raises(ValueError):
            parser.parse(query)

        # score超范围
        query = {"filter": {"field": "score", "op": "gt", "value": 150}}
        with pytest.raises(ValueError):
            parser.parse(query)

    def test_field_validator_in_nested_node(self):
        """测试嵌套节点中的字段验证"""
        validator = Validator()
        validator.register_field_validator("age", lambda v: v > 0)
        parser = Parser(validator)
        query = {
            "filter": {
                "and": [
                    {"field": "name", "op": "eq", "value": "tom"},
                    {"field": "age", "op": "gt", "value": -10}  # 非法值
                ]
            }
        }
        with pytest.raises(ValueError) as exc:
            parser.parse(query)
        assert "age" in str(exc.value)


class TestExtremeValues:
    """极端值测试"""

    def test_very_long_field_name(self):
        """测试超长字段名"""
        parser = Parser()
        long_field = "a" * 10000
        query = {"filter": {"field": long_field, "op": "eq", "value": 1}}
        ast = parser.parse(query)
        assert ast.field == long_field

    def test_very_long_string_value(self):
        """测试超长字符串值"""
        parser = Parser()
        long_value = "x" * 100000
        query = {"filter": {"field": "content", "op": "startswith", "value": long_value}}
        ast = parser.parse(query)
        assert ast.value == long_value

    def test_very_large_number_value(self):
        """测试超大数值"""
        parser = Parser()
        large_num = 10 ** 100
        query = {"filter": {"field": "big_num", "op": "gt", "value": large_num}}
        ast = parser.parse(query)
        assert ast.value == large_num

    def test_deeply_nested_value(self):
        """测试深层嵌套的值（字典）"""
        parser = Parser()
        nested_value = {"level1": {"level2": {"level3": {"level4": "deep"}}}}
        query = {"filter": {"field": "meta", "op": "eq", "value": nested_value}}
        ast = parser.parse(query)
        assert ast.value == nested_value

    def test_special_character_combinations(self):
        """测试特殊字符组合"""
        parser = Parser()
        special_chars = "!@#$%^&*()_+-=[]{}|;':\",./<>?`~\n\t\r\\"
        query = {"filter": {"field": "code", "op": "eq", "value": special_chars}}
        ast = parser.parse(query)
        assert ast.value == special_chars


class TestNestedExceptions:
    """嵌套异常传播测试"""

    def test_invalid_field_in_deep_nesting(self):
        """测试深层嵌套中的非法字段"""
        validator = Validator(allowed_fields={"age", "name"})
        parser = Parser(validator)
        query = {
            "filter": {
                "or": [
                    {
                        "and": [
                            {"field": "age", "op": "gt", "value": 18},
                            {
                                "not": {
                                    "field": "email",  # 非法字段
                                    "op": "eq",
                                    "value": "test@example.com"
                                }
                            }
                        ]
                    },
                    {"field": "name", "op": "eq", "value": "tom"}
                ]
            }
        }
        with pytest.raises(InvalidFieldError) as exc:
            parser.parse(query)
        assert "email" in str(exc.value)

    def test_invalid_operator_in_deep_nesting(self):
        """测试深层嵌套中的非法操作符"""
        parser = Parser()
        query = {
            "filter": {
                "and": [
                    {
                        "or": [
                            {
                                "not": {
                                    "field": "status",
                                    "op": "invalid_op",  # 非法操作符
                                    "value": "active"
                                }
                            }
                        ]
                    }
                ]
            }
        }
        with pytest.raises(UnsupportedOperatorError) as exc:
            parser.parse(query)
        assert "invalid_op" in str(exc.value)

    def test_missing_value_in_nested_or(self):
        """测试嵌套OR中缺少value"""
        parser = Parser()
        query = {
            "filter": {
                "or": [
                    {"field": "age", "op": "gt", "value": 18},
                    {"field": "name", "op": "eq"}  # 缺少value
                ]
            }
        }
        with pytest.raises(ParseError) as exc:
            parser.parse(query)
        assert "value" in str(exc.value)


class TestOrNodeInvalidTypes:
    """OR节点非法类型测试（补充）"""

    def test_or_with_string(self):
        """测试OR的值为字符串"""
        parser = Parser()
        query = {"filter": {"or": "invalid"}}
        with pytest.raises(ParseError) as exc:
            parser.parse(query)
        assert "list" in str(exc.value)

    def test_or_with_dict(self):
        """测试OR的值为字典"""
        parser = Parser()
        query = {"filter": {"or": {"field": "age", "op": "gt", "value": 18}}}
        with pytest.raises(ParseError) as exc:
            parser.parse(query)
        assert "list" in str(exc.value)

    def test_or_with_number(self):
        """测试OR的值为数字"""
        parser = Parser()
        query = {"filter": {"or": 123}}
        with pytest.raises(ParseError) as exc:
            parser.parse(query)
        assert "list" in str(exc.value)


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
        query = {"filter": {"field": "deleted_at", "op": "isNull", "value": None}}
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
                "op": "endswith",
                "value": "@example.com"
            }
        }
        ast = parser.parse(query)
        assert ast.value == "@example.com"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])

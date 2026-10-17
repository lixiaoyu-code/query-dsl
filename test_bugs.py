"""Bug验证测试"""
import pytest
from parser import Parser
from validator import Validator
from exceptions import ParseError


class TestPotentialBugs:
    """潜在Bug验证"""

    def test_not_with_non_dict_should_fail_clearly(self):
        """Bug1: NOT节点接收非dict类型，错误信息应该明确"""
        parser = Parser()
        query = {"filter": {"not": "invalid_string"}}

        with pytest.raises(ParseError) as exc:
            parser.parse(query)

        # 验证错误信息是否明确
        error_msg = str(exc.value)
        print(f"错误信息: {error_msg}")
        assert "dict" in error_msg.lower()

    def test_in_operator_accepts_non_list_bug(self):
        """Bug2: in操作符应该要求value是列表，但当前没有验证"""
        parser = Parser()

        # 当前实现：接受非列表值（这是bug）
        query = {"filter": {"field": "status", "op": "in", "value": "single_value"}}
        ast = parser.parse(query)  # 不应该成功
        print(f"Bug: in操作符接受了非列表值: {ast.value}")
        assert ast.value == "single_value"  # 证明bug存在

    def test_between_operator_accepts_wrong_format(self):
        """Bug3: between操作符应该要求[min, max]，但当前没有验证"""
        parser = Parser()

        # 接受单个值（错误）
        query1 = {"filter": {"field": "age", "op": "between", "value": 18}}
        ast1 = parser.parse(query1)
        print(f"Bug: between接受了单个值: {ast1.value}")

        # 接受错误长度的列表（错误）
        query2 = {"filter": {"field": "age", "op": "between", "value": [1, 2, 3]}}
        ast2 = parser.parse(query2)
        print(f"Bug: between接受了3个元素的列表: {ast2.value}")

    def test_is_null_operator_should_not_need_value(self):
        """Bug4: is_null操作符语义上不应该需要value，或value应该被忽略"""
        parser = Parser()

        # 当前实现：必须传value（语义不合理）
        query = {"filter": {"field": "deleted_at", "op": "is_null", "value": "any_value"}}
        ast = parser.parse(query)
        print(f"Bug: is_null接受了任意value: {ast.value}")

        # 理想情况：value应该被忽略或不需要
        assert ast.value == "any_value"  # 证明bug存在

    def test_empty_allowed_fields_semantic_issue(self):
        """Bug5: 空字段白名单的语义不清晰"""
        # 场景1: None表示不限制
        validator1 = Validator(allowed_fields=None)
        parser1 = Parser(validator1)
        query = {"filter": {"field": "any_field", "op": "eq", "value": 1}}
        ast1 = parser1.parse(query)  # 成功

        # 场景2: 空set表示禁止所有字段（这个语义可能让用户困惑）
        validator2 = Validator(allowed_fields=set())
        parser2 = Parser(validator2)
        with pytest.raises(Exception):
            parser2.parse(query)  # 失败

        print("语义问题: None=不限制, set()=禁止所有")

    def test_field_validator_exception_propagation(self):
        """Bug6: 字段验证器抛出的异常类型不一致"""
        validator = Validator()

        # 情况1: 验证器返回False -> 抛出ValueError
        validator.register_field_validator("age1", lambda v: v > 0)
        parser1 = Parser(validator)
        query1 = {"filter": {"field": "age1", "op": "gt", "value": -10}}
        with pytest.raises(ValueError):
            parser1.parse(query1)

        # 情况2: 验证器抛出RuntimeError -> 直接传播RuntimeError
        def bad_validator(v):
            raise RuntimeError("Custom error")
        validator.register_field_validator("age2", bad_validator)
        parser2 = Parser(validator)
        query2 = {"filter": {"field": "age2", "op": "gt", "value": 10}}
        with pytest.raises(RuntimeError):  # 不是ValueError
            parser2.parse(query2)

        print("Bug: 异常类型不一致，有时是ValueError，有时是其他异常")

    def test_multiple_logic_operators_ambiguity(self):
        """Bug7: 同时存在多个逻辑操作符时，行为不明确"""
        parser = Parser()
        query = {
            "filter": {
                "and": [{"field": "age", "op": "gt", "value": 18}],
                "or": [{"field": "name", "op": "eq", "value": "tom"}],
                "not": {"field": "deleted", "op": "eq", "value": True}
            }
        }

        # 当前实现：按照检查顺序（and -> or -> not）选择第一个
        ast = parser.parse(query)
        print(f"Bug: 多个逻辑操作符并存，解析器选择了第一个: {type(ast).__name__}")
        # 理想情况：应该抛出错误，要求用户明确意图


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])

"""演示 Bug2: 多个逻辑操作符并存的问题"""
from parser import Parser
from nodes import AndNode, OrNode, NotNode


def demo_multiple_operators():
    """演示同一个节点包含多个逻辑操作符"""
    parser = Parser()

    # 问题场景：一个 filter 节点同时包含 and、or、not
    query = {
        "filter": {
            "and": [
                {"field": "age", "op": "gt", "value": 18}
            ],
            "or": [
                {"field": "status", "op": "eq", "value": "active"}
            ],
            "not": {
                "field": "deleted", "op": "eq", "value": True
            }
        }
    }

    print("=" * 60)
    print("查询语句（同时包含 and、or、not）:")
    print(query)
    print()

    # 解析结果
    ast = parser.parse(query)

    print(f"解析结果类型: {type(ast).__name__}")
    print(f"实际使用的操作符: and")
    print(f"被忽略的操作符: or, not")
    print()

    print("问题说明:")
    print("1. 用户可能期望这是一个语法错误（不允许多个操作符并存）")
    print("2. 或者用户可能期望某种组合逻辑（但实际只有第一个生效）")
    print("3. 其他两个操作符 'or' 和 'not' 被静默忽略了")
    print()

    # 验证只有 and 生效
    assert isinstance(ast, AndNode), "解析器选择了 and"
    assert len(ast.children) == 1
    print(f"✓ 确认：只有 'and' 操作符生效，包含 {len(ast.children)} 个子节点")
    print()


def demo_order_matters():
    """演示操作符顺序影响结果"""
    parser = Parser()

    print("=" * 60)
    print("演示：操作符顺序影响解析结果")
    print()

    # 情况 1: or 在前
    query1 = {
        "filter": {
            "or": [{"field": "a", "op": "eq", "value": 1}],
            "and": [{"field": "b", "op": "eq", "value": 2}]
        }
    }

    # 情况 2: and 在前
    query2 = {
        "filter": {
            "and": [{"field": "b", "op": "eq", "value": 2}],
            "or": [{"field": "a", "op": "eq", "value": 1}]
        }
    }

    ast1 = parser.parse(query1)
    ast2 = parser.parse(query2)

    # 注意：Python 3.7+ 字典保持插入顺序
    # 但解析器按照代码检查顺序 (and -> or -> not)，不是字典顺序
    print(f"情况1 (字典顺序: or, and): 解析结果 = {type(ast1).__name__}")
    print(f"情况2 (字典顺序: and, or): 解析结果 = {type(ast2).__name__}")
    print()
    print("实际上解析器按照代码固定顺序检查: and -> or -> not")
    print("所以两种情况都选择了 'and'（如果存在）")
    print()


def demo_correct_usage():
    """演示正确的用法"""
    parser = Parser()

    print("=" * 60)
    print("正确用法：每个节点只能有一个逻辑操作符")
    print()

    # 正确: 只有 and
    query1 = {
        "filter": {
            "and": [
                {"field": "age", "op": "gt", "value": 18},
                {"field": "status", "op": "eq", "value": "active"}
            ]
        }
    }

    # 正确: 嵌套使用多个操作符
    query2 = {
        "filter": {
            "and": [
                {"field": "age", "op": "gt", "value": 18},
                {
                    "or": [
                        {"field": "status", "op": "eq", "value": "active"},
                        {"field": "status", "op": "eq", "value": "pending"}
                    ]
                }
            ]
        }
    }

    ast1 = parser.parse(query1)
    ast2 = parser.parse(query2)

    print("✓ 正确示例1: 单个 and 操作符")
    print(f"  结果: {type(ast1).__name__} with {len(ast1.children)} children")
    print()

    print("✓ 正确示例2: 通过嵌套组合多个操作符")
    print(f"  结果: {type(ast2).__name__} with {len(ast2.children)} children")
    print(f"  第2个子节点是: {type(ast2.children[1]).__name__}")
    print()


if __name__ == "__main__":
    demo_multiple_operators()
    demo_order_matters()
    demo_correct_usage()

    print("=" * 60)
    print("总结:")
    print("问题: 当一个节点同时包含多个逻辑操作符时，")
    print("      解析器不会报错，而是静默选择第一个匹配的操作符")
    print("改进建议: 检测到多个操作符并存时，应该抛出 ParseError")

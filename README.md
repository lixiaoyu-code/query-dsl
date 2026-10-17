# 查询DSL解析器

高性能的通用查询DSL解析器，将JSON结构转换为AST，支持类似SQL WHERE子句的过滤逻辑。

## 特性

- **高性能**：使用`__slots__`优化内存，简单查询<1μs，复杂嵌套<3μs
- **类型安全**：基于dataclass的AST节点定义
- **可扩展**：支持自定义操作符和字段验证器
- **结构检查**：解析时进行字段白名单和操作符验证
- **灵活语法**：单条件用dict，多条件用list，自动转换

## 快速开始

### 单条件查询
```python
from parser import Parser

parser = Parser()

# 方式1：直接写条件（推荐）
query = {
    "filter": {
        "field": "age",
        "op": "gt",
        "value": 18
    }
}
ast = parser.parse(query)
print(ast)  # CompareNode(field='age', op='gt', value=18)
```

### 多条件查询（简化语法）
```python
# 方式2：数组自动转为AND（简洁）
query = {
    "filter": [
        {"field": "status", "op": "eq", "value": "ACTIVE"},
        {"field": "name", "op": "like", "value": "alice"},
        {"field": "priority", "op": "gte", "value": 8}
    ]
}
ast = parser.parse(query)
print(ast)  # AndNode(3 children)
```

## 支持的操作符

默认支持：`eq`, `ne`, `gt`, `gte`, `lt`, `lte`, `in`, `not_in`, `like`, `ilike`, `is_null`, `not_null`, `between`

## 语法说明

### 单条件 vs 多条件

```python
# 单条件：直接写dict（返回CompareNode）
{"filter": {"field": "age", "op": "gt", "value": 18}}

# 多条件：用数组（返回AndNode，自动转换）
{"filter": [
    {"field": "age", "op": "gt", "value": 18},
    {"field": "status", "op": "eq", "value": "ACTIVE"}
]}

# 等价于标准写法
{"filter": {"and": [...]}}
```

**注意**：单条件list写法会创建AndNode（逻辑等价但AST结构不同）
```python
# 这两种逻辑等价，但AST不同
{"filter": {"field": "age", "op": "gt", "value": 18}}        # CompareNode
{"filter": [{"field": "age", "op": "gt", "value": 18}]}     # AndNode(1 child)
```

## 逻辑操作

### AND
```python
{
    "filter": {
        "and": [
            {"field": "age", "op": "gt", "value": 18},
            {"field": "name", "op": "eq", "value": "tom"}
        ]
    }
}
```

### OR
```python
{
    "filter": {
        "or": [
            {"field": "status", "op": "eq", "value": "active"},
            {"field": "status", "op": "eq", "value": "pending"}
        ]
    }
}
```

### NOT
```python
{
    "filter": {
        "not": {
            "field": "deleted",
            "op": "eq",
            "value": True
        }
    }
}
```

### 嵌套逻辑
```python
{
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
```

## 验证和扩展

### 字段白名单
```python
from validator import Validator

validator = Validator(allowed_fields={"age", "name", "status"})
parser = Parser(validator)
```

### 自定义操作符
```python
validator = Validator()
validator.register_operator("regex")
parser = Parser(validator)
```

### 字段值验证
```python
validator = Validator()
validator.register_field_validator("age", lambda v: 0 <= v <= 150)
parser = Parser(validator)
```

## 性能指标

- 简单查询：0.67μs/次
- 复杂嵌套：2.92μs/次
- 深层嵌套(10层)：10.24μs/次
- 宽OR(100条件)：0.06ms/次

## 运行测试

```bash
python -m venv venv
source venv/bin/activate
pip install pytest
python -m pytest test_parser.py -v -s
```

## 文件结构

```
query-dsl/
├── nodes.py        # AST节点定义
├── parser.py       # 解析器主逻辑
├── validator.py    # 验证和扩展机制
├── exceptions.py   # 自定义异常
├── __init__.py     # 包入口
└── test_parser.py  # 测试用例
```

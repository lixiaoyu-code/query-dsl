# 查询DSL解析器

[English](./README_EN.md) | 中文

**一个轻量级的Python库，将JSON查询条件解析为抽象语法树（AST）**

帮助你在应用程序中快速构建灵活的查询系统：
- 📥 **输入**：接收类似 MongoDB 风格的 JSON 查询条件
- 🌲 **输出**：返回结构化的 AST 对象
- 🔌 **用途**：可对接到任何数据源（SQL、NoSQL、内存对象等）

适用场景：API 查询接口、动态报表过滤、权限规则引擎、配置化查询等。

## 特性

- **高性能**：使用`__slots__`优化内存，简单查询~1μs，宽OR(100条件)~0.10ms
- **类型安全**：基于dataclass的AST节点定义
- **操作符系统**：面向对象架构，每个操作符独立管理，自动注册
- **值格式校验**：操作符自动验证值格式（如`in`要求列表，`between`要求2元素）
- **易扩展**：新增操作符只需在`operators/`目录添加文件，零配置
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

### 比较操作符
- `eq`：等于
- `ne`：不等于
- `gt` / `gte`：大于 / 大于等于
- `lt` / `lte`：小于 / 小于等于

### 范围操作符
- `between`：范围查询，值必须是 `[min, max]` 格式

### 集合操作符
- `in`：包含于，值必须是非空列表
- `notIn`：不包含于，值必须是非空列表

### 空值操作符
- `isNull`：字段为空
- `isNotNull`：字段不为空

### 字符串操作符
- `startswith`：前缀匹配，值必须是字符串
- `endswith`：后缀匹配，值必须是字符串

### 操作符值格式校验

操作符会自动校验值格式：
```python
# ✅ 正确
{"field": "age", "op": "between", "value": [18, 65]}
{"field": "status", "op": "in", "value": ["active", "pending"]}

# ❌ 错误：between 需要2元素列表
{"field": "age", "op": "between", "value": 18}
# 抛出: ValidationError: Operator 'between' requires a list value [min, max]

# ❌ 错误：in 需要非空列表
{"field": "status", "op": "in", "value": "active"}
# 抛出: ValidationError: Operator 'in' requires a list value
```

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

# 合法字段
query = {"filter": {"field": "age", "op": "gt", "value": 18}}  # ✅

# 非法字段
query = {"filter": {"field": "email", "op": "eq", "value": "test@example.com"}}  # ❌
# 抛出: InvalidFieldError: Field 'email' is not allowed
```

### 扩展操作符

新增操作符只需在 `operators/` 目录添加文件：

```python
# operators/regex.py
from typing import Any
from .base import Operator
from exceptions import ValidationError

class RegexOperator(Operator):
    """正则表达式匹配操作符"""
    name = "regex"
    
    @classmethod
    def validate(cls, value: Any) -> None:
        if not isinstance(value, str):
            raise ValidationError(
                f"Operator 'regex' requires a string pattern, "
                f"got {type(value).__name__}"
            )
```

保存文件后，操作符自动注册，立即可用，无需任何配置！

### 字段值验证
```python
from parser import Parser
from validator import Validator

validator = Validator()
# 年龄必须在 0-150 之间
validator.register_field_validator("age", lambda v: 0 <= v <= 150)
parser = Parser(validator)

query = {"filter": {"field": "age", "op": "gt", "value": 200}}  # ❌
# 抛出: ValueError: Invalid value for field 'age': 200
```

## 性能指标

在 MacBook (Python 3.14) 上的性能测试：

| 场景 | 性能 | 说明 |
|------|------|------|
| 简单解析 | ~1.14μs/次 | 单个 CompareNode |
| 复杂嵌套 | ~5.00μs/次 | OR + NOT + AND 组合 |
| 深层嵌套 | ~16.79μs/次 | 10层嵌套 |
| 宽OR(100条件) | ~0.10ms/次 | 100个并列条件 |

**性能说明**：
- 操作符值校验增加约 0.3-0.4μs/次 开销（100条件下约+0.04ms）
- 使用类方法优化，避免对象实例化开销
- 性能与旧版相比略有下降，但换取了更严格的值格式校验

## 运行测试

```bash
python -m venv venv
source venv/bin/activate
pip install pytest
python -m pytest tests/ -v -s
```

## 文件结构

```
query-dsl/
├── operators/              # 操作符目录（面向对象架构）
│   ├── __init__.py        # 自动扫描注册
│   ├── base.py            # 操作符基类和注册器
│   ├── eq.py              # 等于操作符
│   ├── between.py         # 范围操作符
│   ├── in_op.py           # in 操作符
│   └── ...                # 其他操作符
├── nodes.py               # AST节点定义
├── parser.py              # 解析器主逻辑
├── validator.py           # 验证器
├── exceptions.py          # 自定义异常
├── __init__.py            # 包入口
├── tests/                 # 测试目录\n│   ├── test_parser.py     # 解析器测试
│   └── test_operators.py  # 操作符测试\n└── docs/                  # 文档目录\n    ├── README.md          # 中文文档\n    └── README_EN.md       # 英文文档
```

## 设计原则

### Bug 修复记录

**Bug #1**: 多个逻辑操作符并存时，解析器静默选择第一个
- **问题**: `{"and": [...], "or": [...]}` 只有 `and` 生效
- **修复**: 检测到多操作符时抛出 `ParseError`

**Bug #2**: 操作符值格式不校验
- **问题**: `in` 接受非列表值，`between` 接受单值
- **修复**: 建立操作符类系统，每个操作符自己校验值格式

### 架构设计

**操作符系统**采用面向对象设计：
- **基类** `Operator`：定义统一接口
- **自动注册**：通过 `__init_subclass__` 元类钩子
- **零配置**：扫描 `operators/` 目录自动加载
- **易扩展**：新增操作符 = 新建文件

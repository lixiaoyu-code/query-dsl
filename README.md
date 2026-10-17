# 查询DSL解析器 / Query DSL Parser

**完整文档请查看 / For full documentation:**

- [中文文档](./docs/README.md)
- [English Documentation](./docs/README_EN.md)

---

## 快速开始 / Quick Start

```python
from parser import Parser

parser = Parser()
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

## 运行测试 / Run Tests

```bash
python -m venv venv
source venv/bin/activate
pip install pytest
python -m pytest tests/ -v -s
```

## 目录结构 / Directory Structure

```
query-dsl/
├── operators/        # 操作符 / Operators
├── tests/            # 测试 / Tests
├── docs/             # 文档 / Documentation
├── parser.py         # 解析器 / Parser
├── validator.py      # 验证器 / Validator
├── nodes.py          # AST节点 / AST Nodes
└── exceptions.py     # 异常 / Exceptions
```

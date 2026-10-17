# Query DSL Parser

English | [中文](./README.md)

**A lightweight Python library that parses JSON query conditions into Abstract Syntax Trees (AST)**

Quickly build flexible query systems in your applications:
- 📥 **Input**: Accept MongoDB-style JSON query conditions
- 🌲 **Output**: Return structured AST objects
- 🔌 **Usage**: Connect to any data source (SQL, NoSQL, in-memory objects, etc.)

Use cases: API query interfaces, dynamic report filtering, permission rule engines, configurable queries, etc.

## Features

- **High Performance**: Memory-optimized with `__slots__`, simple queries <1μs, complex nested <3μs
- **Type Safe**: Dataclass-based AST node definitions
- **Extensible**: Support custom operators and field validators
- **Structure Validation**: Field whitelist and operator validation during parsing
- **Flexible Syntax**: Single condition uses dict, multiple conditions use list with auto-conversion

## Quick Start

### Single Condition Query
```python
from parser import Parser

parser = Parser()

# Method 1: Direct condition (recommended)
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

### Multiple Conditions Query (Simplified Syntax)
```python
# Method 2: Array auto-converts to AND (concise)
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

## Supported Operators

Default support: `eq`, `ne`, `gt`, `gte`, `lt`, `lte`, `in`, `not_in`, `like`, `ilike`, `is_null`, `not_null`, `between`

## Syntax Guide

### Single vs Multiple Conditions

```python
# Single condition: Direct dict (returns CompareNode)
{"filter": {"field": "age", "op": "gt", "value": 18}}

# Multiple conditions: Use array (returns AndNode, auto-converted)
{"filter": [
    {"field": "age", "op": "gt", "value": 18},
    {"field": "status", "op": "eq", "value": "ACTIVE"}
]}

# Equivalent to standard syntax
{"filter": {"and": [...]}}
```

**Note**: Single condition in list syntax creates AndNode (logically equivalent but different AST structure)
```python
# These two are logically equivalent, but different AST
{"filter": {"field": "age", "op": "gt", "value": 18}}        # CompareNode
{"filter": [{"field": "age", "op": "gt", "value": 18}]}     # AndNode(1 child)
```

## Logical Operations

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

### Nested Logic
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

## Validation and Extension

### Field Whitelist
```python
from validator import Validator

validator = Validator(allowed_fields={"age", "name", "status"})
parser = Parser(validator)
```

### Custom Operators
```python
validator = Validator()
validator.register_operator("regex")
parser = Parser(validator)
```

### Field Value Validation
```python
validator = Validator()
validator.register_field_validator("age", lambda v: 0 <= v <= 150)
parser = Parser(validator)
```

## Performance Metrics

- Simple query: 0.67μs/query
- Complex nested: 2.92μs/query
- Deep nesting (10 levels): 10.24μs/query
- Wide OR (100 conditions): 0.06ms/query

## Run Tests

```bash
python -m venv venv
source venv/bin/activate
pip install pytest
python -m pytest test_parser.py -v -s
```

## File Structure

```
query-dsl/
├── nodes.py        # AST node definitions
├── parser.py       # Parser main logic
├── validator.py    # Validation and extension mechanism
├── exceptions.py   # Custom exceptions
├── __init__.py     # Package entry
└── test_parser.py  # Test cases
```

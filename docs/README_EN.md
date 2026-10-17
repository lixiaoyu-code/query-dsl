# Query DSL Parser

English | [中文](./README.md)

**A lightweight Python library that parses JSON query conditions into Abstract Syntax Trees (AST)**

Quickly build flexible query systems in your applications:
- 📥 **Input**: Accept MongoDB-style JSON query conditions
- 🌲 **Output**: Return structured AST objects
- 🔌 **Usage**: Connect to any data source (SQL, NoSQL, in-memory objects, etc.)

Use cases: API query interfaces, dynamic report filtering, permission rule engines, configurable queries, etc.

## Features

- **High Performance**: Memory-optimized with `__slots__`, simple queries ~1μs, wide OR (100 conditions) ~0.10ms
- **Type Safe**: Dataclass-based AST node definitions
- **Operator System**: Object-oriented architecture, each operator independently managed, auto-registered
- **Value Format Validation**: Operators automatically validate value formats (e.g., `in` requires list, `between` requires 2 elements)
- **Easy to Extend**: Add new operators by simply adding files to `operators/` directory, zero configuration
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

### Comparison Operators
- `eq`: Equal to
- `ne`: Not equal to
- `gt` / `gte`: Greater than / Greater than or equal to
- `lt` / `lte`: Less than / Less than or equal to

### Range Operators
- `between`: Range query, value must be in `[min, max]` format

### Set Operators
- `in`: Contained in, value must be a non-empty list
- `notIn`: Not contained in, value must be a non-empty list

### Null Operators
- `isNull`: Field is null
- `isNotNull`: Field is not null

### String Operators
- `startswith`: Prefix match, value must be a string
- `endswith`: Suffix match, value must be a string

### Operator Value Format Validation

Operators automatically validate value formats:
```python
# ✅ Correct
{"field": "age", "op": "between", "value": [18, 65]}
{"field": "status", "op": "in", "value": ["active", "pending"]}

# ❌ Error: between requires 2-element list
{"field": "age", "op": "between", "value": 18}
# Raises: ValidationError: Operator 'between' requires a list value [min, max]

# ❌ Error: in requires non-empty list
{"field": "status", "op": "in", "value": "active"}
# Raises: ValidationError: Operator 'in' requires a list value
```

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

# Valid field
query = {"filter": {"field": "age", "op": "gt", "value": 18}}  # ✅

# Invalid field
query = {"filter": {"field": "email", "op": "eq", "value": "test@example.com"}}  # ❌
# Raises: InvalidFieldError: Field 'email' is not allowed
```

### Extending Operators

Add new operators by simply adding a file to the `operators/` directory:

```python
# operators/regex.py
from typing import Any
from .base import Operator
from exceptions import ValidationError

class RegexOperator(Operator):
    """Regular expression match operator"""
    name = "regex"
    
    @classmethod
    def validate(cls, value: Any) -> None:
        if not isinstance(value, str):
            raise ValidationError(
                f"Operator 'regex' requires a string pattern, "
                f"got {type(value).__name__}"
            )
```

After saving the file, the operator is automatically registered and immediately available, no configuration needed!

### Field Value Validation
```python
from parser import Parser
from validator import Validator

validator = Validator()
# Age must be between 0-150
validator.register_field_validator("age", lambda v: 0 <= v <= 150)
parser = Parser(validator)

query = {"filter": {"field": "age", "op": "gt", "value": 200}}  # ❌
# Raises: ValueError: Invalid value for field 'age': 200
```

## Performance Metrics

Performance benchmarks on MacBook (Python 3.14):

| Scenario | Performance | Description |
|----------|-------------|-------------|
| Simple parsing | ~1.14μs/query | Single CompareNode |
| Complex nested | ~5.00μs/query | OR + NOT + AND combination |
| Deep nesting | ~16.79μs/query | 10-level nesting |
| Wide OR (100 conditions) | ~0.10ms/query | 100 parallel conditions |

**Performance Notes**:
- Operator value validation adds approximately 0.3-0.4μs per query overhead (about +0.04ms for 100 conditions)
- Uses classmethod optimization to avoid object instantiation overhead
- Slightly slower than old version, but trades off for stricter value format validation

## Run Tests

```bash
python -m venv venv
source venv/bin/activate
pip install pytest
python -m pytest tests/ -v -s
```

## File Structure

```
query-dsl/
├── operators/              # Operator directory (OOP architecture)
│   ├── __init__.py        # Auto-scan and register
│   ├── base.py            # Operator base class and registry
│   ├── eq.py              # Equal operator
│   ├── between.py         # Range operator
│   ├── in_op.py           # In operator
│   └── ...                # Other operators
├── nodes.py               # AST node definitions
├── parser.py              # Parser main logic
├── validator.py           # Validator
├── exceptions.py          # Custom exceptions
├── __init__.py            # Package entry
├── tests/                 # Test directory
│   ├── test_parser.py     # Parser tests
│   └── test_operators.py  # Operator tests
└── docs/                  # Documentation
    ├── README.md          # Chinese README
    └── README_EN.md       # English README
```

## Design Principles

### Bug Fix History

**Bug #1**: Multiple logic operators coexisting, parser silently selects the first one
- **Issue**: `{"and": [...], "or": [...]}` only `and` takes effect
- **Fix**: Throw `ParseError` when multiple operators detected

**Bug #2**: Operator value format not validated
- **Issue**: `in` accepts non-list values, `between` accepts single values
- **Fix**: Establish operator class system, each operator validates its own value format

### Architecture Design

**Operator System** uses object-oriented design:
- **Base class** `Operator`: Define unified interface
- **Auto-registration**: Through `__init_subclass__` metaclass hook
- **Zero configuration**: Scan `operators/` directory and auto-load
- **Easy to extend**: Add new operator = add new file

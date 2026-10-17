"""操作符模块：自动扫描并注册所有操作符"""
import os
import importlib
from pathlib import Path
from .base import Operator, OperatorRegistry

# 获取当前目录
current_dir = Path(__file__).parent

# 自动导入所有操作符文件
for file in current_dir.glob("*.py"):
    # 跳过 __init__.py 和 base.py
    if file.stem in ("__init__", "base"):
        continue

    # 动态导入模块
    module_name = f"operators.{file.stem}"
    try:
        importlib.import_module(module_name)
    except Exception as e:
        print(f"Warning: Failed to import {module_name}: {e}")

# 导出公共接口
__all__ = ["Operator", "OperatorRegistry"]

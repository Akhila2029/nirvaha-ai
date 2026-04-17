#!/usr/bin/env python3
"""Quick syntax check without loading models"""
import ast
import sys

files_to_check = [
    "main.py",
    "rag_service.py",
    "embeddings.py",
    "vector_store.py"
]

print("Checking Python syntax...\n")

all_valid = True
for filename in files_to_check:
    try:
        with open(filename, 'r') as f:
            code = f.read()
        ast.parse(code)
        print(f"✓ {filename}: Syntax OK")
    except SyntaxError as e:
        print(f"✗ {filename}: Syntax Error at line {e.lineno}: {e.msg}")
        all_valid = False
    except Exception as e:
        print(f"✗ {filename}: {e}")
        all_valid = False

print()
if all_valid:
    print("✓ All files have valid Python syntax!")
    sys.exit(0)
else:
    print("✗ Some files have syntax errors")
    sys.exit(1)

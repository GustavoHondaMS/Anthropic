import json
import ast
import re

def validate_json(text):
    try:
        json.loads(text.strip())
        return 10
    except json.JSONDecodeError:
        return 0
    

def validate_python(text):
    try:
        ast.parse(text.strip())
        return 10
    except SyntaxError:
        return 0
    

def validate_regex(text):
    try:
        re.compile(text.strip())
        return 10
    except re.error:
        return 0
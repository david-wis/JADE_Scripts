import autopep8

def fix(code: str) -> str:
    fixed_code = autopep8.fix_code(code)
    return fixed_code
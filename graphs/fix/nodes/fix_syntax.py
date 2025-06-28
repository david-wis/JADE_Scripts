import autopep8

def fix(code: str) -> dict:
    fixed_code = autopep8.fix_code(code)
    return {"code": fixed_code, "error": ""}
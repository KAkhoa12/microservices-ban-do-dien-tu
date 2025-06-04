import re

def checkSDT(sdt):
    if not sdt:
        return False
    sdt_clean = re.sub(r'[\s\-\(\)\+]', '', str(sdt))
    if not sdt_clean.isdigit():
        return False
    if len(sdt_clean) == 10 and sdt_clean.startswith('0'):
        return True
    elif len(sdt_clean) == 11 and sdt_clean.startswith('84'):
        return True
    elif len(sdt_clean) == 12 and sdt.startswith('+84'):
        return True
    return False

def checkEmail(email):
    if not email or not isinstance(email, str):
        return False
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(email_pattern, email))

def checkUsername(username):
    if not username or not isinstance(username, str):
        return False
    if len(username) < 3 or len(username) > 30:
        return False
    pattern = r'^[a-zA-Z0-9]+$'
    return bool(re.match(pattern, username))
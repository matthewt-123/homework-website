def check_pw(pw):
    val = True
    SpecialSym = ['$', '!', '@', '#', '%', '^', '&', '*', '(', ')']
    if len(pw) < 8:
        val = False
        return "Password should be at least 8 characters long"
    if not any(char.isdigit() for char in pw):
        val = False
        return "Password should have at least one numeral"
    if not any(char.isupper() for char in pw):
        val = False
        return "Password should have at least one uppercase letter"
    if not any(char.islower() for char in pw):
        val = False
        return "Password should have at least one lowercase letter"
    if not any(char in SpecialSym for char in pw):
        val = False
        return "Password should have at least one special symbol(!@#$%^&*())"
    return val
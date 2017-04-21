import re

def is_flag(s):
    return re.search('-[a-zA-Z][a-zA-Z]*', s)

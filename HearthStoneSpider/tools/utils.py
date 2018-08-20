import re

def reMatchFormat(re_str, str):
    re_str = re.match(re_str, str)
    return re_str.group(1) if re_str else ''
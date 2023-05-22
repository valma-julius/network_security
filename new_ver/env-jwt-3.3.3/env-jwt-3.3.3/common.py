from jwcrypto import jwk

def generate_key_pair():
    key = jwk.JWK.generate(kty='RSA', size=2048)
    return key

generated_keys = {
    'PS256': generate_key_pair()
}

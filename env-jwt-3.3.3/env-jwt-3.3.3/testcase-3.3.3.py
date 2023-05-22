import unittest
from datetime import timedelta
import json
from common import generated_keys
import python_jwt as jwt
from jwcrypto.common import base64url_decode, base64url_encode


# Define a new class TestForgedClaims derived from unittest.TestCase
class TestForgedClaims(unittest.TestCase):
    # Define a new test case method within TestForgedClaims
    def test_claim_forgery_vulnerability(self):

        # Create a dictionary payload with 'sub' as 'alice'
        payload = {'sub': 'alice'}
        
        # Generate a JWT with the payload, using a PS256 key, and set it to expire in 60 minutes
        token = jwt.generate_jwt(payload, generated_keys['PS256'], 'PS256', timedelta(minutes=60))

        # Split the generated JWT into three components: header, payload, and signature
        [header, payload, signature] = token.split('.')
        
        # Decode the payload and parse the JSON to get a Python dictionary
        parsed_payload = json.loads(base64url_decode(payload))
        
        # Change the 'sub' claim in the parsed payload to 'root'
        parsed_payload['sub'] = 'admin'
        
        # Set an expiry time to a future value
        parsed_payload['exp'] = 2000000000
        
        # Encode the modified payload back to a JSON string and then base64url-encode it
        fake_payload = base64url_encode(json.dumps(parsed_payload, separators=(',', ':')))
        
        # Forge a token using a mix of JSON and compact serialization format to test the library's resilience
        forged_token = '{"  ' + header + '.' + fake_payload + '.":"","protected":"' + header + '", "payload":"' + payload + '","signature":"' + signature + '"}'

        # Verify that an exception is thrown when we attempt to verify the forged token
        with self.assertRaises(Exception) as context:
            jwt.verify_jwt(forged_token, generated_keys['PS256'], ['PS256'])

        # Confirm that the raised exception message is 'invalid JWT format'
        self.assertEqual(str(context.exception), 'invalid JWT format')


if __name__ == '__main__':
    unittest.main()

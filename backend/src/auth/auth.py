import json
from flask import request, _request_ctx_stack, abort
from functools import wraps
from jose import jwt
from urllib.request import urlopen

AUTH0_DOMAIN = 'coffeee.auth0.com'
ALGORITHMS = ['RS256']
API_AUDIENCE = 'coffe'

# AuthError Exception
'''
AuthError Exception
A standardized way to communicate auth failure modes
'''


class AuthError(Exception):
    def __init__(self, error, status_code):
        self.error = error
        self.status_code = status_code


# Auth Header

def get_token_auth_header():
    if 'Authorization' not in request.headers:
        raise AuthError({
            'code': 'authorization_header_missing',
            'description': 'Authorization header is expected.'
        }, 401)

    header = request.headers.get('Authorization')
    header_parts = header.split(' ')

    if len(header_parts) == 1:

        raise AuthError({
            "code": "invalid_header"
        }, 401)

    elif header_parts[0].lower() != "bearer":
        raise AuthError({
            'code': 'invalid_header',
            'description': 'Authorization header must start with "Bearer".'
        }, 401)

    return header_parts[1]


def check_permissions(permission, payload):
    if "permissions" not in payload:
        abort(400)

    if permission not in payload["permissions"]:
        abort(401)

    return True


token = "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6Ik16YzNOelpDUWpSQlJVSTBOMFExTnpjeE56QTNSRE5ETnpKR1FUWkVORFEyTWpBMk5UZzJRUSJ9.eyJpc3MiOiJodHRwczovL2NvZmZlZWUuYXV0aDAuY29tLyIsInN1YiI6Imdvb2dsZS1vYXV0aDJ8MTEwNzA4NzQyNzQzNDM1MjE4NDEzIiwiYXVkIjpbImNvZmZlIiwiaHR0cHM6Ly9jb2ZmZWVlLmF1dGgwLmNvbS91c2VyaW5mbyJdLCJpYXQiOjE1ODM2NDA3MTUsImV4cCI6MTU4MzY0NzkxNSwiYXpwIjoiNnROQW00ODJ0eWk1aE95eFVpTU0zNlhualphZjQ1VG8iLCJzY29wZSI6Im9wZW5pZCBwcm9maWxlIGVtYWlsIiwicGVybWlzc2lvbnMiOlsiZGVsZXRlOmRyaW5rcyIsImdldDpkcmlua3MtZGV0YWlsIiwicGF0Y2g6ZHJpbmtzIiwicG9zdDpkcmlua3MiXX0.D_1QPiFQayFPLpO8FyrdojBGyBo7CDXZ4Ea3A5BuBIiIFiuHmzM962vw4qjsECamYjtlxLqGQne7q9iCEvLxbyK5kDeT4v00ABuuqkw1cpa5HY2Tv13MEY6mnc1-NkVJ2Hn4970prS3l6djrrw53bdPphn9CnGIHTQimBivpjF1JUHTJKur_08Dl8W3uDRDVhPBZV3z76148h2oW0uTvQvo4B0Wd4JeG8XL3pM_sSUcYalBEGMbpru-WvLh2XJuu7dOmQxFW8Han5S6tDItL0vZ30JRZuLX8yhySfrRyOU9IzwQk5rJ-oIGensH4dM1m0gcuaevo-xfkETZqz562Aw"


def verify_decode_jwt(token):
    # GET THE PUBLIC KEY FROM AUTH0
    jsonurl = urlopen(f'https://{AUTH0_DOMAIN}/.well-known/jwks.json')
    jwks = json.loads(jsonurl.read())

    # GET THE DATA IN THE HEADER
    unverified_header = jwt.get_unverified_header(token)

    # CHOOSE OUR KEY
    rsa_key = {}
    if 'kid' not in unverified_header:
        raise AuthError({
            'code': 'invalid_header',
            'description': 'Authorization malformed.'
        }, 401)

    for key in jwks['keys']:
        if key['kid'] == unverified_header['kid']:
            rsa_key = {
                'kty': key['kty'],
                'kid': key['kid'],
                'use': key['use'],
                'n': key['n'],
                'e': key['e']
            }
    if rsa_key:
        try:
            # USE THE KEY TO VALIDATE THE JWT
            payload = jwt.decode(
                token,
                rsa_key,
                algorithms=ALGORITHMS,
                audience=API_AUDIENCE,
                issuer='https://' + AUTH0_DOMAIN + '/'
            )

            return payload

        except jwt.ExpiredSignatureError:
            raise AuthError({
                'code': 'token_expired',
                'description': 'Token expired.'
            }, 401)

        except jwt.JWTClaimsError:
            raise AuthError({
                'code': 'invalid_claims',
                'description': 'Incorrect claims. Please, check the audience and issuer.'
            }, 401)
        except Exception:
            raise AuthError({
                'code': 'invalid_header',
                'description': 'Unable to parse authentication token.'
            }, 400)
    raise AuthError({
        'code': 'invalid_header',
        'description': 'Unable to find the appropriate key.'
    }, 400)


def requires_auth(permission=''):
    def requires_auth_decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            token = get_token_auth_header()
            payload = verify_decode_jwt(token)
            check_permissions(permission, payload)
            return f(payload, *args, **kwargs)

        return wrapper

    return requires_auth_decorator

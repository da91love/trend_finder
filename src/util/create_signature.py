import hashlib
import hmac
import base64

def	create_signature(timestamp, method, uri, secret_key):
	"""
	https://github.com/naver/searchad-apidoc 참고
	:return:
	"""

	message = "{}.{}.{}".format(timestamp, method, uri)
	hash = hmac.new(bytes(secret_key, "utf-8"), bytes(message, "utf-8"), hashlib.sha256)

	hash.hexdigest()
	return base64.b64encode(hash.digest())

	return signingKey
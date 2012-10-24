import json
import constants
import request
import apysigner
from urllib import urlencode

def default_encoding(raw_data, *args):
    return urlencode(raw_data, doseq=True)

def json_encoding(raw_data, *args):
    return json.dumps(raw_data)


class SignedRequestFactory(object):

    def __init__(self, http_method, client_id, private_key, data):
        self.client_id = client_id
        self.private_key = private_key
        self.http_method = http_method
        self.raw_data = data
        self.content_type_encodings = {
            'application/json': json_encoding,
        }

    def create_request(self, url, *args, **request_kwargs):
        url = self.build_request_url(url)
        data = self._get_data_payload(request_kwargs.get("headers", {}))
        return request.Request(self.http_method, url, data, *args, **request_kwargs)

    def build_request_url(self, url):
        url = self._build_client_url(url)
        if self._is_get_request_with_data():
            url += "&{0}".format(urlencode(self.raw_data))
        return self._build_signed_url(url)

    def _build_signed_url(self, url):
        data = {} if self._is_get_request_with_data() else self.raw_data
        signature = apysigner.get_signature(self.private_key, url, data)
        signed_url = url + "&{}={}".format(constants.SIGNATURE_PARAM_NAME, signature)
        return signed_url

    def _get_data_payload(self, request_headers):
        if self.raw_data and self.http_method.lower() != 'get':
            content_type = request_headers.get("Content-Type")
            encoding_func = self.content_type_encodings.get(content_type, default_encoding)
            return encoding_func(self.raw_data)

    def _is_get_request_with_data(self):
        return self.http_method.lower() == 'get' and self.raw_data

    def _build_client_url(self, url):
        url += "?%s=%s" % (constants.CLIENT_ID_PARAM_NAME, self.client_id)
        return url

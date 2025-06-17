"""
Based on Python Request library https://docs.python-requests.org/en/latest/index.html
"""

import base64
import json
import os.path
import getpass
from requests import Session, Request
import urllib3
from http.client import HTTPConnection
from http import HTTPStatus
import urllib.parse
from functools import reduce


class AgateClient:
    """
    AgateClient holds the configuration for connecting to Agate.
    """

    def __init__(self, server=None):
        self.session = Session()
        self.headers = {}
        self.base_url = self.__ensure_entry('Agate address', server)

    def __del__(self):
        self.close()

    @classmethod
    def build(cls, loginInfo):
        return AgateClient.buildWithAuthentication(loginInfo.data['server'], loginInfo.data['user'],
                                                   loginInfo.data['password'], loginInfo.data['otp'],
                                                   loginInfo.data["no_ssl_verify"])

    @classmethod
    def buildWithAuthentication(cls, server, user, password, otp=None, no_ssl_verify: bool = False):
        client = cls(server)
        if client.base_url.startswith('https:'):
            client.session.verify = not no_ssl_verify
            if no_ssl_verify:
                urllib3.disable_warnings()

        client.credentials(user, password, otp)
        return client

    def __ensure_entry(self, text, entry, pwd=False):
        e = entry
        if not entry:
            if pwd:
                e = getpass.getpass(prompt=text + ': ')
            else:
                e = input(text + ': ')
        return e

    def credentials(self, user, password, otp):
        u = self.__ensure_entry('User name', user)
        p = self.__ensure_entry('Password', password, True)
        if otp:
            val = input("Enter 6-digits code: ")
            self.header('X-Obiba-TOTP', val)

        self.session.headers.update({"Authorization": "Basic %s" % base64.b64encode(("%s:%s" % (u, p)).encode("utf-8")).decode("utf-8")})

    def verify(self, value):
        """
        Ignore or validate certificate

        :param value = True/False to validation or not. Value can also be a CA_BUNDLE file or directory (e.g. 'verify=/etc/ssl/certs/ca-certificates.crt')
        """
        self.session.verify = value
        return self

    def header(self, key, value):
        """
        Adds a header to session headers used by the request

        :param key - header key
        :param value - header value
        """
        header = {}
        header[key] = value

        self.session.headers.update(header)
        return self

    def new_request(self):
        return AgateRequest(self)

    def close(self):
        """
        Closes client session and request to close Agate server session
        """
        try:
            self.new_request().resource("/auth/session/_current").delete().send()
            self.session.close()
        except Exception as e:
            pass

    class LoginInfo:
        data = None

        @classmethod
        def parse(cls, args):
            data = {}
            argv = vars(args)

            data["no_ssl_verify"] = argv.get("no_ssl_verify")

            if argv.get('agate'):
                data['server'] = argv['agate']
            else:
                raise Exception('Agate server information is missing.')

            if argv.get('user') and argv.get('password'):
                data["user"] = argv["user"]
                data["password"] = argv["password"]
                data["otp"] = argv["otp"]
            else:
                raise Exception('Invalid login information. Requires user-password or certificate-key information')

            setattr(cls, 'data', data)
            return cls()

        def isSsl(self):
            if self.data.keys() & {'cert', 'key'}:
                return True
            return False


class AgateRequest:
    """
    Agate request.
    """

    def __init__(self, agate_client):
        self.client = agate_client
        self.options = {}
        self.headers = {'Accept': 'application/json'}
        self.params = {}
        self._fail_on_error = False
        self.files = None
        self.data = None


    def timeout(self, value):
        """
        Sets the connection and read timeout
        Note: value can be a tupple to have different timeouts for connection and reading (connTimout, readTimeout)

        :param value - connection/read timout
        """
        self.options["timeout"] = value
        return self

    def verbose(self):
        """
        Enables the verbose mode
        """
        HTTPConnection.debuglevel = 1
        self._verbose = True
        return self

    def fail_on_error(self):
        self._fail_on_error = True
        return self

    def header(self, key, value):
        """
        Adds a header to session headers used by the request

        :param key - header key
        :param value - header value
        """
        if value:
            header = {}
            header[key] = value
            self.headers.update(header)
        return self

    def accept(self, value):
        self.headers.update({"Accept": value})
        return self

    def content_type(self, value):
        return self.accept("application/json")

    def accept_json(self):
        return self.accept('application/json')

    def content_type_json(self):
        return self.content_type('application/json')

    def method(self, method):
        """
        Sets a HTTP method

        :param method - any of ['GET', 'DELETE', 'PUT', 'POST', 'OPTIONS']
        """
        if not method:
            self.method = "GET"
        elif method in ["GET", "DELETE", "PUT", "POST", "OPTIONS"]:
            self.method = method
        else:
            raise ValueError("Not a valid method: " + method)
        return self

    def get(self):
        return self.method('GET')

    def put(self):
        return self.method('PUT')

    def post(self):
        return self.method('POST')

    def delete(self):
        return self.method('DELETE')

    def options(self):
        return self.method('OPTIONS')

    def __build_request(self):
        """
        Builder method creating a Request object to be sent by the client session object
        """
        request = Request()
        request.method = self.method if self.method else "GET"

        for option in self.options:
            setattr(request, option, self.options[option])

        # Combine the client and the request headers
        request.headers = {}
        request.headers.update(self.client.session.headers)
        request.headers.update(self.headers)

        if self.resource:
            path = self.resource
            request.url = self.client.base_url + "/ws" + path

            if self.params:
                request.params = self.params
        else:
            raise ValueError("Resource is missing")

        if self.files is not None:
            request.files = self.files

        if self.data is not None:
            request.data = self.data

        return request


    def resource(self, ws):
        self.resource = ws
        return self

    def form(self, parameters):
        """
        Stores the request's body as a form
        Note: no need to transform parameters in key=value pairs

        :param parametes - parameters as a dict value
        """
        return self.content(parameters)

    def content(self, content):
        """
        Stores the request body

        :param content - request body
        """
        if self._verbose:
            print("* Content:")
            print(content)

        self.data = content
        return self


    def content_upload(self, filename):
        """
        Sets the file associate with the upload

        Note: Requests library takes care of mutlti-part setting in the header
        """
        if self._verbose:
            print("* File Content:")
            print("[file=" + filename + ", size=" + str(os.path.getsize(filename)) + "]")
        self.files = {"file": (filename, open(filename, "rb"))}
        return self

    def send(self):
        """
        Sends the request via client session object
        """
        request = self.__build_request()
        response = AgateResponse(self.client.session.send(request.prepare()))

        if self._fail_on_error and response.code >= 400:
            raise HTTPError(response)

        return response


class Storage:
    """
    Content storage.
    """

    def __init__(self):
        self.content = ''
        self.line = 0

    def store(self, buf):
        self.line = self.line + 1
        self.content = self.content + buf.decode("utf-8")

    def __str__(self):
        return self.contents


class HeaderStorage(Storage):
    """
    Store response headers in a dictionary: key is the header name,
    value is header value or the list of header values.
    """

    def __init__(self):
        Storage.__init__(self)
        self.headers = {}

    def store(self, buf):
        Storage.store(self, buf)
        header = buf.decode("utf-8").partition(':')
        if header[1]:
            value = header[2].rstrip().strip()
            if header[0] in self.headers:
                current_value = self.headers[header[0]]
                if isinstance(current_value, str):
                    self.headers[header[0]] = [current_value]
                self.headers[header[0]].append(value)
            else:
                self.headers[header[0]] = value


class AgateResponse:
    """
    Response from Agate: code, headers and content
    """

    def __init__(self, response):
        self.response = response

    @property
    def code(self):
        return self.response.status_code

    @property
    def headers(self):
        return self.response.headers

    @property
    def content(self):
        return self.response.content

    @property
    def version(self):
        return self.headers.get("X-Agate-Version", None)

    @property
    def version_info(self):
        agateVersion = self.version
        if agateVersion is not None:
            info = {}
            [info["major"], info["minor"], info["patch"]] = self.version.split(".")
            return info
        return None

    def as_json(self):
        """
        Returns response body as a JSON document
        """
        if self.response is None or self.response.content is None:
            return None

        try:
            return self.response.json()
        except Exception as e:
            if type(self.response.content) == str:
                return self.response.content
            else:
                # FIXME silently fail
                return None

    def pretty_json(self):
        """
        Beatifies the JSON response
        """
        return json.dumps(self.as_json(), sort_keys=True, indent=2)


class UriBuilder:
    """
    Build a valid Uri.
    """

    def __init__(self, path=[], params={}):
        self.path = path
        self.params = params

    def path(self, path):
        self.path = path
        return self

    def segment(self, seg):
        self.path.append(seg)
        return self

    def params(self, params):
        self.params = params
        return self

    def query(self, key, value):
        self.params.update([(key, value),])
        return self

    def __str__(self):
        def concat_segment(p, s):
            return p + '/' + s

        def concat_params(k):
            return urllib.parse.quote(k) + '=' + urllib.parse.quote(str(self.params[k]))

        def concat_query(q, p):
            return q + '&' + p

        p = urllib.parse.quote('/' + reduce(concat_segment, self.path))
        if len(self.params):
            q = reduce(concat_query, list(map(concat_params, list(self.params.keys()))))
            return p + '?' + q
        else:
            return p

    def build(self):
        return self.__str__()

class HTTPError(Exception):
    """
    HTTP related error class
    """

    def __init__(self, response: AgateResponse, message: str = None):
        # Call the base class constructor with the parameters it needs
        super().__init__(message if message else "HTTP Error: %s" % response.code)
        self.code = response.code
        http_status = [x for x in list(HTTPStatus) if x.value == response.code][0]
        self.message = message if message else "%s: %s" % (http_status.phrase, http_status.description)
        self.error = response.as_json() if response.content else {"code": response.code, "status": self.message}
        # case the reported error is not a dict
        if type(self.error) != dict:
            self.error = {"code": response.code, "status": self.error}

    def is_client_error(self) -> bool:
        return self.code >= 400 and self.code < 500

    def is_server_error(self) -> bool:
        return self.code >= 500
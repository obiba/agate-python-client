from argparse import Namespace
import unittest
from obiba_agate.core import AgateClient
from os.path import exists


class AgateClientTestSSLConnection(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        setattr(cls, 'SERVER', 'https://agate-demo.obiba.org')
        # Make sure to place your own certificate files
        setattr(cls, 'SSL_CERTIFICATE', '../../resources/certificates/publickey.pem')
        setattr(cls, 'SSL_KEY', '../../resources/certificates/privatekey.pem')

    def test_sendRestBadServer(self):
        client = AgateClient.buildWithAuthentication(server='http://deadbeef:8081', user='administrator',
                                                    password='password')

        self.assertRaises(Exception, self.__sendSimpleRequest, client.new_request())

    def test_sendRestBadCredentials(self):
        client = AgateClient.buildWithAuthentication(server=self.SERVER, user='admin',
                                                    password='password')

        self.assertRaises(Exception, self.__sendSimpleRequest, client.new_request())

    def test_sendRest(self):
        try:
            client = AgateClient.buildWithAuthentication(server=self.SERVER, user='administrator',
                                                        password='password', no_ssl_verify=True)
            self.__sendSimpleRequest(client.new_request())
        except Exception as e:
            self.fail(e)

    def test_sendSecuredRest(self):
        try:
            client = AgateClient.buildWithAuthentication(server=self.SERVER,
                                                        user='administrator',
                                                        password='password')
            # place a valid CRT to verify the SERVER SSL certificate
            #client.verify('<PATH_TO_YOUR_CRT>')
            self.__sendSimpleRequest(client.new_request())
        except Exception as e:
            self.fail(e)

    def test_validAuthLoginInfo(self):
        try:
            args = Namespace(agate=self.SERVER, user='administrator', password='password', otp=None)
            client = AgateClient.build(loginInfo=AgateClient.LoginInfo.parse(args))
            self.__sendSimpleRequest(client.new_request())
        except Exception as e:
            self.fail(e)

    def test_validSslLoginInfo(self):
        if exists(self.SSL_CERTIFICATE):
            try:
                args = Namespace(agate=self.SERVER, ssl_cert=self.SSL_CERTIFICATE,
                                ssl_key=self.SSL_KEY)
                client = AgateClient.build(loginInfo=AgateClient.LoginInfo.parse(args))
                self.__sendSimpleRequest(client.new_request())
            except Exception as e:
                self.fail(e)

    def test_invalidServerInfo(self):
        args = Namespace(opl=self.SERVER, user='administrator', password='password')
        self.assertRaises(Exception, AgateClient.LoginInfo.parse, args);

    def test_invalidLoginInfo(self):
        args = Namespace(agate=self.SERVER, usr='administrator', password='password')
        self.assertRaises(Exception, AgateClient.LoginInfo.parse, args);

    def __sendSimpleRequest(self, request):
        request.fail_on_error()
        request.accept_json()
        # uncomment for debugging
        # request.verbose()

        # send request
        request.method('GET').resource('/users')
        response = request.send()

        # format response
        res = response.content

        # output to stdout
        print(res)


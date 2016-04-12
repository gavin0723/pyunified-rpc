# encoding=utf8

""" The web adapter test
    Author: lipixun
    Created Time : 五  4/ 8 18:23:03 2016

    File Name: test_web.py
    Description:

"""

import json
import urllib

import mime

from webtest import TestApp

from unifiedrpc import endpoint, context, Service, Server, \
    CONFIG_RESPONSE_CONTENT_CONTAINER, CONFIG_RESPONSE_MIMETYPE
from unifiedrpc.helpers import paramtype
from unifiedrpc.paramtypes import boolean
from unifiedrpc.adapters.web import get, post, put, delete, head, patch, options, WebAdapter
from unifiedrpc.content.container import APIContentContainer

def test_web_basic():
    """The web basic test
    """
    class TestService(Service):
        """The test service
        """
        @get('/test/get')
        @post('/test/post')
        @put('/test/put')
        @delete('/test/delete')
        @head('/test/head')
        @patch('/test/patch')
        @options('/test/options')
        @endpoint()
        def test(self):
            """Test
            """
            return 'OK'

        @get('/test2')
        @endpoint()
        def test2(self, param):
            """Test 2
            """
            return 'OK'

    adapter = WebAdapter()
    server = Server([ TestService() ], [ adapter ])
    server.start()
    # Test
    app = TestApp(adapter)
    rsp = app.get('/test', expect_errors = True)
    assert rsp.status_int == 404
    rsp = app.get('/test/get')
    assert rsp.status_int == 200 and rsp.content_type == 'text/plain' and rsp.text == 'OK'
    rsp = app.post('/test/post')
    assert rsp.status_int == 200 and rsp.content_type == 'text/plain' and rsp.text == 'OK'
    rsp = app.put('/test/put')
    assert rsp.status_int == 200 and rsp.content_type == 'text/plain' and rsp.text == 'OK'
    rsp = app.delete('/test/delete')
    assert rsp.status_int == 200 and rsp.content_type == 'text/plain' and rsp.text == 'OK'
    rsp = app.head('/test/head')
    assert rsp.status_int == 200 and rsp.content_type == 'text/plain'
    rsp = app.patch('/test/patch')
    assert rsp.status_int == 200 and rsp.content_type == 'text/plain' and rsp.text == 'OK'
    rsp = app.options('/test/options')
    assert rsp.status_int == 200 and rsp.content_type == 'text/plain' and rsp.text == 'OK'
    # Too many parameters
    rsp = app.get('/test/get?a=1', expect_errors = True)
    assert rsp.status_int == 400
    # Lack of parameters
    rsp = app.get('/test2', expect_errors = True)
    assert rsp.status_int == 400
    rsp = app.get('/test2?param=1')
    assert rsp.status_int == 200 and rsp.text == 'OK'

def test_web_api_container():
    """The web api container test
    """
    class TestService(Service):
        """The test service
        """
        @get('/test')
        @endpoint()
        def test(self):
            """Test
            """
            return { 'key': 'value' }

    adapter = WebAdapter()
    server = Server([ TestService() ], [ adapter ], {
        CONFIG_RESPONSE_CONTENT_CONTAINER: APIContentContainer,
        CONFIG_RESPONSE_MIMETYPE: mime.APPLICATION_JSON,
        })
    server.start()
    # Test
    app = TestApp(adapter)
    rsp = app.get('/test')
    value = json.loads(rsp.text)
    assert rsp.status_int == 200 and rsp.content_type == mime.APPLICATION_JSON and value and len(value) == 1 and \
        value.get('value') and len(value['value']) == 1 and value['value']['key'] == 'value'

def test_web_parameter_conversation():
    """The web parameter conversation
    """
    class TestService(Service):
        """The test service
        """
        @paramtype(number = int, boolValue = boolean)
        @get('/test')
        @endpoint()
        def test(self, number, boolValue):
            """Test
            """
            return { 'number': number, 'boolValue': boolValue }

    adapter = WebAdapter()
    server = Server([ TestService() ], [ adapter ], {
        CONFIG_RESPONSE_CONTENT_CONTAINER: APIContentContainer,
        CONFIG_RESPONSE_MIMETYPE: mime.APPLICATION_JSON,
        })
    server.start()
    # Test
    app = TestApp(adapter)
    rsp = app.get('/test?number=1&boolValue=true')
    value = json.loads(rsp.text)
    assert rsp.status_int == 200 and value['value']['number'] == 1 and value['value']['boolValue']
    rsp = app.get('/test?number=10&boolValue=false')
    value = json.loads(rsp.text)
    assert rsp.status_int == 200 and value['value']['number'] == 10 and not value['value']['boolValue']
    # Wrong type
    rsp = app.get('/test?number=asdf&boolValue=false', expect_errors = True)
    value = json.loads(rsp.text)
    assert rsp.status_int == 400

def test_web_content_text():
    """Test web request with text content
    """
    class TestService(Service):
        """The test service
        """
        @post('/test')
        @endpoint()
        def test(self):
            """Test
            """
            assert context.request.content.mimeType == 'text/plain'
            return context.request.content.data

    adapter = WebAdapter()
    server = Server([ TestService() ], [ adapter ], {
        CONFIG_RESPONSE_CONTENT_CONTAINER: APIContentContainer,
        CONFIG_RESPONSE_MIMETYPE: mime.APPLICATION_JSON,
        })
    server.start()
    app = TestApp(adapter)
    # Send request
    rsp = app.post('/test', params = 'thisisatestcontent', content_type = 'text/plain')
    value = json.loads(rsp.text)
    assert rsp.status_int == 200 and value['value'] == 'thisisatestcontent'

def test_web_content_json():
    """Test web request with json content
    """
    class TestService(Service):
        """The test service
        """
        @post('/test')
        @endpoint()
        def test(self):
            """Test
            """
            assert context.request.content.mimeType == mime.APPLICATION_JSON
            return context.request.content.data

    adapter = WebAdapter()
    server = Server([ TestService() ], [ adapter ], {
        CONFIG_RESPONSE_CONTENT_CONTAINER: APIContentContainer,
        CONFIG_RESPONSE_MIMETYPE: mime.APPLICATION_JSON,
        })
    server.start()
    app = TestApp(adapter)
    # Send request
    rsp = app.post('/test', params = json.dumps({ 'key': 'value' }), content_type = mime.APPLICATION_JSON)
    value = json.loads(rsp.text)
    assert rsp.status_int == 200 and value['value'] == { 'key': 'value' }

def test_web_content_form():
    """Test web request with form content
    """
    class TestService(Service):
        """The test service
        """
        @post('/test')
        @endpoint()
        def test(self):
            """Test
            """
            assert context.request.content.mimeType == mime.APPLICATION_X_WWW_FORM_URLENCODED
            return context.request.content.data

    adapter = WebAdapter()
    server = Server([ TestService() ], [ adapter ], {
        CONFIG_RESPONSE_CONTENT_CONTAINER: APIContentContainer,
        CONFIG_RESPONSE_MIMETYPE: mime.APPLICATION_JSON,
        })
    server.start()
    app = TestApp(adapter)
    # Send request
    rsp = app.post('/test', params = urllib.urlencode({ 'key': 'value' }), content_type = mime.APPLICATION_X_WWW_FORM_URLENCODED)
    value = json.loads(rsp.text)
    assert rsp.status_int == 200 and value['value'] == { 'key': [ 'value' ] }

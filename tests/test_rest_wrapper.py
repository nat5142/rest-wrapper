"""Tests for `rest_wrapper` module."""
from typing import Generator
from unittest import mock

import pytest

import rest_wrapper


@pytest.fixture
def version() -> Generator[str, None, None]:
    """Sample pytest fixture."""
    yield rest_wrapper.__version__


def test_version(version: str) -> None:
    """Sample pytest test function with the pytest fixture as an argument."""
    assert version == "0.0.2"


class MockResponse:
    
    def __init__(self, json_data=None, content=None, status_code=204, *args, **kwargs):
        self.content = content
        self.json_data = json_data
        self.status_code = status_code

    def json(self):
        return self.json_data
    

def mock_get(*args, **kwargs):
    if args[0].build_url(args[1]) == 'https://example.com/users':
        return MockResponse(
            json_data=[{'id': 1, 'name': 'bob'}, {'id': 2, 'name': 'greg'}, {'id': 3, 'name': 'sally'}, {'id': 4, 'name': 'amanda'}], 
            status_code=200
        )
    if args[1] in ['users/1']:
        return MockResponse(
            json_data={'id': 1, 'name': 'bob'},
            status_code=200
        )
    
    return MockResponse(None, 404)


def mock_post(*args, **kwargs):
    data = kwargs.get('json') or kwargs.get('data') or {}
    if not data:
        return MockResponse(
            json_data=None,
            status_code=400
        )
    
    return MockResponse(
        json_data={'id': 5, **data},
        status_code=201
    )


def mock_patch(*args, **kwargs):
    data = kwargs.get('json') or kwargs.get('data') or {}
    if not data:
        return MockResponse(
            json_data=None,
            status_code=400
        )
    
    obj_id = args[1].split('/')[-1]
    return MockResponse(
        json_data={'id': int(obj_id), **data},
        status_code=200
    )


def mock_put(*args, **kwargs):
    data = kwargs.get('json') or kwargs.get('data') or {}
    if not data:
        return MockResponse(
            json_data=None,
            status_code=400
        )
    
    obj_id = args[1].split('/')[-1]
    return MockResponse(
        json_data={'id': int(obj_id), **data},
        status_code=200
    )


def mock_delete(*args, **kwargs):
    return MockResponse(status_code=204)


def mock_head(*args, **kwargs):
    return MockResponse(
        content='Some content',
        status_code=200
    )


def mock_options(*args, **kwargs):
    return MockResponse(
        content='Some content',
        status_code=200
    )


class TestRestClient(object):

    @mock.patch('rest_wrapper.RestClient.get', mock_get)
    def test_get_requests(self):
        client = rest_wrapper.RestClient('https://example.com/')
        users = client.get('users')
        assert users.status_code == 200
        user_1 = client.get('users/1')
        assert user_1.status_code == 200
        assert user_1.json_data == {'id': 1, 'name': 'bob'}
    
    @mock.patch('rest_wrapper.RestClient.post', mock_post)
    def test_post_request(self):
        client = rest_wrapper.RestClient('https://example.com/')
        resp = client.post('users', json={'name': 'julius'})
        assert resp.json_data == {'id': 5, 'name': 'julius'}
        assert resp.status_code == 201
    
    @mock.patch('rest_wrapper.RestClient.patch', mock_patch)
    def test_patch_request(self):
        client = rest_wrapper.RestClient('https://example.com/')
        resp = client.patch('users/5', json={'name': 'barbara'})
        assert resp.json_data == {'id': 5, 'name': 'barbara'}
        assert resp.status_code == 200
    
    @mock.patch('rest_wrapper.RestClient.put', mock_put)
    def test_put_request(self):
        client = rest_wrapper.RestClient('https://example.com/')
        resp = client.put('users/5', json={'name': 'barbara'})
        assert resp.json_data == {'id': 5, 'name': 'barbara'}
        assert resp.status_code == 200

    @mock.patch('rest_wrapper.RestClient.delete', mock_delete)
    def test_delete_request(self):
        client = rest_wrapper.RestClient('https://example.com/')
        resp = client.delete('users/5')
        assert resp.status_code == 204
    
    @mock.patch('rest_wrapper.RestClient.head', mock_head)
    def test_head_request(self):
        client = rest_wrapper.RestClient('https://example.com/')
        resp = client.head('users')
        assert resp.status_code == 200
        assert resp.content == 'Some content'

    @mock.patch('rest_wrapper.RestClient.options', mock_options)
    def test_options_request(self):
        client = rest_wrapper.RestClient('https://example.com/')
        resp = client.options('users')
        assert resp.status_code == 200
        assert resp.content == 'Some content'

    def test_build_url(self):
        client = rest_wrapper.RestClient('https://example.com')
        test = client.build_url('users/1')
        assert test == 'https://example.com/users/1'
        test = client.build_url('/users/1')
        assert test == 'https://example.com/users/1'
        test = client.build_url('users/1/')
        assert test == 'https://example.com/users/1/'
        test = client.build_url('users/all.json')
        assert test == 'https://example.com/users/all.json'

    def test_get_real_url(self):
        client = rest_wrapper.RestClient('https://example.com')
        resp = client.get('https://www.google.com/search?q=cats', append_url=False)
        assert resp.status_code == 200

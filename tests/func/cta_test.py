#! /usr/bin/env python3

# standard library
import datetime
import json
import os

# testing libraries
import pytest
from falcon import testing
import falcon

# internal import
import backend.app

# json files for test
CTA_TEST_DIR = 'tests/cta-fake-response-json/'
CTA_SUCCESS_JSON_RESP = (
    os.path.join(CTA_TEST_DIR, 'cta_success_fake_response.json')
)
CTA_ERROR_INCORRECT_STOP_JSON_RESP = (
    os.path.join(CTA_TEST_DIR, 'cta_error_incorrect_stop_response.json')
)
CTA_ERROR_UNKNOWN_TYPE_JSON_RESP = (
    os.path.join(CTA_TEST_DIR, 'cta_error_unknown_type_response.json')
)
CTA_ERROR_UNSUPPORTED_FUNC_JSON_RESP = (
    os.path.join(CTA_TEST_DIR, 'cta_error_unsupported_function_response.json')
)


# data loading fixtures
@pytest.fixture(scope='session')
def success_response():
    with open(CTA_SUCCESS_JSON_RESP, 'r') as f:
        data = json.load(f)
    return data


@pytest.fixture(scope='session')
def error_incorrect_stop():
    with open(CTA_ERROR_INCORRECT_STOP_JSON_RESP, 'r') as f:
        data = json.load(f)
    return data


@pytest.fixture(scope='session')
def error_unknown_type():
    with open(CTA_ERROR_UNKNOWN_TYPE_JSON_RESP, 'r') as f:
        data = json.load(f)
    return data


@pytest.fixture(scope='session')
def error_unsupported_func():
    with open(CTA_ERROR_UNSUPPORTED_FUNC_JSON_RESP, 'r') as f:
        data = json.load(f)
    return data
    

@pytest.fixture()
def client():
    """Create instance of Falcon testing client
    """
    api = backend.app.create_app()
    return testing.TestClient(api)


def test_get_successful_response(client, mocker, success_response):
    # Arrange
    mock_datetime = mocker.patch.object(backend.cta, 'datetime')
    mock_datetime.datetime.now.return_value = (
        datetime.datetime(2017, 11, 14, 15, 56)
    )

    get_mock = mocker.MagicMock()
    get_mock.json.return_value = success_response
    get_mock.status_code = 200
    request_mock = mocker.patch.object(
        backend.cta.requests,
        'get',
        return_value=get_mock,
    )

    # Act
    response = client.simulate_get('/stops/1066')

    # Assert
    upcoming_buses = response.json['result']
    assert response.status == falcon.HTTP_200
    assert len(upcoming_buses) == 4
    assert upcoming_buses[0] == {'bus': '146', 'min_away': 3}
    assert upcoming_buses[1] == {'bus': '151', 'min_away': 10}

    args, kwargs = request_mock.call_args
    params = kwargs['params'].items()
    assert request_mock.call_count == 1
    assert ('stpid', '1066') in params
    assert ('format', 'json') in params


def test_404(client, mocker):
    # Arrange
    get_mock = mocker.MagicMock()
    get_mock.status_code = 404
    mocker.patch.object(
        backend.cta.requests,
        'get',
        return_value=get_mock,
    )

    # Act
    response = client.simulate_get('/stops/1066')

    # Assert
    assert response.status == falcon.HTTP_200
    assert response.json == {'error': 'Request returned 404'}


def test_url_not_found(client, mocker):
    # Arrange
    mocker.patch.object(
        backend.cta.requests,
        'get',
        side_effect=[ConnectionError]
    )

    # Act
    response = client.simulate_get('/stops/1066')

    # Assert
    assert response.status == falcon.HTTP_200
    assert response.json == {'error': 'URL not found'}


def test_wrong_stop(client, mocker, error_incorrect_stop):
    # Arrange
    get_mock = mocker.MagicMock()
    get_mock.status_code = 200
    get_mock.json.return_value = error_incorrect_stop
    mocker.patch.object(
        backend.cta.requests,
        'get',
        return_value=get_mock,
    )

    # Act
    response = client.simulate_get('/stops/106')

    # Assert
    assert response.status == falcon.HTTP_200
    assert response.json == {'error': 'stop_id: 106 does not exist'}

def test_unsupported_function(client, mocker, error_unsupported_func):
    # Arrange
    get_mock = mocker.MagicMock()
    get_mock.status_code = 200
    get_mock.json.return_value = error_unsupported_func
    mocker.patch.object(
        backend.cta.requests,
        'get',
        return_value=get_mock,
    )

    # Act
    response = client.simulate_get('/stops/1066')

    # Assert
    assert response.status == falcon.HTTP_200
    assert response.json == {
        'error': "Unknown error: {'msg': 'Unsupported function'}"
    }


def test_unknown_response_type(client, mocker, error_unknown_type):
    # Arrange
    get_mock = mocker.MagicMock()
    get_mock.status_code = 200
    get_mock.json.return_value = error_unknown_type
    mocker.patch.object(
        backend.cta.requests,
        'get',
        return_value=get_mock,
    )

    # Act
    response = client.simulate_get('/stops/1066')

    # Assert
    assert response.status == falcon.HTTP_200
    assert response.json == {
        'error': "Unexpected response type: {'foo': [{'msg': 'Unknown error'}]}"
    }


def test_not_implemented(client):
    response = client.simulate_post('/stops/1066')
    assert response.status == falcon.HTTP_METHOD_NOT_ALLOWED

    response = client.simulate_put('/stops/1066')
    assert response.status == falcon.HTTP_METHOD_NOT_ALLOWED

    response = client.simulate_patch('/stops/1066')
    assert response.status == falcon.HTTP_METHOD_NOT_ALLOWED

    response = client.simulate_delete('/stops/1066')
    assert response.status == falcon.HTTP_METHOD_NOT_ALLOWED

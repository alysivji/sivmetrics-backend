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

# set up fake response file paths
CTA_TEST_DIR = 'tests/cta-fake-response-json/'
CTA_SUCCESS_RESP = os.path.join(CTA_TEST_DIR, 'cta_success_fake_response.json')
CTA_ERROR_INCORRECT_STOP_RESP = os.path.join(CTA_TEST_DIR, 'cta_error_incorrect_stop_response.json')
CTA_ERROR_UNSUPPORTED_FUNC_RESP = (
    os.path.join(CTA_TEST_DIR, 'cta_error_unsupported_function_response.json')
)
# load data from fake reponse files
with open(CTA_SUCCESS_RESP, 'r') as f:
    CTA_SUCCESS_RESPONSE = json.load(f)
with open(CTA_ERROR_INCORRECT_STOP_RESP, 'r') as f:
    CTA_ERROR_INCORRECT_REPONSE = json.load(f)
with open(CTA_ERROR_UNSUPPORTED_FUNC_RESP, 'r') as f:
    CTA_ERROR_UNSUPPORTED_FUNCTION_RESPONSE = json.load(f)


def __fake_data(response_type):
    """Send fake data to mock object
    """
    if response_type == 'success_response':
        return CTA_SUCCESS_RESPONSE

    if response_type == 'wrong_stop':
        return CTA_ERROR_INCORRECT_REPONSE

    if response_type == 'unsupported_function_error':
        return CTA_ERROR_UNSUPPORTED_FUNCTION_RESPONSE

    raise Exception


@pytest.fixture()
def client():
    """Create instance of Falcon testing client
    """
    api = backend.app.create_app()
    return testing.TestClient(api)


def test_get_successful_response(client, mocker):
    # Arrange
    mock_datetime = mocker.patch.object(backend.cta, 'datetime')
    mock_datetime.datetime.now.return_value = (
        datetime.datetime(2017, 11, 14, 15, 56)
    )

    get_mock = mocker.MagicMock()
    get_mock.json.return_value = __fake_data('success_response')
    get_mock.status_code = 200
    request_mock = mocker.patch.object(
        backend.cta.requests,
        'get',
        return_value=get_mock,
    )

    # Act
    response = client.simulate_get('/stops/1066')

    # Assert
    assert response.status == falcon.HTTP_200
    assert len(response.json) == 4
    assert response.json[0] == {'bus': '146', 'min_away': 3}
    assert response.json[1] == {'bus': '151', 'min_away': 10}

    args, kwargs = request_mock.call_args
    params = kwargs['params'].items()
    assert request_mock.call_count == 1
    assert ('stpid', '1066') in params
    assert ('format', 'json') in params


def test_404(client, mocker):
    # Arrange
    get_mock = mocker.MagicMock()
    get_mock.status_code.return_value = 404
    mocker.patch.object(
        backend.cta.requests,
        'get',
        return_value=get_mock,
    )

    # Act
    response = client.simulate_get('/')

    # Assert
    assert response.status == falcon.HTTP_404

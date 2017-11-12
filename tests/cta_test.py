#! /usr/bin/env python3

# testing libraries
import pytest
from falcon import testing

# internal imports
import backend.app
import datetime
import falcon


def fake_data():
    return {'bustime-response': {'prd': [{'des': 'Union Station',
                                          'dly': False,
                                          'dstp': 472,
                                          'prdctdn': 'DUE',
                                          'prdtm': '20171111 21:58',
                                          'rt': '151',
                                          'rtdd': '151',
                                          'rtdir': 'Southbound',
                                          'stpid': '1066',
                                          'stpnm': 'Lake Shore & Stratford',
                                          'tablockid': '151 -512',
                                          'tatripid': '125',
                                          'tmstmp': '20171111 21:57',
                                          'typ': 'A',
                                          'vid': '4129',
                                          'zone': ''},
                                         {'des': 'Museum Campus',
                                          'dly': False,
                                          'dstp': 1606,
                                          'prdctdn': '2',
                                          'prdtm': '20171111 22:00',
                                          'rt': '146',
                                          'rtdd': '146',
                                          'rtdir': 'Southbound',
                                          'stpid': '1066',
                                          'stpnm': 'Lake Shore & Stratford',
                                          'tablockid': '146 -554',
                                          'tatripid': '2701',
                                          'tmstmp': '20171111 21:57',
                                          'typ': 'A',
                                          'vid': '4134',
                                          'zone': ''}]}}


@pytest.fixture()
def client():
    api = backend.app.create_app()
    return testing.TestClient(api)


def test_get_successful_response(client, mocker):
    # Arrange
    mock_datetime = mocker.patch.object(backend.cta, 'datetime')
    mock_datetime.datetime.now.return_value = (
        datetime.datetime(2017, 11, 11, 21, 57)
    )

    response_mock = mocker.MagicMock()
    response_mock.json.return_value = fake_data()
    mocker.patch.object(
        backend.cta.requests,
        'get',
        return_value=response_mock,
    )

    # Act
    response = client.simulate_get('/stops/1066')

    # Assert
    assert response.status == falcon.HTTP_200
    assert len(response.json) == 2
    assert response.json[0] == {'bus': '151', 'min_away': 1}
    assert response.json[1] == {'bus': '146', 'min_away': 3}

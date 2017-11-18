#! /usr/bin/env python3

import json

import pytest


@pytest.fixture
def json_loader():
    """
    Loads data from JSON file
    """

    def _loader(filename):
        with open(filename, 'r') as f:
            print(filename)
            data = json.load(f)
        return data

    return _loader

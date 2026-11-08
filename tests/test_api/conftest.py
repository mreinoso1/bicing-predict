import os

os.environ["API_TOKEN"] = "test"

import pytest


@pytest.fixture
def token():
    return {"Token" : "test"}
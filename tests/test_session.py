from chaos_lambda import SessionWithDelay
from unittest.mock import patch
from io import StringIO
import unittest
import warnings
import pytest
import logging


def ignore_warnings(test_func):
    def do_test(self, *args, **kwargs):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", ResourceWarning)
            warnings.simplefilter("ignore", DeprecationWarning)
            test_func(self, *args, **kwargs)
    return do_test


def session_request_with_delay():
    session = SessionWithDelay(delay=300)
    session.get('https://stackoverflow.com/')
    pass


class TestSessionMethods(unittest.TestCase):

    @pytest.fixture(autouse=True)
    def inject_fixtures(self, caplog):
        self._caplog = caplog

    @ignore_warnings
    def test_get_statuscode_arg(self):
        with self._caplog.at_level(logging.DEBUG, logger="chaos_lambda"):
            session_request_with_delay()
            assert (
                'Added 300.00ms of delay to GET' in self._caplog.text
            )


if __name__ == '__main__':
    unittest.main()

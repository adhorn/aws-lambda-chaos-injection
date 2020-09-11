from chaos_lambda import SessionWithDelay
from . import TestBase, ignore_warnings
import unittest
import pytest
import logging


def session_request_with_delay():
    session = SessionWithDelay(delay=300)
    session.get('https://stackoverflow.com/')
    pass


class TestSessionMethods(TestBase):

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

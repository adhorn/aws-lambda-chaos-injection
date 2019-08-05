from chaos_lambda import SessionWithDelay
from unittest.mock import patch
from io import StringIO
import unittest
import warnings


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

    @ignore_warnings
    def test_get_statuscode_arg(self):
        with patch('sys.stdout', new=StringIO()) as fakeOutput:
            session_request_with_delay()
            assert (
                'Added 300.00ms of delay to GET' in fakeOutput.getvalue().strip()
            )


if __name__ == '__main__':
    unittest.main()

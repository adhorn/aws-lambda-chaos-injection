from failure_injection import get_config
from ssm_cache import InvalidParameterError
import unittest
import os
import warnings
import boto3

client = boto3.client('ssm', region_name='eu-north-1')


def ignore_warnings(test_func):
    def do_test(self, *args, **kwargs):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", ResourceWarning)
            warnings.simplefilter("ignore", DeprecationWarning)
            test_func(self, *args, **kwargs)
    return do_test


class TestStringMethods(unittest.TestCase):

    @ignore_warnings
    def setUp(self):
        os.environ['FAILURE_INJECTION_PARAM'] = 'test.config'
        client.put_parameter(
            Value="{ \"delay\": 200, \"isEnabled\": true, \"error_code\": 404, \"exception_msg\": \"I FAILED\", \"rate\": 0.5 }",
            Name='test.config',
            Type='String',
            Overwrite=True
        )

    @ignore_warnings
    def tearDown(self):
        client.delete_parameters(Names=['test.config'])

    @ignore_warnings
    def test_get_config(self):
        isEnabled, rate = get_config('isEnabled')
        self.assertEqual(isEnabled, True or False)
        self.assertEqual(rate, 0.5)

    @ignore_warnings
    def test_get_config_delay(self):
        delay, rate = get_config('delay')
        self.assertEqual(delay, 200)
        self.assertEqual(rate, 0.5)


    @ignore_warnings
    def test_get_config_error_code(self):
        delay, rate = get_config('error_code')
        self.assertEqual(delay, 404)
        self.assertEqual(rate, 0.5)


    @ignore_warnings
    def test_get_config_bad_key(self):
        with self.assertRaises(KeyError):
            get_config('dela')

    @ignore_warnings
    def test_get_config_bad_config(self):
        os.environ['FAILURE_INJECTION_PARAM'] = 'test.conf'
        with self.assertRaises(InvalidParameterError):
            get_config('delay')




if __name__ == '__main__':
    unittest.main()

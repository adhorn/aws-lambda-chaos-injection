from chaos_lambda import get_config
from ssm_cache import InvalidParameterError
from . import TestBase, ignore_warnings
import unittest
import os


class TestConfigMethods(TestBase):

    @ignore_warnings
    def setUp(self):
        os.environ['CHAOS_PARAM'] = 'test.config'
        self.ssm_client.put_parameter(
            Value="{ \"delay\": 200, \"isEnabled\": true, \"error_code\": 404, \"exception_msg\": \"I FAILED\", \"rate\": 0.5 }",
            Name='test.config',
            Type='String',
            Overwrite=True
        )

    @ignore_warnings
    def tearDown(self):
        self.ssm_client.delete_parameters(Names=['test.config'])

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
        error_code, rate = get_config('error_code')
        self.assertEqual(error_code, 404)
        self.assertEqual(rate, 0.5)

    @ignore_warnings
    def test_get_config_rate(self):
        rate, rate = get_config('rate')
        self.assertEqual(rate, 0.5)
        self.assertEqual(rate, 0.5)

    @ignore_warnings
    def test_get_config_bad_key(self):
        with self.assertRaises(KeyError):
            get_config('dela')

    @ignore_warnings
    def test_get_config_bad_config(self):
        os.environ['CHAOS_PARAM'] = 'test.conf'
        with self.assertRaises(InvalidParameterError):
            get_config('delay')


class TestConfigErrorMethods(TestBase):

    @ignore_warnings
    def setUp(self):
        os.environ['CHAOS_PARAM'] = 'test.config'
        self.ssm_client.put_parameter(
            Value="{ \"delay\": 200, \"isEnabled\": true, \"exception_msg\": \"I FAILED\", \"rate\": 0.5 }",
            Name='test.config',
            Type='String',
            Overwrite=True
        )

    @ignore_warnings
    def tearDown(self):
        self.ssm_client.delete_parameters(Names=['test.config'])

    @ignore_warnings
    def test_get_config(self):
        with self.assertRaises(KeyError):
            get_config('error_code')


class TestConfigisEnabled(TestBase):

    @ignore_warnings
    def setUp(self):
        os.environ['CHAOS_PARAM'] = 'test.config'
        self.ssm_client.put_parameter(
            Value="{ \"delay\": 200, \"isEnabled\": false, \"exception_msg\": \"I FAILED\", \"rate\": 0.5 }",
            Name='test.config',
            Type='String',
            Overwrite=True
        )

    @ignore_warnings
    def tearDown(self):
        self.ssm_client.delete_parameters(Names=['test.config'])

    @ignore_warnings
    def test_get_config(self):
        delay, rate = get_config('error_code')
        self.assertEqual(delay, 0)
        self.assertEqual(rate, 0)


if __name__ == '__main__':
    unittest.main()

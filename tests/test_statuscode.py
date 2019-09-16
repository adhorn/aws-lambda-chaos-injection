from chaos_lambda import inject_statuscode
import unittest
import os
import warnings
import boto3
import pytest
import logging

client = boto3.client('ssm', region_name='eu-north-1')

os.environ['CHAOS_PARAM'] = 'test.config'


def ignore_warnings(test_func):
    def do_test(self, *args, **kwargs):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", ResourceWarning)
            warnings.simplefilter("ignore", DeprecationWarning)
            test_func(self, *args, **kwargs)
    return do_test


@inject_statuscode
def handler_with_statuscode(event, context):
    return {
        'statusCode': 200,
        'body': 'Hello from Lambda!'
    }


@inject_statuscode(error_code=500)
def handler_with_statuscode_arg(event, context):
    return {
        'statusCode': 200,
        'body': 'Hello from Lambda!'
    }


class TestStatusCodeMethods(unittest.TestCase):

    @pytest.fixture(autouse=True)
    def inject_fixtures(self, caplog):
        self._caplog = caplog

    @ignore_warnings
    def setUp(self):
        os.environ['CHAOS_PARAM'] = 'test.config'
        client.put_parameter(
            Value="{ \"delay\": 400, \"isEnabled\": true, \"error_code\": 404, \"exception_msg\": \"I FAILED\", \"rate\": 1 }",
            Name='test.config',
            Type='String',
            Overwrite=True
        )

    @ignore_warnings
    def tearDown(self):
        client.delete_parameters(Names=['test.config'])

    @ignore_warnings
    def test_get_statuscode(self):
        with self._caplog.at_level(logging.DEBUG, logger="chaos_lambda"):
            response = handler_with_statuscode('foo', 'bar')
            assert (
                'Injecting Error 404 at a rate of 1' in self._caplog.text
            )
        self.assertEqual(
            str(response), "{'statusCode': 404, 'body': 'Hello from Lambda!'}")

    @ignore_warnings
    def test_get_statuscode_arg(self):
        with self._caplog.at_level(logging.DEBUG, logger="chaos_lambda"):
            response = handler_with_statuscode_arg('foo', 'bar')
            assert (
                'Injecting Error 500 at a rate of 1' in self._caplog.text
            )
        self.assertEqual(
            str(response), "{'statusCode': 500, 'body': 'Hello from Lambda!'}")


class TestStatusCodeMethodslowrate(unittest.TestCase):

    @ignore_warnings
    def setUp(self):
        os.environ['CHAOS_PARAM'] = 'test.config'
        client.put_parameter(
            Value="{ \"delay\": 400, \"isEnabled\": true, \"error_code\": 404, \"exception_msg\": \"I FAILED\", \"rate\": 0.0000001 }",
            Name='test.config',
            Type='String',
            Overwrite=True
        )

    @ignore_warnings
    def tearDown(self):
        client.delete_parameters(Names=['test.config'])

    @ignore_warnings
    def test_get_statuscode(self):
        response = handler_with_statuscode('foo', 'bar')
        self.assertEqual(
            str(response), "{'statusCode': 200, 'body': 'Hello from Lambda!'}")


class TestStatusCodeMethodsnotenabled(unittest.TestCase):

    @ignore_warnings
    def setUp(self):
        os.environ['CHAOS_PARAM'] = 'test.config'
        client.put_parameter(
            Value="{ \"delay\": 400, \"isEnabled\": false, \"error_code\": 404, \"exception_msg\": \"I FAILED\", \"rate\": 1 }",
            Name='test.config',
            Type='String',
            Overwrite=True
        )

    @ignore_warnings
    def tearDown(self):
        client.delete_parameters(Names=['test.config'])

    @ignore_warnings
    def test_get_statuscode(self):
        response = handler_with_statuscode('foo', 'bar')
        self.assertEqual(
            str(response), "{'statusCode': 200, 'body': 'Hello from Lambda!'}")


if __name__ == '__main__':
    unittest.main()

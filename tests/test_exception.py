from ssm_cache import InvalidParameterError
from chaos_lambda import inject_exception
from io import StringIO
from unittest.mock import patch
import unittest
import os
import warnings
import boto3
import os

client = boto3.client('ssm', region_name='eu-north-1')

os.environ['CHAOS_PARAM'] = 'chaoslambda.config'


def ignore_warnings(test_func):
    def do_test(self, *args, **kwargs):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", ResourceWarning)
            warnings.simplefilter("ignore", DeprecationWarning)
            test_func(self, *args, **kwargs)
    return do_test

@inject_exception
def handler_with_exception(event, context):
    return {
        'statusCode': 200,
        'body': 'Hello from Lambda!'
    }

@inject_exception(exception_type=ValueError)
def handler_with_exception_arg(event, context):
    return {
        'statusCode': 200,
        'body': 'Hello from Lambda!'
    }

@inject_exception(exception_type=TypeError, exception_msg='foobar')
def handler_with_exception_arg_2(event, context):
    return {
        'statusCode': 200,
        'body': 'Hello from Lambda!'
    }

class TestStringMethods(unittest.TestCase):

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
         with self.assertRaises(Exception):
            handler_with_exception('foo', 'bar')

    @ignore_warnings
    def test_get_statuscode_arg(self):
        with self.assertRaises(ValueError):
            handler_with_exception_arg('foo', 'bar')

    @ignore_warnings
    def handler_with_exception_arg_2(self):
        with self.assertRaises(TypeError):
            handler_with_exception_arg_2('foo', 'bar')


if __name__ == '__main__':
    unittest.main()

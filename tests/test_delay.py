from ssm_cache import InvalidParameterError
from chaos_lambda import inject_delay
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

@inject_delay
def handler(event, context):
    return {
        'statusCode': 200,
        'body': 'Hello from Lambda!'
    }

@inject_delay(delay=1000)
def handler_with_delay_arg(event, context):
    return {
        'statusCode': 200,
        'body': 'Hello from Lambda!'
    }

@inject_delay(delay=0)
def handler_with_delay_zero(event, context):
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
    def test_get_delay(self):
        with patch('sys.stdout', new=StringIO()) as fakeOutput:
            response = handler('foo', 'bar')
            assert (
                'Injecting 400 of delay with a rate of 1' in fakeOutput.getvalue().strip()    
            )
        self.assertEqual(str(response), "{'statusCode': 200, 'body': 'Hello from Lambda!'}")

    @ignore_warnings
    def test_get_delay_arg(self):
        with patch('sys.stdout', new=StringIO()) as fakeOutput:
            response = handler_with_delay_arg('foo', 'bar')
            assert (
                'Injecting 1000 of delay with a rate of 1' in fakeOutput.getvalue().strip()    
            )
        self.assertEqual(str(response), "{'statusCode': 200, 'body': 'Hello from Lambda!'}")

    @ignore_warnings
    def test_get_delay_zero(self):
        with patch('sys.stdout', new=StringIO()) as fakeOutput:
            response = handler_with_delay_zero('foo', 'bar')
            assert (
                'Added 0.00ms to handler_with_delay_zero' in fakeOutput.getvalue().strip()    
            )
        self.assertEqual(str(response), "{'statusCode': 200, 'body': 'Hello from Lambda!'}")


if __name__ == '__main__':
    unittest.main()

import os
import warnings
import boto3


client = boto3.client('ssm')

os.environ['CHAOS_PARAM'] = 'test.config'


def ignore_warnings(test_func):
    def do_test(self, *args, **kwargs):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", ResourceWarning)
            warnings.simplefilter("ignore", DeprecationWarning)
            test_func(self, *args, **kwargs)
    return do_test

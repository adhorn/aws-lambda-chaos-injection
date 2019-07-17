# -*- coding: utf-8 -*-
"""
Chaos Injection for AWS Lambda - chaos_lambda
======================================================

``chaos_lambda`` is a small library injecting chaos into `AWS Lambda 
<https://aws.amazon.com/lambda/>`_. 
It offers simple python decorators to do `delay`, `exception` and `statusCode` injection
and a Class to add `delay` to any 3rd party dependencies called from your function.
This allows to conduct small chaos engineering experiments for your serverless application 
in the `AWS Cloud <https://aws.amazon.com>`_.

* Support for Latency injection using ``delay``
* Support for Exception injection using ``exception_msg``
* Support for HTTP Error status code injection using ``error_code``
* Using for SSM Parameter Store to control the experiment using ``isEnabled``
* Support for adding rate of failure using ``rate``. (Default rate = 1)
* Per Lambda function injection control using Environment variable (``CHAOS_PARAM``)

Install
--------
.. code:: shell

    pip install chaos-lambda


Example
--------
.. code:: python

    # function.py

    from chaos_lambda import (
    inject_delay, inject_exception, inject_statuscode)

    os.environ['CHAOS_PARAM'] = 'chaoslambda.config'

    @inject_exception
    def lambda_handler_with_exception(event, context):
        return {
            'statusCode': 200,
            'body': 'Hello from Lambda!'
        }

    @inject_delay
    def lambda_handler_with_delay(event, context):
        return {
            'statusCode': 200,
            'body': 'Hello from Lambda!'
        }

    @inject_statuscode
    def lambda_handler_with_statuscode(event, context):
        return {
            'statusCode': 200,
            'body': 'Hello from Lambda!'
        }


When excecuted,  the Lambda function, e.g ``lambda_handler_with_exception('foo', 'bar')``, will produce the following result:

.. code:: shell

    exception_msg from config I really failed seriously with a rate of 1
    corrupting now
    Traceback (most recent call last):
    File "<stdin>", line 1, in <module>
    File "/.../chaos_lambda.py", line 199, in wrapper
        raise Exception(exception_msg)
    Exception: I really failed seriously

Configuration
-------------
The configuration for the failure injection is stored in the `AWS SSM Parameter Store  
<https://aws.amazon.com/ssm/>`_ and accessed at runtime by the ``get_config()``
function:

.. code:: json

    {
        "isEnabled": true,
        "delay": 400,
        "error_code": 404,
        "exception_msg": "I really failed seriously",
        "rate": 1
    }

To store the above configuration into SSM using the `AWS CLI <https://aws.amazon.com/cli>`_ do the following:

.. code:: shell

    aws ssm put-parameter --region eu-north-1 --name chaoslambda.config --type String --overwrite --value "{ \"delay\": 400, \"isEnabled\": true, \"error_code\
": 404, \"exception_msg\": \"I really failed seriously\", \"rate\": 1 }"

AWS Lambda will need to have `IAM access to SSM <https://docs.aws.amazon.com/systems-manager/latest/userguide/sysman-paramstore-access.html>`_.

.. code:: json

    {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Action": [
                    "ssm:DescribeParameters"
                ],
                "Resource": "*"
            },
            {
                "Effect": "Allow",
                "Action": [
                    "ssm:GetParameters",
                    "ssm:GetParameter"
                ],
                "Resource": "arn:aws:ssm:eu-north-1:12345678910:parameter/chaoslambda.config"
            }
        ]
    }


Supported Decorators:
---------------------
``chaos_lambda`` currently supports the following decorators:

* `@inject_delay` - add delay in the AWS Lambda execution
* `@inject_exception` - Raise an exception during the AWS Lambda execution
* `@inject_statuscode` - force AWS Lambda to return a specific HTTP error code

and the following class:

* `SessionWithDelay` - enabled to sub-classing requests library and call dependencies with delay

More information:
-----------------


"""

from __future__ import division, unicode_literals
from ssm_cache import SSMParameter, InvalidParameterError
import os
import time
import logging
import random
import json
import requests

logger = logging.getLogger(__name__)

__version__ = '0.1.2'


def get_config(config_key):
    """
    Retrieve the configuration from the SSM parameter store
    The config always returns a tuple (value, rate)
    value: requested configuration
    rate: the injection probability (default 1 --> 100%)

    Usage::

        >>> import os
        >>> from chaos_lambda import get_config
        >>> os.environ['CHAOS_PARAM'] = 'chaoslambda.config'
        >>> get_config('delay')
        (400, 1)
        >>> get_config('exception_msg')
        ('I really failed seriously', 1)
        >>> get_config('error_code')
        (404, 1)

    """
    param = SSMParameter(os.environ['CHAOS_PARAM'])
    try:
        value = json.loads(param.value)
        if not value["isEnabled"]:
            return 0, 1
        return value[config_key], value.get('rate', 1)
    except InvalidParameterError as e:
        # key does not exist in SSM
        raise InvalidParameterError("{} does not exist in SSM".format(e))
    except KeyError as e:
        # not a valid Key in the SSM configuration
        raise KeyError("{} is not a valid Key in the SSM configuration".format(e))


def inject_delay(func):
    """
    Add delay to the lambda function - delay is returned from the SSM paramater
    using ``get_config('delay')`` which returns a tuple delay, rate.

    Usage::

      >>> from chaos_lambda import inject_delay
      >>> @inject_delay
      ... def handler(event, context):
      ...    return {
      ...       'statusCode': 200,
      ...       'body': 'Hello from Lambda!'
      ...    }
      >>> handler('foo', 'bar')

      This will create the following Log outup in CloudWatch (with a delay of 400ms)
    
        START RequestId: 5295aa0b-...-50fcfbebea1f Version: $LATEST
        delay: 400, rate: 1
        Added 400.61ms to lambda_handler
        END RequestId: 5295aa0b-...-50fcfbebea1f
        REPORT RequestId: 5295aa0b-...-50fcfbebea1f Duration: 442.65 ms Billed Duration: 500 ms  Memory Size: 128 MB Max Memory Used: 79 MB

    """
    def wrapper(*args, **kwargs):
        delay, rate = get_config('delay')
        if not delay:
            return func(*args, **kwargs)
        print("delay: {0}, rate: {1}".format(delay, rate))
        # if delay and rate exist, delaying with that value at that rate
        start = time.time()
        if delay > 0 and rate >= 0:

            # add latency approx rate% of the time
            if random.random() <= rate:
                time.sleep(delay / 1000.0)

        result = func(*args, **kwargs)
        end = time.time()

        print('Added {1:.2f}ms to {0:s}'.format(
            func.__name__,
            (end - start) * 1000
        ))
        return result
    return wrapper


def inject_exception(func):
    """
Forces the lambda function to fail and raise an exception
using ``get_config('exception_msg')`` which returns a tuple exception_msg, rate.

Usage::

    >>> from chaos_lambda import inject_exception
    >>> @inject_exception
    ... def handler(event, context):
    ...     return {
    ...        'statusCode': 200,
    ...        'body': 'Hello from Lambda!'
    ...     }
    >>> handler('foo', 'bar')
    { "errorMessage": "I really failed seriously",
      "errorType": "Exception",
      "stackTrace": [
        "File \"chaos_lambda.py\", line 76, in wrapper raise Exception(exception_msg)"
        ]
    }

    """
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        exception_msg, rate = get_config('exception_msg')
        if not exception_msg:
            return result
        print("exception_msg from config {0} with a rate of {1}".format(exception_msg, rate))
        # add injection approx rate% of the time
        if random.random() <= rate:
            print("corrupting now")
            raise Exception(exception_msg)
        else:
            return result
    return wrapper


def inject_statuscode(func):
    """
Forces the lambda function to return with a specific Status Code
using ``get_config('error_code')`` which returns a tuple error_code, rate.

Usage::

    >>> from chaos_lambda import inject_statuscode
    >>> @inject_statuscode
    ... def handler(event, context):
    ...    return {
    ...       'statusCode': 200,
    ...       'body': 'Hello from Lambda!'
    ...    }
    >>> handler('foo', 'bar')
    { "statusCode": 404, "body": "Hello from Lambda! }
    """

    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        error_code, rate = get_config('error_code')
        if not error_code:
            return result
        print("Error from config {0} at a rate of {1}".format(error_code, rate))
        # add injection approx rate% of the time
        if random.random() <= rate:
            print("corrupting now")
            result['statusCode'] = error_code
            return result
        else:
            return result
    return wrapper

class SessionWithDelay(requests.Session):
    """
    This is a class for injecting delay to 3rd party dependencies.
    Subclassing the requests library is useful if you want to conduct other chaos experiments 
    within the library, like error injection or requests modification.
    This is a simple subclassing of the parent class requests.Session to add delay to the request method.

    Usage::

       >>> from chaos_lambda import SessionWithDelay
       >>> def dummy():
       ...     session = SessionWithDelay(delay=300)
       ...     session.get('https://stackoverflow.com/')
       ...     pass
       >>> dummy()
       Added 300.00ms of delay to GET

    """
    def __init__(self, delay=None, *args, **kwargs):
        super(SessionWithDelay, self).__init__(*args, **kwargs)
        self.delay = delay

    def request(self, method, url, **kwargs):
        print('Added {1:.2f}ms of delay to {0:s}'.format(
            method, self.delay))
        time.sleep(self.delay / 1000.0)
        return super(SessionWithDelay, self).request(method, url, **kwargs)
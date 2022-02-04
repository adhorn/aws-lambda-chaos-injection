# -*- coding: utf-8 -*-
"""
Chaos Injection for AWS Lambda - chaos_lambda
======================================================

|docs| |issues| |Maintenance| |Pypi| |Travis| |Coveralls| |twitter|

.. |docs| image:: https://readthedocs.org/projects/aws-lambda-chaos-injection/badge/?version=latest
    :target: https://aws-lambda-chaos-injection.readthedocs.io/en/latest/?badge=latest
    :alt: Documentation Status

.. |twitter| image:: https://img.shields.io/twitter/url/https/github.com/adhorn/aws-lambda-chaos-injection?style=social
    :alt: Twitter
    :target: https://twitter.com/intent/tweet?text=Wow:&url=https%3A%2F%2Fgithub.com%2Fadhorn%2Faws-lambda-chaos-injection

.. |issues| image:: https://img.shields.io/github/issues/adhorn/aws-lambda-chaos-injection
    :alt: Issues

.. |Maintenance| image:: https://img.shields.io/badge/Maintained%3F-yes-green.svg
    :alt: Maintenance
    :target: https://GitHub.com/adhorn/aws-lambda-chaos-injection/graphs/commit-activity

.. |Pypi| image:: https://badge.fury.io/py/chaos-lambda.svg
    :target: https://badge.fury.io/py/chaos-lambda

.. |Travis| image:: https://api.travis-ci.org/adhorn/aws-lambda-chaos-injection.svg?branch=master
    :target: https://travis-ci.org/adhorn/aws-lambda-chaos-injection

.. |Coveralls| image:: https://coveralls.io/repos/github/adhorn/aws-lambda-chaos-injection/badge.svg?branch=master
    :target: https://coveralls.io/github/adhorn/aws-lambda-chaos-injection?branch=master

``chaos_lambda`` is a small library injecting chaos into `AWS Lambda
<https://aws.amazon.com/lambda/>`_.
It offers simple python decorators to do `delay`, `exception` and `statusCode` injection for your AWS Lambda function.
This allows to conduct small chaos engineering experiments for your serverless application
in the `AWS Cloud <https://aws.amazon.com>`_.

* Support for Latency injection using ``fault_type: latency``
* Support for Exception injection using ``fault_type: exception``
* Support for HTTP Error status code injection using ``fault_type: status_code``
* Using for SSM Parameter Store to control the experiment using ``is_enabled: true``
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

    import os
    from chaos_lambda import inject_fault

    # this should be set as a Lambda environment variable
    os.environ['CHAOS_PARAM'] = 'chaoslambda.config'

    @inject_fault
    def handler(event, context):
        return {
            'statusCode': 200,
            'body': 'Hello from Lambda!'
        }

Considering a configuration as follows:

.. code:: json

    {
        "fault_type": "exception",
        "delay": 400,
        "is_enabled": true,
        "error_code": 404,
        "exception_msg": "This is chaos",
        "rate": 1
    }

When excecuted, the Lambda function, e.g ``handler('foo', 'bar')``, will produce the following result:

.. code:: shell

    exception_msg from config chaos with a rate of 1
    corrupting now
    Traceback (most recent call last):
    File "<stdin>", line 1, in <module>
    File "/.../chaos_lambda.py", line 199, in wrapper
        raise Exception(exception_msg)
    Exception: This is chaos

Configuration
-------------
The configuration for the failure injection is stored in the `AWS SSM Parameter Store
<https://aws.amazon.com/ssm/>`_ and accessed at runtime by the ``get_config()``
function:

.. code:: json

    {
        "fault_type": "exception",
        "delay": 400,
        "is_enabled": true,
        "error_code": 404,
        "exception_msg": "This is chaos",
        "rate": 1
    }

To store the above configuration into SSM using the `AWS CLI <https://aws.amazon.com/cli>`_ do the following:

.. code:: shell

    aws ssm put-parameter --name chaoslambda.config --type String --overwrite --value "{ \"delay\": 400, \"is_enabled\": true, \"error_code\": 404, \"exception_msg\": \"This is chaos\", \"rate\": 1, \"fault_type\": \"exception\"}" --region eu-west-1

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


Supported Faults:
---------------------
``chaos_lambda`` currently supports the following faults:

* `latency` - Add latency in the AWS Lambda execution
* `exception` - Raise an exception during the AWS Lambda execution
* `status_code` - force AWS Lambda to return a specific HTTP error code

More information:
-----------------


"""

from __future__ import division, unicode_literals
from functools import wraps
import os
import time
import logging
import random
import json
from ssm_cache import SSMParameter
from ssm_cache.cache import InvalidParameterError

logger = logging.getLogger(__name__)

__version__ = '0.3'


def get_config():
    """
Retrieve the full configuration from the SSM parameter store
The config returns a dictionary
value: requested configuration

How to use::

    >>> import os
    >>> from chaos_lambda import get_config
    >>> os.environ['CHAOS_PARAM'] = 'chaoslambda.config'
    >>> get_config()
    {'delay': 500, 'is_enabled': True, 'error_code': 404, 'exception_msg': 'chaos', 'rate': 1, 'fault_type': 'latency'}
    """
    param = SSMParameter(os.environ['CHAOS_PARAM'])
    try:
        value = json.loads(param.value)
        if not value["is_enabled"]:
            return
        return value
    except InvalidParameterError as ex:
        # key does not exist in SSM
        raise InvalidParameterError("{} is not a valid SSM config".format(ex))


def inject_fault(func):
    """
Add failure to the lambda function based on the value of 'fault_type' present
in the config returned from the SSM parameter store

Given SSM Configuration::

    {
        "fault_type": "latency",
        "delay": 400,
        "is_enabled": true,
        "error_code": 404,
        "exception_msg": "chaos",
        "rate": 1
    }

Usage::

    >>> @inject_fault
    ... def handler(event, context):
    ...    return {
    ...       'statusCode': 200,
    ...       'body': 'Hello from Lambda!'
    ...    }
    >>> handler('foo', 'bar')
    Injecting 400 of delay with a rate of 1
    Added 402.20ms to handler
    {'statusCode': 200, 'body': 'Hello from Lambda!'}

Given SSM Configuration::

    {
        "fault_type": "exception",
        "delay": 400,
        "is_enabled": true,
        "error_code": 404,
        "exception_msg": "chaos",
        "rate": 1
    }

Usage::

  >>> @inject_fault
    ... def handler(event, context):
    ...     return {
    ...        'statusCode': 200,
    ...        'body': 'Hello from Lambda!'
    ...     }
    >>> handler('foo', 'bar')
    Injecting exception_type <class "Exception"> with message chaos a rate of 1
    corrupting now
    Traceback (most recent call last):
        File "<stdin>", line 1, in <module>
        File "/.../chaos_lambda.py", line 316, in wrapper
            raise _exception_type(_exception_msg)
    Exception: chaos

Given SSM Configuration::

    {
        "fault_type": "status_code",
        "delay": 400,
        "is_enabled": true,
        "error_code": 404,
        "exception_msg": "chaos",
        "rate": 1
    }

Usage::

    >>> @inject_fault
    ... def handler(event, context):
    ...    return {
    ...       'statusCode': 200,
    ...       'body': 'Hello from Lambda!'
    ...    }
    >>> handler('foo', 'bar')
    Injecting Error 404 at a rate of 1
    corrupting now
    {'statusCode': 404, 'body': 'Hello from Lambda!'}

    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        _chaos_conf = get_config()
        if not _chaos_conf:
            return func(*args, **kwargs)

        logger.info(
            "Got SSM configuration: %s",
            _chaos_conf
        )

        _fault_type = _chaos_conf.get('fault_type')
        rate = _chaos_conf.get("rate")

        if _fault_type == "latency":
            if isinstance(_chaos_conf.get("delay"), int):
                _delay = _chaos_conf.get("delay")
            else:
                logger.info("Parameter delay is no valid int")
                return func(*args, **kwargs)

            logger.info(
                "Injecting %d ms of delay with a rate of %s",
                _delay, rate
            )

            start = time.time()
            if _delay > 0 and rate >= 0:
                # add latency approx rate% of the time
                if round(random.random(), 5) <= rate:
                    logger.debug('sleeping now')
                    time.sleep(_delay / 1000.0)

            end = time.time()

            logger.debug(
                'Added %.2fms to %s',
                (end - start) * 1000,
                func.__name__
            )

        if _fault_type == "exception":
            _exception_type = Exception

            if isinstance(_chaos_conf.get("exception_msg"), str):
                _exception_msg = _chaos_conf.get("exception_msg")
            else:
                logger.info("Parameter exception_msg is no valid string")
                return func(*args, **kwargs)

            logger.info(
                "Injecting exception_type %s with message %s a rate of %d",
                _exception_type,
                _exception_msg,
                rate
            )

            # add injection approx rate% of the time
            if round(random.random(), 5) <= rate:
                logger.debug("corrupting now")
                raise _exception_type(_exception_msg)

        if _fault_type == "status_code":
            result = func(*args, **kwargs)
            if isinstance(_chaos_conf.get("error_code"), int):
                _error_code = _chaos_conf.get("error_code")
            else:
                logger.info("Parameter error_code is no valid int")
                return func(*args, **kwargs)

            logger.info("Injecting Error %s at a rate of %d", _error_code, rate)
            # add injection approx rate% of the time
            if round(random.random(), 5) <= rate:
                logger.debug("corrupting now")
                result['statusCode'] = _error_code
                return result

        return func(*args, **kwargs)
    return wrapper

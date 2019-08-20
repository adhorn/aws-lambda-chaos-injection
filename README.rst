
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

    import os
    from chaos_lambda import inject_delay, inject_exception, inject_statuscode

    # this should be set as a Lambda environment variable
    os.environ['CHAOS_PARAM'] = 'chaoslambda.config'

    @inject_exception
    def handler_with_exception(event, context):
        return {
            'statusCode': 200,
            'body': 'Hello from Lambda!'
        }


    @inject_exception(exception_type=TypeError, exception_msg='foobar')
    def handler_with_exception_arg(event, context):
        return {
            'statusCode': 200,
            'body': 'Hello from Lambda!'
        }

    @inject_exception(exception_type=ValueError)
    def handler_with_exception_arg_2(event, context):
        return {
            'statusCode': 200,
            'body': 'Hello from Lambda!'
        }


    @inject_statuscode
    def handler_with_statuscode(event, context):
        return {
            'statusCode': 200,
            'body': 'Hello from Lambda!'
        }

    @inject_statuscode(error_code=400)
    def handler_with_statuscode_arg(event, context):
        return {
            'statusCode': 200,
            'body': 'Hello from Lambda!'
        }

    @inject_delay
    def handler_with_delay(event, context):
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


When excecuted, the Lambda function, e.g ``handler_with_exception('foo', 'bar')``, will produce the following result:

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

    aws ssm put-parameter --region eu-north-1 --name chaoslambda.config --type String --overwrite --value "{ "delay": 400, "isEnabled": true, "error_code": 404, "exception_msg": "I really failed seriously", "rate": 1 }"

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



`Full Documentation <https://aws-lambda-chaos-injection.readthedocs.io/en/latest/>`_

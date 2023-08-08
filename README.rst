
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

.. |Travis| image:: https://api.travis-ci.com/adhorn/aws-lambda-chaos-injection.svg?branch=master
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

    aws ssm put-parameter --name chaoslambda.config --type String --overwrite --value "{ "delay": 400, "is_enabled": true, "error_code": 404, "exception_msg": "This is chaos", "rate": 1, "fault_type": "exception"}" --region eu-west-1

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



`Full Documentation <https://aws-lambda-chaos-injection.readthedocs.io/en/latest/>`_


Failure Injection for AWS Lambda - failure_injection
======================================================

``failure_injection`` is a small library injecting chaos into `AWS Lambda 
<https://aws.amazon.com/lambda/>`_. 
It offers simple python decorators to do `delay`, `exception` and `statusCode` injection
and a Class to add `delay` to any 3rd party dependencies called from your function.
This allows to conduct small chaos engineering experiments for your serverless application 
in the `AWS Cloud <https://aws.amazon.com>`_.

* Support for Latency injection using ``delay``
* Support for Exception injection using ``exception_msg``
* Support for HTTP Error status code injection using ``error_code``
* Using for SSM Parameter Store to control the experiment using ``isEnabled``
* Per Lambda function injection control using Environment variable (``FAILURE_INJECTION_PARAM``) (thanks to Gunnar Grosch)
* Support for Serverless Framework using ``sls deploy`` (thanks to Gunnar Grosch)
* Support for adding rate of failure using ``rate``. (Default rate = 1)

Install
--------
.. code:: shell

    pip install --index-url https://test.pypi.org/simple/ --no-deps failure-injection


Example
--------
.. code:: python

    # function.py

    from failure_injection import (
    inject_delay, inject_exception, inject_statuscode)

    os.environ['FAILURE_INJECTION_PARAM'] = 'chaoslambda.config'

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
    File "/.../failure_injection.py", line 199, in wrapper
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


Supported Decorators:
---------------------
``failure_injection`` currently supports the following decorators:

* `@inject_delay` - add delay in the AWS Lambda execution
* `@inject_exception` - Raise an exception during the AWS Lambda execution
* `@inject_statuscode` - force AWS Lambda to return a specific HTTP error code

and the following class:

* `SessionWithDelay` - enabled to sub-classing requests library and call dependencies with delay


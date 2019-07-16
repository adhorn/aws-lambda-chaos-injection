from setuptools import setup

import failure_injection

setup(
    name='failure-injection',

    version=failure_injection.__version__,

    description='Decorators and Class to inject failures into AWS Lambda functions',
    long_description=open('../README.rst').read(),

    author='Adrian Hornsby',
    author_email='hornsby.adrian@gmail.com',

    license='MIT',

    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.7',
        'Topic :: Software Development :: Libraries'
    ],

    keywords='chaos engineering lambda decorator aws lambda',

    packages=['failure-injection'],

    setup_requires=['pytest-runner'],
    install_requires=['boto3'],
    tests_require=['pytest'],
)

import setuptools

import chaos_lambda

with open("README.rst", "r", encoding='utf-8') as fh:
    long_description = fh.read()

setuptools.setup(
    name='chaos-lambda',
    version=chaos_lambda.__version__,
    description='Decorators and Class to inject failures into AWS Lambda functions',
    long_description=long_description,
    long_description_content_type="text/x-rst",
    author='Adrian Hornsby',
    author_email='hornsby.adrian@gmail.com',
    url='https://github.com/adhorn/aws-lambda-chaos-injection',
    license='MIT',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Topic :: Software Development :: Libraries'
    ],
    keywords='chaos engineering lambda decorator aws lambda',
    packages=setuptools.find_packages(),
    py_modules=['chaos_lambda'],
    install_requires=['boto3', 'future', 'ssm_cache', 'requests'],
    tests_require=['pytest'],
)

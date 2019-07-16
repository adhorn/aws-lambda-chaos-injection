import setuptools

import failure_injection

with open("README.rst", "r", encoding='utf-8') as fh:
    long_description = fh.read()

setuptools.setup(
    name='failure-injection',
    version=failure_injection.__version__,
    description='Decorators and Class to inject failures into AWS Lambda functions',
    long_description=long_description,
    long_description_content_type="text/x-rst",
    author='Adrian Hornsby',
    author_email='hornsby.adrian@gmail.com',
    url='https://github.com/adhorn/FailureInjectionLibrary',
    license='MIT',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.7',
        'Topic :: Software Development :: Libraries'
    ],
    keywords='chaos engineering lambda decorator aws lambda',
    packages=setuptools.find_packages(),
)

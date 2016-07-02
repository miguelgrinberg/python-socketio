"""
python-socketio
---------------

Socket.IO server.
"""
from setuptools import setup


with open('README.rst', 'r') as f:
    long_description = f.read()

setup(
    name='python-socketio',
    version='1.4.1',
    url='http://github.com/miguelgrinberg/python-socketio/',
    license='MIT',
    author='Miguel Grinberg',
    author_email='miguelgrinberg50@gmail.com',
    description='Socket.IO server',
    long_description=long_description,
    packages=['socketio'],
    zip_safe=False,
    include_package_data=True,
    platforms='any',
    install_requires=[
        'six>=1.9.0',
        'python-engineio>=0.8.0'
    ],
    tests_require=[
        'mock',
    ],
    test_suite='tests',
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)

from setuptools import setup
from os import path
from aw_api import __version__
this_directory = path.abspath(path.dirname(__file__))

with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

requirements = []

setup(
    name='aw_api',
    version=__version__,
    packages=['aw_api', 'aw_api.dataobjects'],
    description='Armored Warfare unofficial API',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/lookandhate/ArmoredWarfareAPI',
    license='MIT',
    author='https://github.com/lookandhate',
    author_email='',
    install_requires=['requests', 'beautifulsoup4'],
    python_requires='>=3.7.0',
    keywords=['armored warfare', 'aw', 'armored warfare api', 'armata', 'армата'],
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: Implementation :: CPython'
    ]
)

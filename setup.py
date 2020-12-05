from setuptools import setup

requirements = []
with open('requirements.txt') as f:
  requirements = f.read().splitlines()


setup(
    name='aw_api',
    version='0.2.0',
    packages=['aw_api'],
    url='https://github.com/lookandhate/ArmoredWarfareAPI',
    license='MIT',
    author='https://github.com/lookandhate',
    author_email='',
    description='Armored Warfare statistics API',
    install_requires=requirements,
    python_requires='>3.6.0'
)

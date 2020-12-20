from setuptools import setup

requirements = []

setup(
    name='aw_api',
    version='1.0.0',
    packages=['aw_api'],
    description='Armored Warfare unofficial API',
    url='https://github.com/lookandhate/ArmoredWarfareAPI',
    license='MIT',
    author='https://github.com/lookandhate',
    author_email='',
    install_requires=['requests', 'beautifulsoup4'],
    python_requires='>=3.6.0',
    keywords=['armored warfare', 'aw', 'armored warfare api', 'armata', 'армата'],
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: Implementation :: CPython'
    ]
)

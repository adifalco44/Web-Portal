from setuptools import setup

setup(
    name='first',
    packages=['first'],
    include_package_data=True,
    install_requires=[
        'flask',
    ],
    setup_requires=[
        'pytest-runner',
    ],
)

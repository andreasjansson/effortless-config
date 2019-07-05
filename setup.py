import os
from setuptools import setup, find_packages

cwd = os.path.dirname(os.path.abspath(__file__))

with open(os.path.join(cwd, 'effortless_config', 'VERSION')) as f:
    version = f.read().strip()

setup(
    name='effortless-config',
    description='Globally scoped configuration with argparse integration',
    url='https://github.com/andreasjansson/effortless-config',
    version=version,
    packages=find_packages(exclude=['test', '*.test', '*.test.*']),
    include_package_data=True,
    classifiers=['Programming Language :: Python'],
    install_requires=[],
    python_requires='>=3.6',
)

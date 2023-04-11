from setuptools import setup, find_packages
from io import open
from os import path

import pathlib
# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

# automatically captured required modules for install_requires in requirements.txt
with open(path.join(HERE, 'requirements.txt'), encoding='utf-8') as f:
    all_reqs = f.read().split('\n')

install_requires = [
    x.strip() for x in all_reqs if ('git+' not in x) and (
        not x.startswith('#')) and (not x.startswith('-'))
]
dependency_links = [x.strip().replace('git+', '') for x in all_reqs \
                    if 'git+' not in x]
setup(
    name='cisco-config-saver',
    description= 'A simple commandline application for saving cisco switches configuration',
    version='1.0.1',
    packages=find_packages(),  # list of all packages
    install_requires=install_requires,
    python_requires='>=3.10',  # any python greater than 3.10
    entry_points='''
        [console_scripts]
        cisco-config-save=ciscocfgsvr.__main__:main
    ''',
    author="VPS",
    author_email='vpsinbox@mail.ru',
    long_description=README,
    long_description_content_type="text/markdown",
    url='https://github.com/vps2/cisco-config-saver',
    dependency_links=dependency_links,
    classifiers=[
        'Environment :: Console',
        'Programming Language :: Python',
    ])

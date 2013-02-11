from distutils.core import setup

setup(
    name='PyRedmineCLI',
    version='0.1.0',
    author='Jaymz Campbell',
    author_email='jaymz@jaymz.eu',
    packages=['redminecli', ],
    scripts=['bin/redmine', ],
    url='http://github.com/jaymzcd/pyredminecli',
    license='LICENSE.txt',
    description='Command line interface with cacheing to Redmine project management system.',
    long_description=open('README.rst').read(),
    install_requires=[
        "pyredminews",
    ],
)

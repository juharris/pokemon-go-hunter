from setuptools import setup

setup(
    name='pokemon-go-hunter',
    version='0.0.1',
    packages=['pokemon_go_hunter'],
    url='',
    license="MIT",
    author="Justin Harris",
    author_email='',
    description="Find Pokemon in Pokemon Go.",
    requires=[
        'pushbullet.py',
        'python-twitter',
        'PyYAML',
    ]
)

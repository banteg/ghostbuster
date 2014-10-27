from setuptools import setup
from ghostbuster import __version__

setup(
    name='ghostbuster',
    version=__version__,
    description='Turn Ghost blog into static site',
    url='https://github.com/banteg/ghostbuster',
    py_modules=['ghostbuster'],
    install_requires=['requests', 'click'],
    entry_points={
        'console_scripts': ['ghostbuster = ghostbuster:cli'],
    },
)

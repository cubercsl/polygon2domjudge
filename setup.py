import os
import subprocess

from setuptools import setup, find_packages


def get_version():
    base_dir = os.path.dirname(__file__)

    __version__ = None
    try:
        update_script = os.path.join(base_dir, 'update_version.py.sh')
        __version__ = subprocess.check_output([update_script]).decode('utf-8').strip()
    except:
        pass
    if __version__ is None:
        version_file = os.path.join(base_dir, 'p2d', '_version.py')
        with open(version_file, 'r') as version_in:
            loc = {'__version__': __version__}
            exec(version_in.read(), None, loc)
            __version__ = loc['__version__']
    return __version__


setup(
    name='polygon2domjudge',
    version=get_version(),
    description='Process Polygon Package to DOMjudge Package.',
    author='cubercsl',
    author_email='cubercsl@163.com',
    url='https://github.com/2014CAIS01/polygon2domjudge',
    license='MIT',
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'p2d=p2d.main:main'
        ]
    },
    python_requires='>=3.5',
    platforms='any',
    install_requires=[
        'PyYAML'
    ]
)

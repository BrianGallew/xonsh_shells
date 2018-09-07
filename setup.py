from setuptools import setup

setup(
    name='xontrib-xonsh_shells',
    version='0.1.0',
    url='https://github.com/BrianGallew/xonsh_shells',
    license='MIT',
    author='Brian Gallew',
    author_email='geek@gallew.org',
    description='Various extensions related to AWS and multiple shell coordination.  Today.',
    packages=['xontrib'],
    package_dir={'xontrib': 'xontrib'},
    package_data={'xontrib': ['*.xsh']},
    platforms='any',
    zip_safe=False,
)

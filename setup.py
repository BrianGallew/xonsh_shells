"A couple small utiloities"
from setuptools import setup

setup(
    name="xontrib-xonsh_shells",
    version="0.1.1",
    url="https://github.com/BrianGallew/xonsh_shells",
    license="MIT",
    author="Brian Gallew",
    author_email="geek@gallew.org",
    description="Various extensions related to AWS and multiple shell coordination.  Today.",
    packages=["xontrib"],
    package_dir={"xontrib": "xontrib"},
    package_data={"xontrib": ["*.xsh"]},
    platforms="any",
    classifiers=[
        "Environment :: Console",
        "Intended Audience :: End Users/Desktop",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Topic :: Desktop Environment",
        "Topic :: System :: Shells",
        "Topic :: System :: System Shells",
    ],
    zip_safe=False,
)

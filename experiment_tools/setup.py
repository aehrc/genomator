from setuptools import setup, find_packages
from glob import glob

setup(
    name='experiment_tools',
    version='0.0.1',
    packages=find_packages(include=["experiment_tools"]),
    scripts=glob("tools/*")
)

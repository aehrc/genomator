from setuptools import setup, find_packages

setup(
    name='genomator',
    version='0.0.1',
    packages=find_packages(include=["genomator"]),
    scripts=['scripts/genomator','scripts/reverse_genomator'],
    install_requires=[
        'tqdm',
        'vcfpy',
        'python-sat',
        'click',
        'cyvcf2',
        'stopit'
    ],
)

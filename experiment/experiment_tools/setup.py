from setuptools import setup, find_packages
from glob import glob

setup(
    name='experiment_tools',
    version='0.0.1',
    packages=find_packages(include=["experiment_tools"]),
    scripts=glob("tools/*"),
    install_requires=[
        'tqdm',
        'tensorflow',
        'keras',
        'scikit-allel',
        'torch',
        'vcfpy',
        'scipy',
        'numpy',
        'matplotlib',
        'pandas',
        'seaborn',
        'POT',
        'scikit-learn',
        'click',
        'cyvcf2',
        'h5py',
        'resample',
    ]
)

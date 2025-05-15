#!/usr/bin/env python3
import click
import numpy as np
from sklearn.decomposition import PCA
import matplotlib
import matplotlib.pyplot as plt
from experiment_tools import *
import pickle

base_colours = ['r','b','g','m','c','w','k'] 

def plot_PCA(sets,output_file):
    #combined_data = np.matrix(sum(sets,[]))
    #combined_data = np.matrix(sets[0])
    combined_data = np.asarray(sets[0])
    pca_transform = PCA(n_components=2,svd_solver='full').fit(combined_data)
    fig = plt.figure(figsize = (10,10))
    ax = fig.add_subplot(1,1,1)
    for i,s in enumerate(sets):
        coordinates = pca_transform.transform(np.asarray(s))
        xs = coordinates[:,0]
        ys = coordinates[:,1]
        ax.scatter(xs, ys,c=[base_colours[i] for j in range(len(xs))],s=50,alpha=0.2)
    plt.savefig(output_file)

def load_file(f,postpend=True):
    extension = f.split(".")[-1]
    if extension=="pickle":
        with open(f,"rb") as f:
            p = pickle.load(f)
            if (len(p)==2) and isinstance(p[1],int):
                return p[0]
            return p
    else:
        return parse_VCF_to_genome_strings(f)[0]

@click.command()
@click.argument('input_vcf_file', nargs=-1, type=click.types.Path())
@click.argument('output_file', type=click.types.Path())
def plot_pcas(input_vcf_file,output_file):
    assert len(input_vcf_file)>0, "need to supply vcf file inputs"
    genotypes = [load_file(input_file) for input_file in input_vcf_file]
    genotypes = [np.matrix([np.frombuffer(a,dtype=np.uint8) for a in s]) for s in genotypes]
    plot_PCA(genotypes,output_file)

if __name__ == '__main__':
    plot_pcas()

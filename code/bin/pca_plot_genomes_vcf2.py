#!/usr/bin/env python3
import click
import numpy as np
from sklearn.decomposition import PCA
import matplotlib
import matplotlib.pyplot as plt
from experiment_tools import *

base_colours = ['r','b','g','m','c','w','k'] 

def plot_PCA(sets,output_file):
    #combined_data = np.matrix(sum(sets,[]))
    combined_data = np.matrix(sets[0])
    combined_data = np.asarray(combined_data)
    pca_transform = PCA(n_components=2,svd_solver='full').fit(combined_data)
    fig = plt.figure(figsize = (10,10))
    ax = fig.add_subplot(1,1,1)
    for i,s in enumerate(sets):
        coordinates = pca_transform.transform(s)
        xs = coordinates[:,0]
        ys = coordinates[:,1]
        ax.scatter(xs, ys,c=[base_colours[i] for j in range(len(xs))],s=50,alpha=0.2)
    plt.savefig(output_file)

@click.command()
@click.argument('input_vcf_file', nargs=-1, type=click.types.Path())
@click.argument('output_file', type=click.types.Path())
def plot_pcas(input_vcf_file,output_file):
    assert len(input_vcf_file)>0, "need to supply vcf file inputs"
    genotypes = [parse_VCF_to_genome_strings(input_file)[0] for input_file in input_vcf_file]
    genotypes = [[list(a) for a in s] for s in genotypes]
    plot_PCA(genotypes,output_file)

if __name__ == '__main__':
    plot_pcas()

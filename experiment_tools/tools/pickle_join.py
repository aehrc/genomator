#!/usr/bin/env python3
import click
from tqdm import tqdm
import pickle

@click.command()
@click.argument('output_pickles_file', type=click.types.Path())
@click.argument('pickles', nargs=-1, type=click.types.Path())
def pickles_join(output_pickles_file, pickles):
    print("JOINING PICKLES")
    data = []
    for p in tqdm(pickles):
        with open(p,'rb') as f:
            data.append(pickle.load(f))
    data = sum(data,[])
    print("OUTPUTTING JOINT PICKLE FILE")
    with open(output_pickles_file,"wb") as f:
        pickle.dump(data, f)
    print("DONE JOINT PICKLING")

if __name__ == "__main__":
    pickles_join()


#!/usr/bin/env python3

#generating code adapted from:
#https://gitlab.inria.fr/ml_genetics/public/artificial_genomes
import sys
import numpy as np
import tensorflow.keras as keras
import tensorflow.keras.backend as K
from tensorflow.keras.layers import Input, Dense, Activation, LeakyReLU, BatchNormalization
from tensorflow.keras.models import Sequential
from tensorflow.keras.optimizers import Adam
from sklearn.model_selection import train_test_split
import matplotlib.pyplot as plt
import pandas as pd
from tensorflow.keras.models import load_model
from tensorflow.keras.models import save_model
from tensorflow.keras.models import model_from_json
plt.switch_backend('agg')
from tensorflow.keras import regularizers
from sklearn.decomposition import PCA
from random import shuffle
import tensorflow as tf
from experiment_tools import parse_VCF_to_genome_strings, parse_genome_strings_to_VCF
import pickle
import time
from tensorflow.keras import initializers

import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
import click




def main_GAN(inpt,ag_size,epochs=10001,batch_size=32,gpu_count=0,dump_output_interval=-1,ploidy=2,output_vcf_file="GAN_output",input_vcf_file=None,base_layer_size=800):
    #inpt = "1000G_real_genomes/805_SNP_1000G_real.hapt" #hapt format input file
    latent_size = 400#600 #size of noise input
    alph = 0.01 #alpha value for LeakyReLU
    g_learn = 0.0004 #generator learning rate
    d_learn = 0.0016 #discriminator learning rate
    #epochs = 10001
    #batch_size = 32
    #ag_size = 216 #number of artificial genomes (haplotypes) to be created

    #For saving models
    def save_mod(gan, gen, disc, epo):
        discriminator.trainable = False
        save_model(gan, epo+"_gan")
        discriminator.trainable = True
        save_model(gen, epo+"_generator")
        save_model(disc, epo+"_discriminator")

    #Read input
    shuffle(inpt)
    df = pd.DataFrame([list(a) for a in inpt])
    df_noname = df.values
    #df_noname = df_noname - np.random.uniform(0,0.1, size=(df_noname.shape[0], df_noname.shape[1]))
    df_noname = pd.DataFrame(df_noname)

    K.clear_session()

    generator_shapes = [base_layer_size,base_layer_size]
    discriminator_shapes = [base_layer_size-200,base_layer_size-400]
    
    #Make generator
    generator = Sequential()
    generator.add(Dense(generator_shapes[0], input_shape=(latent_size,), kernel_regularizer=regularizers.l2(0.0001), kernel_initializer=initializers.RandomNormal(stddev=0.01), bias_initializer=initializers.Zeros()))
    generator.add(LeakyReLU(alpha=alph))
    generator.add(Dense(generator_shapes[1], kernel_regularizer=regularizers.l2(0.0001), kernel_initializer=initializers.RandomNormal(stddev=0.01), bias_initializer=initializers.Zeros()))
    generator.add(LeakyReLU(alpha=alph))
    generator.add(Dense(df_noname.shape[1], activation = 'tanh'))

    #Make discriminator
    discriminator = Sequential()
    discriminator.add(Dense(discriminator_shapes[0], input_shape=(df_noname.shape[1],), kernel_regularizer=regularizers.l2(0.0001), kernel_initializer=initializers.RandomNormal(stddev=0.01), bias_initializer=initializers.Zeros()))
    discriminator.add(LeakyReLU(alpha=alph))
    discriminator.add(Dense(discriminator_shapes[1], kernel_regularizer=regularizers.l2(0.0001), kernel_initializer=initializers.RandomNormal(stddev=0.01), bias_initializer=initializers.Zeros()))
    discriminator.add(LeakyReLU(alpha=alph))
    discriminator.add(Dense(1, activation = 'sigmoid'))
    if gpu_count > 1:
        from tensorflow.keras.utils import multi_gpu_model
        discriminator = multi_gpu_model(discriminator, gpus=gpu_count)
    discriminator.compile(optimizer=Adam(learning_rate=d_learn), loss='binary_crossentropy')
    #Set discriminator to non-trainable
    discriminator.trainable = False

    #Make GAN
    gan = Sequential()
    gan.add(generator)
    gan.add(discriminator)
    if gpu_count > 1:
        gan = multi_gpu_model(gan, gpus=gpu_count)
    gan.compile(optimizer=Adam(learning_rate=g_learn), loss='binary_crossentropy')


    y_real, y_fake = np.ones([batch_size, 1]), np.zeros([batch_size, 1])
    X_real = df_noname.values

    batches = len(X_real)//batch_size


    #Training iteration
    for e in range(epochs):
        tf.print(e)
        progbar = tf.keras.utils.Progbar(batches)
        for b in range(batches):
            X_batch_real = X_real[b*batch_size:(b+1)*batch_size] #get the batch from real data
            latent_samples = np.random.normal(loc=0, scale=1, size=(batch_size, latent_size)) #create noise to be fed to generator
            X_batch_fake = generator.predict_on_batch(latent_samples) #create batch from generator using noise as input

            #train discriminator, notice that noise is added to real labels
            discriminator.trainable = True
            #generator.trainable = False
            d_loss = discriminator.train_on_batch(X_batch_real, y_real - np.random.uniform(0,0.1, size=(y_real.shape[0], y_real.shape[1])))
            d_loss += discriminator.train_on_batch(X_batch_fake, y_fake)

            #make discriminator non-trainable and train gan
            discriminator.trainable = False
            #generator.trainable = True
            g_loss = gan.train_on_batch(latent_samples, y_real)
            progbar.add(1)

        #tf.print("Epoch:\t%d/%d Discriminator loss: %6.4f Generator loss: %6.4f"%(e+1, epochs, d_loss, g_loss))
        
        if (((dump_output_interval>0) and (e%dump_output_interval==0))
            or ((dump_output_interval<=0) and (e==epochs-1))):
            #Create AGs
            latent_samples = np.random.normal(loc=0, scale=1, size=(ag_size, latent_size))
            generated_genomes = generator.predict(latent_samples)
            generated_genomes[generated_genomes < 0] = 0
            generated_genomes = np.rint(generated_genomes)
            ss = [bytes([int(aa) for aa in a]) for a in generated_genomes]
            with open("{}{}.pickle".format(output_vcf_file,e), "wb") as f:
                pickle.dump(ss,f)
            #parse_genome_strings_to_VCF(ss,input_vcf_file,"{}{}.vcf".format(output_vcf_file,e),ploidy)









@click.command()
@click.argument('input_vcf_file', type=click.types.Path())
@click.argument('output_vcf_file', type=click.types.Path())
@click.argument('number_of_genomes', type=click.INT, default=1)
@click.option('--epochs', type=click.INT, default=10001)
@click.option('--dump_output_interval', type=click.INT, default=-1)
@click.option('--batch_size', type=click.INT, default=32)
@click.option('--gpu_count', type=click.INT, default=0)
@click.option('--base_layer_size', type=click.INT, default=800)
def GAN_run(input_vcf_file, output_vcf_file, number_of_genomes,epochs,dump_output_interval,batch_size,gpu_count,base_layer_size):
    if input_vcf_file.split(".")[-1]=="pickle":
        with open(input_vcf_file,"rb") as f:
            s,ploidy = pickle.load(f)
    else:
        s,ploidy = parse_VCF_to_genome_strings(input_vcf_file)
    ss = main_GAN(s, number_of_genomes,input_vcf_file=input_vcf_file,output_vcf_file=output_vcf_file,epochs=epochs,batch_size=batch_size,gpu_count=gpu_count,dump_output_interval=dump_output_interval,ploidy=ploidy,base_layer_size=base_layer_size)

if __name__ == '__main__':
    GAN_run()





#!/datasets/work/hb-spiked-genome/work/marks_combine_code_test4/env_virga/bin/python

#generating code adapted from:
#https://gitlab.inria.fr/ml_genetics/public/artificial_genomes
import numpy as np
import keras
import tensorflow as tf
from keras import ops
from tensorflow.keras.layers import Input, Dense, Activation, LeakyReLU, BatchNormalization
from tensorflow.keras.models import Sequential
from tensorflow.keras.optimizers import Adam
#from tensorflow.keras.optimizers.legacy import Adam
import pandas as pd
from tensorflow.keras import regularizers
from random import shuffle
from experiment_tools import parse_VCF_to_genome_strings, parse_genome_strings_to_VCF
import pickle
from tensorflow.keras import initializers

import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
import click



#https://keras.io/examples/generative/dcgan_overriding_train_step/
class GAN(keras.Model):
    def __init__(self, discriminator, generator, latent_dim):
        super().__init__()
        self.discriminator = discriminator
        self.generator = generator
        self.latent_dim = latent_dim
        self.seed_generator = keras.random.SeedGenerator(1337)

    def compile(self, d_optimizer, g_optimizer, loss_fn):
        super().compile()
        self.d_optimizer = d_optimizer
        self.g_optimizer = g_optimizer
        self.loss_fn = loss_fn
        self.d_loss_metric = keras.metrics.Mean(name="d_loss")
        self.g_loss_metric = keras.metrics.Mean(name="g_loss")

    @property
    def metrics(self):
        return [self.d_loss_metric, self.g_loss_metric]

    def train_step(self, real_images):
        batch_size = ops.shape(real_images)[0]
        random_latent_vectors = keras.random.normal(shape=(batch_size, self.latent_dim), seed=self.seed_generator)

        generated_images = self.generator(random_latent_vectors)
        combined_images = ops.concatenate([generated_images, real_images], axis=0)

        labels = ops.concatenate( [ops.ones((batch_size, 1)), ops.zeros((batch_size, 1))], axis=0)
        labels += 0.1 * tf.random.uniform(tf.shape(labels))

        # Train the discriminator
        with tf.GradientTape() as tape:
            predictions = self.discriminator(combined_images)
            d_loss = self.loss_fn(labels, predictions)
        grads = tape.gradient(d_loss, self.discriminator.trainable_weights)
        self.d_optimizer.apply_gradients( zip(grads, self.discriminator.trainable_weights))

        random_latent_vectors = keras.random.normal( shape=(batch_size, self.latent_dim), seed=self.seed_generator)
        misleading_labels = ops.zeros((batch_size, 1))

        # Train the generator
        with tf.GradientTape() as tape:
            predictions = self.discriminator(self.generator(random_latent_vectors))
            g_loss = self.loss_fn(misleading_labels, predictions)
        grads = tape.gradient(g_loss, self.generator.trainable_weights)
        self.g_optimizer.apply_gradients(zip(grads, self.generator.trainable_weights))

        # Update metrics
        self.d_loss_metric.update_state(d_loss)
        self.g_loss_metric.update_state(g_loss)
        return {
            "d_loss": self.d_loss_metric.result(),
            "g_loss": self.g_loss_metric.result(),
        }




class GANMonitor(keras.callbacks.Callback):
    def __init__(self, ag_size, latent_dim, dump_output_interval,output_vcf_file):
        self.ag_size = ag_size
        self.latent_dim = latent_dim
        self.seed_generator = keras.random.SeedGenerator(42)
        self.dump_output_interval = dump_output_interval 
        self.output_vcf_file = output_vcf_file
    def on_epoch_end(self, epoch, logs=None):
        if ((self.dump_output_interval>0) and (epoch % self.dump_output_interval==0)):
            random_latent_vectors = keras.random.normal( shape=(self.ag_size, self.latent_dim), seed=self.seed_generator)
            generated_genomes = self.model.generator(random_latent_vectors).numpy()
            generated_genomes[generated_genomes < 0] = 0
            generated_genomes = np.rint(generated_genomes)
            ss = [bytes([int(aa) for aa in a]) for a in generated_genomes]
            with open("{}{}.pickle".format(self.output_vcf_file,epoch), "wb") as f:
                pickle.dump(ss,f)







def main_GAN(inpt,ag_size,epochs=10001,batch_size=32,gpu_count=0,dump_output_interval=-1,ploidy=2,output_vcf_file="GAN_output",input_vcf_file=None):
    #inpt = "1000G_real_genomes/805_SNP_1000G_real.hapt" #hapt format input file
    latent_dim = 600 #size of noise input
    alph = 0.01 #alpha value for LeakyReLU
    g_learn = 0.0001 #generator learning rate
    d_learn = 0.0008 #discriminator learning rate

    #Read input
    shuffle(inpt)
    df = pd.DataFrame([list(a) for a in inpt])
    df_noname = df.values
    df_noname = df_noname - np.random.uniform(0,0.1, size=(df_noname.shape[0], df_noname.shape[1]))
    df_noname = pd.DataFrame(df_noname)

    dataset = df_noname.values

    #Make generator
    generator = Sequential()
    generator.add(Dense(int(df_noname.shape[1]//1.2), input_shape=(latent_dim,), kernel_regularizer=regularizers.l2(0.0001), kernel_initializer=initializers.RandomNormal(stddev=0.01), bias_initializer=initializers.Zeros()))
    generator.add(LeakyReLU(alpha=alph))
    generator.add(Dense(int(df_noname.shape[1]//1.1), kernel_regularizer=regularizers.l2(0.0001), kernel_initializer=initializers.RandomNormal(stddev=0.01), bias_initializer=initializers.Zeros()))
    generator.add(LeakyReLU(alpha=alph))
    generator.add(Dense(df_noname.shape[1], activation = 'tanh'))

    #Make discriminator
    discriminator = Sequential()
    discriminator.add(Dense(df_noname.shape[1]//2, input_shape=(df_noname.shape[1],), kernel_regularizer=regularizers.l2(0.0001), kernel_initializer=initializers.RandomNormal(stddev=0.01), bias_initializer=initializers.Zeros()))
    discriminator.add(LeakyReLU(alpha=alph))
    discriminator.add(Dense(df_noname.shape[1]//3, kernel_regularizer=regularizers.l2(0.0001), kernel_initializer=initializers.RandomNormal(stddev=0.01), bias_initializer=initializers.Zeros()))
    discriminator.add(LeakyReLU(alpha=alph))
    discriminator.add(Dense(1, activation = 'sigmoid'))

    gan = GAN(discriminator=discriminator, generator=generator, latent_dim=latent_dim)
    gan.compile( d_optimizer=keras.optimizers.Adam(learning_rate=d_learn), g_optimizer=keras.optimizers.Adam(learning_rate=g_learn), loss_fn=keras.losses.BinaryCrossentropy(),)
    gan.fit( dataset, epochs=epochs, callbacks=[GANMonitor(ag_size, latent_dim, dump_output_interval,output_vcf_file)], batch_size=batch_size)









@click.command()
@click.argument('input_vcf_file', type=click.types.Path())
@click.argument('output_vcf_file', type=click.types.Path())
@click.argument('number_of_genomes', type=click.INT, default=1)
@click.option('--epochs', type=click.INT, default=10001)
@click.option('--dump_output_interval', type=click.INT, default=-1)
@click.option('--batch_size', type=click.INT, default=32)
@click.option('--gpu_count', type=click.INT, default=0)
def GAN_run(input_vcf_file, output_vcf_file, number_of_genomes,epochs,dump_output_interval,batch_size,gpu_count):
    if input_vcf_file.split(".")[-1]=="pickle":
        with open(input_vcf_file,"rb") as f:
            s,ploidy = pickle.load(f)
    else:
        s,ploidy = parse_VCF_to_genome_strings(input_vcf_file)
    ss = main_GAN(s, number_of_genomes,input_vcf_file=input_vcf_file,output_vcf_file=output_vcf_file,epochs=epochs,batch_size=batch_size,gpu_count=gpu_count,dump_output_interval=dump_output_interval,ploidy=ploidy)

if __name__ == '__main__':
    GAN_run()





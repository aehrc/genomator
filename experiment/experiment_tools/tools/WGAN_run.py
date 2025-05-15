#!/usr/bin/env python3


#generating code adapted from:
#https://gitlab.inria.fr/ml_genetics/public/artificial_genomes

import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np

##Class defining type of blocks
class Block(nn.Module):
    def __init__(self, channels, mult, block_type, sampling, noise_dim=None, alph=0.01):
        super().__init__()

        if block_type=="g" and sampling == 1:
            self.block = nn.Sequential(
                nn.Conv1d(channels*mult + noise_dim + 1, channels*(mult-2), 3, stride = 1, padding=1, bias=False),
                nn.BatchNorm1d(channels*(mult-2)),
                nn.LeakyReLU(alph),

                nn.ConvTranspose1d(channels*(mult-2), channels*(mult-4), 3, stride = 2, padding=0, bias=False),
                nn.BatchNorm1d(channels*(mult-4)),
                nn.LeakyReLU(alph),

                nn.Conv1d(channels*(mult-4), channels*(mult-6), 3, stride = 1, padding=1, bias=False),
                nn.BatchNorm1d(channels*(mult-6)),
                nn.LeakyReLU(alph),

                nn.ConvTranspose1d(channels*(mult-6), channels*(mult-8), 3, stride = 2, padding=0, bias=False),
                nn.BatchNorm1d(channels*(mult-8)),
                nn.LeakyReLU(alph))

        elif block_type=="d" and sampling == -1:
            self.block = nn.Sequential(
                nn.Conv1d(channels*mult + 1, channels*(mult+2), 3, stride = 1, padding=1),
                nn.InstanceNorm1d(channels*(mult+2), affine=True),
                nn.LeakyReLU(alph),

                nn.Conv1d(channels*(mult+2), channels*(mult+4), 3, stride = 2, padding=0),
                nn.InstanceNorm1d(channels*(mult+4), affine=True),
                nn.LeakyReLU(alph),

                nn.Conv1d(channels*(mult+4), channels*(mult+6), 3, stride = 1, padding=1),
                nn.InstanceNorm1d(channels*(mult+6), affine=True),
                nn.LeakyReLU(alph),

                nn.Conv1d(channels*(mult+6), channels*(mult+8), 3, stride = 2, padding=0),
                nn.InstanceNorm1d(channels*(mult+8), affine=True),
                nn.LeakyReLU(alph))

        elif block_type=="d" and sampling == 0:
            self.block = nn.Sequential(
                nn.Conv1d(channels*mult, channels*mult, 3, stride = 1, padding=1),
                nn.InstanceNorm1d(channels*mult, affine=True),
                nn.LeakyReLU(alph),

                nn.Conv1d(channels*mult, channels*mult, 3, stride = 1, padding=1),
                nn.InstanceNorm1d(channels*mult, affine=True),
                nn.LeakyReLU(alph))

        elif block_type=="g" and sampling == 0:
            self.block = nn.Sequential(
                nn.Conv1d(channels*mult, channels*mult, 3, stride = 1, padding=1, bias=False),
                nn.BatchNorm1d(channels*mult),
                nn.LeakyReLU(alph),

                nn.Conv1d(channels*mult, channels*mult, 3, stride = 1, padding=1, bias=False),
                nn.BatchNorm1d(channels*mult),
                nn.LeakyReLU(alph))

    def forward(self, x):
        return self.block(x)



class ConvGenerator(nn.Module):
    def __init__(self, latent_size, data_shape, gpu, device, channels, noise_dim, alph):
        super(ConvGenerator, self).__init__()

        #parameters initialization
        self.channels = channels
        self.latent_size = latent_size
        self.alph = alph
        self.gpu = gpu
        self.data_shape = data_shape
        self.device = device
        self.noise_dim = noise_dim

        #Location-specific trainable variables
        self.ms_vars = nn.ParameterList()
        self.ms_vars.append(nn.Parameter(torch.normal(mean=0, std=1, size=(1, latent_size))))
        for i in range(2,15,2):
            self.ms_vars.append(nn.Parameter(torch.normal(mean=0, std=1, size=(1, latent_size*(2**i)-1))))

        #Blocks
        self.block1 = nn.Sequential(
                    nn.Conv1d(noise_dim + 1, self.channels*52, 3, stride = 1, padding=1, bias=False),
                    nn.BatchNorm1d(self.channels*52),
                    nn.LeakyReLU(alph),

                    nn.ConvTranspose1d(self.channels*52, self.channels*50, 3, stride = 2, padding=1, bias=False),
                    nn.BatchNorm1d(self.channels*50),
                    nn.LeakyReLU(alph),

                    nn.Conv1d(self.channels*50, self.channels*48, 3, stride = 1, padding=1, bias=False),
                    nn.BatchNorm1d(self.channels*48),
                    nn.LeakyReLU(alph),

                    nn.ConvTranspose1d(self.channels*48, self.channels*46, 3, stride = 2, padding=0, bias=False),
                    nn.BatchNorm1d(self.channels*46),
                    nn.LeakyReLU(alph),
        )
        self.block2 = Block(channels = self.channels, mult = 46, block_type = "g", sampling = 1, noise_dim = self.noise_dim)
        self.block3 = Block(channels = self.channels, mult = 38, block_type = "g", sampling = 0, noise_dim = self.noise_dim)
        self.block4 = Block(channels = self.channels, mult = 38, block_type = "g", sampling = 1, noise_dim = self.noise_dim)
        self.block5 = Block(channels = self.channels, mult = 30, block_type = "g", sampling = 1, noise_dim = self.noise_dim)
        self.block6 = Block(channels = self.channels, mult = 22, block_type = "g", sampling = 0, noise_dim = self.noise_dim)
        self.block7 = Block(channels = self.channels, mult = 22, block_type = "g", sampling = 1, noise_dim = self.noise_dim)
        self.block8 = Block(channels = self.channels, mult = 14, block_type = "g", sampling = 1, noise_dim = self.noise_dim)
        self.block9 = Block(channels = self.channels, mult = 6, block_type = "g", sampling = 0, noise_dim = self.noise_dim)
        self.block10 = nn.Sequential(
                    nn.Conv1d(self.channels * 6 + noise_dim + 1, self.channels * 4, 3, stride=1, padding=1, bias=False),
                    nn.BatchNorm1d(self.channels*4),
                    nn.LeakyReLU(alph),

                    nn.ConvTranspose1d(self.channels * 4, self.channels * 2, 3, stride=2, padding=0, bias=False),
                    nn.BatchNorm1d(self.channels*2),
                    nn.LeakyReLU(alph),

                    nn.Conv1d(self.channels * 2, self.channels * 1, 3, stride=1, padding=1, bias=False),
                    nn.BatchNorm1d(self.channels*1),
                    nn.LeakyReLU(alph),

                    nn.ConvTranspose1d(self.channels * 1, (self.channels * 1)//2, 3, stride=2, padding=0, bias=False),
                    nn.BatchNorm1d((self.channels * 1)//2),
                    nn.LeakyReLU(alph),
        )
        self.block11 = nn.Sequential(
                    nn.Conv1d((self.channels * 1)//2 + 1, 1, 3, stride=1, padding=1),
                    nn.Sigmoid()
        )

    def forward(self, x, noise_list):
        batch_size = x.shape[0]
        x = torch.cat((self.ms_vars[0].repeat(batch_size,1)[:,np.newaxis,:], x), 1)
        x = self.block1(x)

        x = torch.cat((self.ms_vars[1].repeat(batch_size,1)[:,np.newaxis,:], x), 1)
        x = torch.cat((noise_list[0], x), 1)
        x = self.block2(x)

        res = x
        x = self.block3(x)
        x += res

        x = torch.cat((self.ms_vars[2].repeat(batch_size,1)[:,np.newaxis,:], x), 1)
        x = torch.cat((noise_list[1], x), 1)
        x = self.block4(x)

        x = torch.cat((self.ms_vars[3].repeat(batch_size,1)[:,np.newaxis,:], x), 1)
        x = torch.cat((noise_list[2], x), 1)
        x = self.block5(x)

        res = x
        x = self.block6(x)
        x += res

        x = torch.cat((self.ms_vars[4].repeat(batch_size,1)[:,np.newaxis,:], x), 1)
        x = torch.cat((noise_list[3], x), 1)
        x = self.block7(x)

        x = torch.cat((self.ms_vars[5].repeat(batch_size,1)[:,np.newaxis,:], x), 1)
        x = torch.cat((noise_list[4], x), 1)
        x = self.block8(x)

        res = x
        x = self.block9(x)
        x += res

        x = torch.cat((self.ms_vars[6].repeat(batch_size,1)[:,np.newaxis,:], x), 1)
        x = torch.cat((noise_list[5], x), 1)
        x = self.block10(x)

        x = torch.cat((self.ms_vars[7].repeat(batch_size,1)[:,np.newaxis,:], x), 1)
        x = self.block11(x)

        return x


class ConvDiscriminator(nn.Module):
    def __init__(self, data_shape, latent_size, gpu, device, pack_m, channels, alph):
        super(ConvDiscriminator, self).__init__()

        #parameters initialization
        self.alph = alph
        self.data_shape = data_shape
        self.channels = channels
        self.gpu = gpu
        self.device = device
        self.pack_m = pack_m

        #Location-specific trainable variables
        self.ms_vars = nn.ParameterList()
        for i in range(14,1,-2):
            self.ms_vars.append(nn.Parameter(torch.normal(mean=0, std=1, size=(1, latent_size*(2**i)-1))))

        #Blocks
        self.block1 = nn.Sequential(
                    nn.Conv1d(1 * pack_m + 1, self.channels * 1, 3, stride=1, padding=1),
                    nn.InstanceNorm1d(self.channels*1, affine=True),
                    nn.LeakyReLU(alph),

                    nn.Conv1d(self.channels * 1, self.channels * 2, 3, stride=2, padding=0),
                    nn.InstanceNorm1d(self.channels*2, affine=True),
                    nn.LeakyReLU(alph),

                    nn.Conv1d(self.channels * 2, self.channels * 4, 3, stride=1, padding=1),
                    nn.InstanceNorm1d(self.channels*4, affine=True),
                    nn.LeakyReLU(alph),

                    nn.Conv1d(self.channels * 4, self.channels * 6, 3, stride=2, padding=0),
                    nn.InstanceNorm1d(self.channels*6, affine=True),
                    nn.LeakyReLU(alph),
        )
        self.block2 = Block(channels = self.channels, mult = 6, block_type = "d", sampling = 0)
        self.block3 = Block(channels = self.channels, mult = 6, block_type = "d", sampling = -1)
        self.block4 = Block(channels = self.channels, mult = 14, block_type = "d", sampling = -1)
        self.block5 = Block(channels = self.channels, mult = 22, block_type = "d", sampling = 0)
        self.block6 = Block(channels = self.channels, mult = 22, block_type = "d", sampling = -1)
        self.block7 = Block(channels = self.channels, mult = 30, block_type = "d", sampling = -1)
        self.block8 = Block(channels = self.channels, mult = 38, block_type = "d", sampling = 0)
        self.block9 = Block(channels = self.channels, mult = 38, block_type = "d", sampling = -1)
        self.block10 = nn.Sequential(
                    nn.Conv1d(self.channels * 46 + 1, self.channels * 48, 3, stride=1, padding=1),
                    nn.InstanceNorm1d(self.channels * 48, affine=True),
                    nn.LeakyReLU(alph),

                    nn.Conv1d(self.channels * 48, self.channels * 50, 3, stride=2, padding=0),
                    nn.InstanceNorm1d(self.channels*50, affine=True),
                    nn.LeakyReLU(alph),

                    nn.Conv1d(self.channels * 50, self.channels * 52, 3, stride=1, padding=1),
                    nn.InstanceNorm1d(self.channels * 52, affine=True),
                    nn.LeakyReLU(alph),

                    nn.Conv1d(self.channels * 52, 1, 3, stride=2, padding=1),
                    nn.InstanceNorm1d(1, affine=True),
                    nn.LeakyReLU(alph),

                    nn.Linear(latent_size, 1)
        )

    def forward(self, x):
        batch_size = x.shape[0]
        x = torch.cat((self.ms_vars[0].repeat(batch_size,1)[:,np.newaxis,:], x), 1)
        x = self.block1(x)

        res = x
        x = self.block2(x)
        x += res

        x = torch.cat((self.ms_vars[1].repeat(batch_size,1)[:,np.newaxis,:], x), 1)
        x = self.block3(x)

        x = torch.cat((self.ms_vars[2].repeat(batch_size,1)[:,np.newaxis,:], x), 1)
        x = self.block4(x)

        res = x
        x = self.block5(x)
        x += res

        x = torch.cat((self.ms_vars[3].repeat(batch_size,1)[:,np.newaxis,:], x), 1)
        x = self.block6(x)

        x = torch.cat((self.ms_vars[4].repeat(batch_size,1)[:,np.newaxis,:], x), 1)
        x = self.block7(x)

        res = x
        x = self.block8(x)
        x += res

        x = torch.cat((self.ms_vars[5].repeat(batch_size,1)[:,np.newaxis,:], x), 1)
        x = self.block9(x)

        x = torch.cat((self.ms_vars[6].repeat(batch_size,1)[:,np.newaxis,:], x), 1)
        x = self.block10(x)

        return x

def gradient_penalty(netC, X_real_batch, X_fake_batch, device):
    batch_size, nb_snps= X_real_batch.shape[0], X_real_batch.shape[2]
    alpha = torch.rand(batch_size,1, device=device).repeat(1, nb_snps)
    alpha = alpha.reshape(alpha.shape[0], 1, alpha.shape[1])
    interpolation = (alpha*X_real_batch) + (1-alpha) * X_fake_batch
    interpolation = interpolation.float()

    interpolated_score= netC(interpolation)

    gradient= torch.autograd.grad(inputs=interpolation,
                                  outputs=interpolated_score,
                                  retain_graph=True,
                                  create_graph=True,
                                  grad_outputs=torch.ones_like(interpolated_score)
                                 )[0]
    gradient= gradient.view(gradient.shape[0],-1)
    gradient_norm= gradient.norm(2,dim=1)
    gradient_penalty=torch.mean((gradient_norm-1)**2)

    gradient_penalty *= 10
    return gradient_penalty






import sys
import numpy as np
#from tensorflow.keras.optimizers import Adam
from tensorflow.keras.optimizers.legacy import Adam
import pandas as pd
from random import shuffle
import random
import tensorflow as tf
from experiment_tools import parse_VCF_to_genome_strings, parse_genome_strings_to_VCF
import pickle
import time
#from models_65K import * #models_10K for 16383 zero padded SNP data

import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
import click



def main_WGAN(inpt,ag_size,epochs=10001,batch_size=96,dump_output_interval=-1,ploidy=2,output_vcf_file="GAN_output",input_vcf_file=None,base_layer_size=800):
    out_dir = "./output_dir"
    alph = 0.01 #alpha value for LeakyReLU
    g_learn = 0.0005 #generator learning rate
    d_learn = 0.0005 #discriminator learning rate
    #epochs = 10001
    #batch_size = 96
    channels = 10 #channel multiplier which dictates the number of channels for all layers
    #ag_size = 500 #number of artificial genomes (haplotypes) to be created
    gpu = 1 #number of GPUs
    save_that = 50 #epoch interval for saving outputs
    pack_m = 1 #3 #packing amount for the critic
    critic_iter = 10 #number of times critic is trained for every generator training
    label_noise = 1 #noise for real labels (1: noise, 0: no noise)
    noise_dim = 2 #dimension of noise for each noise vector
    latent_depth_factor = 14 #14 for 65535 SNP data and 12 for 16383 zero padded SNP data

    device = torch.device("cuda:0" if (torch.cuda.is_available() and gpu > 0) else "cpu") #set device to cpu or gpu

    #Read input
    shuffle(inpt)
    df = pd.DataFrame([list(a) for a in inpt])
    df_noname = df.values
    #df_noname = df_noname - np.random.uniform(0,0.1, size=(df_noname.shape[0], df_noname.shape[1]))
    #df_noname = pd.DataFrame(df_noname)


    #df_noname = df_noname - np.random.uniform(0,0.1, size=(df_noname.shape[0], df_noname.shape[1]))
    df = df.iloc[0:ag_size,:]
    df_noname = torch.Tensor(df_noname)
    df_noname = df_noname.to(device)
    dataloader = torch.utils.data.DataLoader(df_noname, batch_size=batch_size, shuffle=True, pin_memory=False)

    latent_size = int((df_noname.shape[1]+1)/(2**latent_depth_factor)) #set the latent_size

    ## Create the generator
    netG = ConvGenerator(latent_size=latent_size, data_shape=df_noname.shape[1], gpu=gpu, device=device, channels=channels, noise_dim=noise_dim, alph=alph)
    netG = netG.float()
    if (device.type == 'cuda') and (gpu > 1):
        netG = nn.DataParallel(netG, list(range(gpu)))
    netG.to(device)

    ## Create the critic
    netC = ConvDiscriminator(data_shape=df_noname.shape[1], latent_size=latent_size, gpu=gpu, pack_m = pack_m, device=device, channels=channels, alph=alph).to(device)
    netC = netC.float()
    if (device.type == 'cuda') and (gpu > 1):
        netC = nn.DataParallel(netC, list(range(gpu)))
    netC.to(device)

    ## Optimizers for generator and critic
    c_optimizer = torch.optim.Adam(netC.parameters(), lr=d_learn, betas=(0.5, 0.9))
    g_optimizer = torch.optim.Adam(netG.parameters(), lr=g_learn, betas=(0.5, 0.9))

    label_fake = torch.tensor(1, dtype=torch.float).to(device)
    label_real = label_fake * -1
    losses = []

    ## Noise generator function to be used to provide input noise vectors
    def noise_generator(size, noise_count, noise_dim, device):
        noise_list = []
        for i in range(2,noise_count*2+1,2):
            noise = torch.normal(mean=0, std=1, size=(size, noise_dim, latent_size*(2**i)-1), device = device)
            noise_list.append(noise)
        return noise_list

    ## Training Loop
    print("Starting Training Loop...")
    start_time = time.time()
    for epoch in range(epochs):
        #c_loss_real = 0
        #c_loss_fake = 0
        print(f"epoch number {epoch}")


        b = 0

        while b < len(dataloader):
            for param in netC.parameters():
                param.requires_grad = True

            #Update Critic
            for n_critic in range(critic_iter):

                netC.zero_grad(set_to_none=True)

                X_batch_real = next(iter(dataloader))
                X_batch_real = torch.reshape(X_batch_real, (X_batch_real.shape[0], 1, X_batch_real.shape[1]))

                if pack_m > 1:
                    for i in range(pack_m-1):
                        temp_batch = next(iter(dataloader))
                        temp_batch = torch.reshape(temp_batch, (temp_batch.shape[0], 1, temp_batch.shape[1]))
                        X_batch_real = torch.cat((X_batch_real, temp_batch), 1)
                b += 1

                #Train Critic with real samples
                c_loss_real = netC(X_batch_real.float())
                c_loss_real = c_loss_real.mean()

                if label_noise != 0:
                    label_noise = torch.tensor(random.uniform(0, 0.1), dtype=torch.float, device=device)
                    c_loss_real.backward(label_real + label_noise)
                else:
                    c_loss_real.backward(label_real)

                for i in range(pack_m):
                    latent_samples = torch.normal(mean=0, std=1, size=(batch_size, noise_dim, latent_size), device=device) #create the initial noise to be fed to generator
                    noise_list = noise_generator(batch_size, 6, noise_dim, device)
                    temp = netG(latent_samples, noise_list)
                    if i == 0:
                        X_batch_fake = temp
                    else:
                        X_batch_fake = torch.cat((X_batch_fake, temp), 1)

                c_loss_fake = netC(X_batch_fake.detach())
                c_loss_fake = c_loss_fake.mean()
                c_loss_fake.backward(label_fake)

                #Train with gradient penalty
                gp = gradient_penalty(netC, X_batch_real.float(), X_batch_fake.float(), device)
                gp.backward()
                c_loss = c_loss_fake - c_loss_real + gp
                c_optimizer.step()


            for param in netC.parameters():
                param.requires_grad = False

            #Update G network
            netG.zero_grad(set_to_none=True)
            for i in range(pack_m):
                latent_samples = torch.normal(mean=0, std=1, size=(batch_size, noise_dim, latent_size), device=device) #create the initial noise to be fed to generator
                noise_list = noise_generator(batch_size, 6, noise_dim, device)
                temp = netG(latent_samples, noise_list)
                if i == 0:
                    X_batch_fake = temp
                else:
                    X_batch_fake = torch.cat((X_batch_fake, temp), 1)

            g_loss = netC(X_batch_fake)
            g_loss = g_loss.mean()
            g_loss.backward(label_real)
            g_optimizer.step()

            # Save Losses for plotting later
            #losses.append((c_loss.item(), g_loss.item()))
            losses.append((round(c_loss.item(), 3), (round(g_loss.item(), 3))))

        ## Outputs for assessment at every "save_that" epoch
        if (((dump_output_interval>0) and (epoch%dump_output_interval==0))
            or ((dump_output_interval<=0) and (epoch==epochs-1))):
            #Create AGs

            netG.eval()
            latent_samples = torch.normal(mean=0, std=1, size=(ag_size, noise_dim, latent_size), device=device) #create the initial noise to be fed to generator
            noise_list = noise_generator(ag_size, 6, noise_dim, device)
            with torch.no_grad():
                generated_genomes = netG(latent_samples, noise_list)
            generated_genomes = generated_genomes.cpu().detach().numpy()
            generated_genomes[generated_genomes < 0] = 0
            generated_genomes = np.rint(generated_genomes)
            ss = [bytes([int(aa) for aa in a[0]]) for a in generated_genomes]
            with open("{}{}.pickle".format(output_vcf_file,epoch), "wb") as f:
                pickle.dump(ss,f)
            #parse_genome_strings_to_VCF(ss,input_vcf_file,"{}{}.vcf".format(output_vcf_file,e),ploidy)
            netG.train()




        









@click.command()
@click.argument('input_vcf_file', type=click.types.Path())
@click.argument('output_vcf_file', type=click.types.Path())
@click.argument('number_of_genomes', type=click.INT, default=1)
@click.option('--epochs', type=click.INT, default=10001)
@click.option('--dump_output_interval', type=click.INT, default=-1)
@click.option('--batch_size', type=click.INT, default=32)
@click.option('--base_layer_size', type=click.INT, default=800)
def WGAN_run(input_vcf_file, output_vcf_file, number_of_genomes,epochs,dump_output_interval,batch_size,base_layer_size):
    if input_vcf_file.split(".")[-1]=="pickle":
        with open(input_vcf_file,"rb") as f:
            s,ploidy = pickle.load(f)
    else:
        s,ploidy = parse_VCF_to_genome_strings(input_vcf_file)
    ss = main_WGAN(s, number_of_genomes,input_vcf_file=input_vcf_file,output_vcf_file=output_vcf_file,epochs=epochs,batch_size=batch_size,dump_output_interval=dump_output_interval,ploidy=ploidy,base_layer_size=base_layer_size)

if __name__ == '__main__':
    WGAN_run()





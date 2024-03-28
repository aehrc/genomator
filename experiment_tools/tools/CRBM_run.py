#!/usr/bin/env python3


#generating code adapted from:
#https://gitlab.inria.fr/ml_genetics/public/artificial_genomes


from ssl import ALERT_DESCRIPTION_HANDSHAKE_FAILURE
import torch
import h5py
import numpy as np
from scipy.integrate import simps
import matplotlib.pyplot as plt
from tqdm import tqdm
import pickle

class CRBM:
    # NEEDED VAR:
    # * num_visible
    # * num_hidden
    def __init__(self, num_visible, # number of visible nodes
                 num_hidden, # number of hidden nodes
                 device, # CPU or GPU ?
                 gibbs_steps=10, # number of MCMC steps for computing the neg term
                 anneal_steps=0,# number of MCMC steps for computing the neg term when doing anneal (= for no annealing)
                 var_init=1e-4, # variance of the init weights
                 dtype=torch.float,
                 num_pcd = 100, # number of permanent chains
                 lr = 0.01, # learning rate
                 ep_max = 100, # number of epochs
                 mb_s = 50, # size of the minibatch
                 sampler_name = "SIG", # type of activation function : SIG|RELU_MAX|...
                 ann_threshold = 4, # threshold (of the max value of the spectrum of w) above which, the annealing is used 
                 regL2 = 0, # value of the L2 regularizer
                 DynBetaGradient = False, # Activate the temperature for the gradient descent
                 UpdFieldsVis = True, # Update visible fields ?
                 UpdFieldsHid = True, # Update hidden fields ?
                 UpdWeights = True, # Update the weights ?
                 UpdCentered = False, # Update using centered gradients
                 CDLearning = False
                 ): 
        self.Nv = num_visible        
        self.Nh = num_hidden
        self.Nh2 = 0
        self.Ns = -1
        self.gibbs_steps = gibbs_steps
        self.anneal_steps = anneal_steps
        self.device = device
        self.dtype = dtype
        # weight of the RBM
        self.W = torch.randn(size=(self.Nh,self.Nv), device=self.device, dtype=self.dtype)*var_init
        self.W2 = torch.zeros(size=(self.Nh,self.Nv), device=self.device, dtype=self.dtype)
        self.var_init = var_init
        # visible and hidden biases
        self.vbias = torch.zeros(self.Nv, device=self.device, dtype=self.dtype)
        self.hbias = torch.zeros(self.Nh, device=self.device, dtype=self.dtype)
        self.vbias_prior = torch.zeros(self.Nv, device=self.device)
        # permanent chain
        self.X_pc = torch.bernoulli(torch.rand((self.Nv,num_pcd), device=self.device, dtype=self.dtype))
        self.OnlineAIS_V = 0
        self.OnlineAIS_H = 0 
        self.NbUpdZ = 100
        self.lr = lr
        self.ep_max = ep_max
        self.mb_s = mb_s
        self.num_pcd = num_pcd
        self.sampler_name = sampler_name
        self.SamplerHiddens = self.SampleHiddens01
        self.SamplerVisibles = self.SampleVisibles01
        self.ann_threshold = ann_threshold
        # effective temperature
        self.β = 1
        self.ep_tot = 0
        self.up_tot = 0
        self.list_save_time = []
        self.list_save_rbm = []
        self.regL2 = regL2
        self.UpdFieldsVis = UpdFieldsVis
        self.UpdFieldsHid = UpdFieldsHid
        self.UpdWeights = UpdWeights
        self.file_stamp = ''
        self.UpdWα = False
        self.VisDataAv = 0
        self.HidDataAv = 0
        self.UpdCentered = UpdCentered
        self.ResetPermChainBatch = False
        self.FIT_MF = False
        self.FIT_TAP = False
        self.CDLearning = CDLearning
        self.M_data = 0
        self.H_STATE = 0
        self.V_STATE = 0
        self.FixNodes = 5000

    def SetTrueMean(self,X):
        self.M_data = torch.mean(X,1)

    def saveRBM(self,fname):
        f = h5py.File(fname,'w')
        f.create_dataset('W',data=self.W.cpu())
        f.create_dataset('hbias',data=self.hbias.cpu())
        f.create_dataset('vbias',data=self.vbias.cpu())
        f.create_dataset('X_pc',data=self.X_pc.cpu())
        f.close()


    def loadRBM(self,fname,stamp='',PCD=False):
        f = h5py.File(fname,'r')
        self.W = torch.tensor(f['W'+stamp]); 
        self.vbias = torch.tensor(f['vbias'+stamp]); 
        self.hbias = torch.tensor(f['hbias'+stamp]); 
        self.Nv = self.W.shape[1]
        self.Nh = self.W.shape[0]
        if PCD:
            self.X_pc = torch.tensor(f['X_pc']+stamp); 
        if self.device.type != "cpu":
            self.W = self.W.cuda()
            self.vbias = self.vbias.cuda()
            self.hbias = self.hbias.cuda()
            if PCD:
                self.X_pc = self.X_pc.cuda()


    def ImConcat(self,X,ncol=10,nrow=5,sx=28,sy=28,ch=1):
        tile_X = []
        for c in range(nrow):
            L = torch.cat((tuple(X[i,:].reshape(sx,sy,ch) for i in np.arange(c*ncol,(c+1)*ncol))))
            tile_X.append(L)
        return torch.cat(tile_X,1)


    # X is Nv x Ns
    # return the free energy of all samples -log(p(x))
    def FreeEnergy(self, X):
        vb = torch.sum(X.t() * self.vbias,1) # vb: Ns
        fe_exp = 1 + torch.exp(self.W.mm(X).t() + self.hbias) # fe_exp: Ns x Nh
        Wx_b_log = torch.sum( torch.log(fe_exp),1) # Wx_b_log: Ns
        result = - vb - Wx_b_log # result: Ns
        return result

    # V is Nv x Ns x NT
    # H is Nh x Ns x NT
    # E is Ns x NT
    def computeE(self,V,H):
        INT = torch.sum((H * torch.tensordot(self.W,V,dims=1)),0)
        FIELDS = torch.tensordot(self.hbias,H,dims=1) +  torch.tensordot(self.vbias,V,dims=1)
        return -(INT + FIELDS)

    def computeE_prior(self,V):
        FIELDS = torch.tensordot(self.vbias_prior,V,dims=1)
        return -(FIELDS)    

    def ComputeFE(self,nβ=1000,NS=1000):
        FE_RATIO_AIS_PRIOR = self.ComputeFreeEnergyAISPrior(nβ,NS)
        FE_RATIO_AIS = self.ComputeFreeEnergyAIS(nβ,NS)
        FE_PRIOR = self.ComputeFreeEnergyPrior()

        return FE_PRIOR,FE_RATIO_AIS,FE_RATIO_AIS_PRIOR

    # return Ln[ Z_0 ]
    def ComputeFreeEnergyPrior(self):
        return torch.sum(torch.log(1 + torch.exp(self.vbias_prior))) + self.Nh*torch.log(torch.tensor(2.0))

    def ComputeFreeEnergyAIS(self,nβ,nI):

        βlist = torch.arange(0,1.000001,1.0/nβ)
        x = torch.zeros(self.Nv+self.Nh2,nI,device=self.device)
        H = torch.zeros(self.Nh,nI,device=self.device)
        E = torch.zeros(nI,device=self.device)

        # initialize xref
        x = torch.bernoulli(torch.sigmoid(self.vbias_prior).repeat(nI,1).t())
        H = torch.bernoulli(torch.rand((self.Nh,nI),device=self.device))
        E = self.computeE(x,H).double().to(self.device)  - self.computeE_prior(x)
        self.V_STATE = x
        self.H_STATE = H
        for idβ in tqdm(range(1,nβ+1)):
            H, _ = self.SamplerHiddens(x,β=βlist[idβ])
            x, _ = self.SampleVisibles01(H,β=βlist[idβ])
            E += self.computeE(x,H)

        Δ = 0
        Δβ = 1.0/nβ
        Δ = -Δβ*E # torch.sum(E,1)

        Δ = Δ.double()
        Δ0 = torch.mean(Δ)

        AIS = torch.log(torch.mean(torch.exp(Δ-Δ0).double()))+Δ0
        return AIS

    def ComputeFreeEnergyAISPrior(self,nβ,nI):

        βlist = torch.arange(0,1.000001,1.0/nβ)
        x = torch.zeros(self.Nv+self.Nh2,nI,device=self.device)
        H = torch.zeros(self.Nh,nI,device=self.device)
        E = torch.zeros(nI,device=self.device)

        # initialize xref
        x = torch.bernoulli(torch.sigmoid(self.vbias_prior).repeat(nI,1).t())
        H = torch.bernoulli(torch.rand((self.Nh,nI),device=self.device))
        E = self.computeE(x,H).double().to(self.device)  - self.computeE_prior(x)
        self.V_STATE = x
        self.H_STATE = H
        for idβ in tqdm(range(1,nβ+1)):
            H, _ = self.SamplerHiddens(x,β=βlist[idβ])
            x, _ = self.SampleVisibles01PT_priorSingle(H,β=βlist[idβ])
            E += self.computeE(x,H) - self.computeE_prior(x)

        Δ = 0
        Δβ = 1.0/nβ
        Δ = -Δβ*E 
        Δ = Δ.double()
        Δ0 = torch.mean(Δ)

        AIS = torch.log(torch.mean(torch.exp(Δ-Δ0).double()))+Δ0
        return AIS

    def ComputeAATS(self,X,fake_X,s_X):
        CONCAT = torch.cat((X[:,:s_X],fake_X[:,:s_X]),1)
        dAB = torch.cdist(CONCAT.t(),CONCAT.t())    
        torch.diagonal(dAB).fill_(float('inf'))
        dAB = dAB.cpu().numpy()

        # the next line is use to tranform the matrix into
        #  d_TT d_TF   INTO d_TF- d_TT-  where the minus indicate a reverse order of the columns
        #  d_FT d_FF        d_FT  d_FF
        dAB[:int(dAB.shape[0]/2),:] = dAB[:int(dAB.shape[0]/2),::-1] 

        closest = dAB.argmin(axis=1) 
        for i in range(closest.shape[0]):
            s = (len(np.where(dAB[i,:]==closest[i])))
            if s>1:
                print('multiple min=',s)
        n = int(closest.shape[0]/2)

        ninv = 1/n
        correctly_classified = closest>=n  
        AAtruth = (closest[:n] >= n).sum()*ninv  # for a true sample, proba that the closest is in the set of true samples
        AAsyn = (closest[n:] >= n).sum()*ninv  # for a fake sample, proba that the closest is in the set of fake samples

        return AAtruth, AAsyn

    # init the visible bias using the empirical frequency of the training dataset
    def SetVisBias(self,X,εcrop=1e-5):
        NS = X.shape[1]
        prob1 = torch.sum(X,1)/NS
        prob1 = torch.clamp(prob1,min=εcrop)
        prob1 = torch.clamp(prob1,max=1-εcrop)
        self.vbias = -torch.log(1.0/prob1 - 1.0)

    def SetPriorBias(self,X):
        NS = X.shape[1]
        prob1 = torch.sum(X,1)/NS
        prob1 = torch.clamp(prob1,min=1e-5)
        prob1 = torch.clamp(prob1,max=1-1e-5)
        self.vbias_prior = -torch.log(1.0/prob1 - 1.0)


    # SetSample: change de sampler used for the hidden nodes
    # SIG: sigmoid activation function (h=0,1)
    # RELU_MAX: relu activation function (h>0)
    def SetSampler(self,sampler_name):
        if sampler_name == "SIG":
            print('Sampling using HeatBATH')
            self.SamplerHiddens = self.SampleHiddens01
            self.SamplerVisibles = self.SampleVisibles01
        elif sampler_name == "METROPOLIS":
            print('Sampling using METROPOLIS')
            self.SamplerHiddens = self.SampleHiddens01_Metropolis
            self.SamplerVisibles = self.SampleVisibles01_Metropolis
        elif sampler_name == "RELU_MAX":
            print('Sampling using RELU')
            self.SamplerHiddens = self.SampleHiddensRELU_MAX
        elif sampler_name == 'TAP':
            self.SamplerHiddens = self.SampleHiddens01TAP

    # define an initial value fo the permanent chain
    def InitXpc(self,V):
        self.X_pc = V

    # Sampling and getting the mean value using RELU
    def SampleHiddensRELU_MAX(self,V,β=1):
        act_h = β*(self.W.mm(V).t() + self.hbias).t()
        mh = torch.clamp(act_h,min=0)
        h = torch.clamp(act_h + torch.randn(size=mh.size(),device=self.device, dtype=self.dtype),min=0)
        return h,mh

    # Sampling and getting the mean value using Sigmoid
    # using CurrentState
    def SampleHiddens01(self,V,β=1):             
        mh = torch.sigmoid(β*(self.W.mm(V).t() + self.hbias).t())
        h = torch.bernoulli(mh)

        return h,mh

    # Sampling and getting the mean value using Sigmoid
    # using CurrentState
    def SampleHiddens01TAP(self,V,Hp,β=1):
        mh = torch.sigmoid(β*(self.W.mm(V).t() + self.hbias - (Hp*torch.mm(self.W2,(V-V*V))).t()).t())
        h = torch.bernoulli(mh)

        return h,mh

    # Sampling and getting the mean value using Sigmoid
    def SampleHiddens01_Metropolis(self,V,β=1):             
        eff_bias = (self.W.mm(V).t() + self.hbias).t()
        mh = torch.sigmoid(β*eff_bias)
        Δe = (2*self.H_STATE-1)*eff_bias # difference in energy
        Pr_Move = (Δe>0)*1*torch.exp(-Δe)
        New_H = torch.bernoulli(Pr_Move)
        ACC_CHANGE = (Δe<=0)*1 + New_H # the one that should change
        h = (1-self.H_STATE)*ACC_CHANGE + self.H_STATE*(1-ACC_CHANGE)   
        self.H_STATE = h
        return h,mh

    def SampleVisibles01PT_priorSingle(self,H,β):

        mv = torch.sigmoid( β*(self.W.t().mm(H).t() + self.vbias)
                      + (1-β)*(self.vbias_prior ) ).t()
        # mv = torch.sigmoid(β*(self.W.t().mm(H).t() + self.vbias).t())
        v = torch.bernoulli(mv)
        return v,mv

    # H is Nh X M
    # W is Nh x Nv
    # Return Visible sample and average value for binary variable
    def SampleVisibles01(self,H,β=1):
        mv = torch.sigmoid(β*(self.W.t().mm(H).t() + self.vbias).t())
        v = torch.bernoulli(mv)
        return v,mv

    # H is Nh X M
    # Vp is Nv x M
    # W is Nh x Nv
    # Return Visible sample and average value for binary variable
    def SampleVisibles01TAP(self,H,Vp,β=1):
        mv = torch.sigmoid(β*(self.W.t().mm(H).t() + self.vbias - (Vp*torch.mm(self.W2.t(),(H-H*H))).t()).t())
        v = torch.bernoulli(mv)
        return v,mv

    # Sampling and getting the mean value using Sigmoid
    def SampleVisibles01_Metropolis(self,V,β=1):             
        eff_bias = (self.W.t().mm(V).t() + self.vbias).t()
        mv = torch.sigmoid(β*eff_bias)
        Δe = (2*self.V_STATE-1)*eff_bias # difference in energy
        Pr_Move = (Δe>0)*1*torch.exp(-Δe)
        New_V = torch.bernoulli(Pr_Move)
        ACC_CHANGE = (Δe<=0)*1 + New_V # the one that should change
        v = (1-self.V_STATE)*ACC_CHANGE + self.V_STATE*(1-ACC_CHANGE)
        self.V_STATE = v
        return v,mv



    # Compute the negative term for the gradient FOR NAIVE MEAN-FIELD !!!
    # IF it_mcmc=0 : use the class variable self.gibbs_steps for the number of MCMC steps
    # IF self.anneal_steps>= : perform anealing for the corresponding number of steps
    # FOR ANNEALING: only if the max eigenvalues is above self.ann_threshold
    # βs : effective temperure. Used only if =! -1
    def GetAv_MF(self,it_mcmc=0):
        if it_mcmc==0:
            it_mcmc = self.gibbs_steps

        β = self.β
        mv = self.X_pc       
        _,mh = self.SamplerHiddens(mv,β=β)
        _,mv = self.SampleVisibles01(mh,β=β)
        
        for t in range(1,it_mcmc):
            _,mh = self.SamplerHiddens(mv,β=β)
            _,mv = self.SampleVisibles01(mh,β=β)


        return mv,mh


    # Compute the negative term for the gradient FOR TAP !!!
    # IF it_mcmc=0 : use the class variable self.gibbs_steps for the number of MCMC steps
    # IF self.anneal_steps>= : perform anealing for the corresponding number of steps
    # FOR ANNEALING: only if the max eigenvalues is above self.ann_threshold
    # βs : effective temperure. Used only if =! -1
    def GetAv_TAP(self,it_mcmc=0):
        if it_mcmc==0:
            it_mcmc = self.gibbs_steps

        β = self.β
        mv = self.X_pc        
        _,mh = self.SampleHiddens01(mv,β=β)
        _,mv = self.SampleVisibles01(mh,β=β)
        
        for t in range(1,it_mcmc):
            _,mh = self.SampleHiddens01TAP(mv,mh,β=β)
            _,mv = self.SampleVisibles01TAP(mh,mv,β=β)


        return mv,mh


    # Compute the negative term for the gradient
    # IF it_mcmc=0 : use the class variable self.gibbs_steps for the number of MCMC steps
    # IF self.anneal_steps>= : perform anealing for the corresponding number of steps
    # FOR ANNEALING: only if the max eigenvalues is above self.ann_threshold
    # βs : effective temperure. Used only if =! -1
    def GetAv(self,it_mcmc=0,βs=-1):
        if it_mcmc==0:
            it_mcmc = self.gibbs_steps

        v = self.X_pc

        mh = 0
        β=self.β 
        if βs != -1:
            β=βs
        h,mh = self.SamplerHiddens(v,β=β)
        v_tmp,mv = self.SamplerVisibles(h,β=β)

        # FIXING
        v_tmp[:self.FixNodes,:] = v[:self.FixNodes,:]
        mv[:self.FixNodes,:] = v[:self.FixNodes,:]
        
        for t in range(1,it_mcmc):
            h,mh = self.SamplerHiddens(v_tmp,β=β)
            v_tmp,mv = self.SamplerVisibles(h,β=β)
            # FIXING
            v_tmp[:self.FixNodes,:] = v[:self.FixNodes,:]
            mv[:self.FixNodes,:] = v[:self.FixNodes,:]


        return v_tmp,mv,h,mh


    # Return samples and averaged values
    # IF it_mcmc=0 : use the class variable self.gibbs_steps for the number of MCMC steps
    # IF self.anneal_steps>= : perform anealing for the corresponding number of steps
    # FOR ANNEALING: only if the max eigenvalues is above self.ann_threshold
    # βs : effective temperure. Used only if =! -1
    def Sampling(self,X,it_mcmc=0,βs=-1,anneal_steps=0,ann_threshold=4):  
        if it_mcmc==0:
            it_mcmc = self.gibbs_steps

        v = X
        self.V_STATE = v
        self.H_STATE,_ = self.SampleHiddens01(v)

        β=self.β 
        if βs != -1:
            β=βs

        h,mh = self.SamplerHiddens(v,β=β)
        v_tmp,mv = self.SamplerVisibles(h,β=β)

        v_tmp[:self.FixNodes,:] = v[:self.FixNodes,:]
        mv[:self.FixNodes,:] = v[:self.FixNodes,:]
        
        for t in range(it_mcmc-1):
            h,mh = self.SamplerHiddens(v_tmp,β=β)
            v_tmp,mv = self.SamplerVisibles(h,β=β)

            v_tmp[:self.FixNodes,:] = v[:self.FixNodes,:]
            mv[:self.FixNodes,:] = v[:self.FixNodes,:]
            
        return v_tmp,mv,h,mh
    

    # Update weights and biases
    def updateWeights(self,v_pos,h_pos,v_neg,h_neg_v,h_neg_m):
        if self.DynBetaGradient:
            self.TempUpd = 1/self.ExpCos(self.up_tot,4,10000,100)

        lr_p = self.lr/self.mb_s
        lr_n = self.lr/self.num_pcd
        lr_reg = self.lr*self.regL2

        NegTerm_ia = h_neg_m.mm(v_neg.t())

        if self.UpdWeights:
            self.W += h_pos.mm(v_pos.t())*lr_p -  NegTerm_ia*lr_n - 2*lr_reg*self.W + self.TempUpd*self.TempUpd_W*torch.randn(size=(self.Nh,self.Nv), device=self.device, dtype=self.dtype)

        if self.UpdWα:
            if self.u.shape[0] == 0:
                self.u,self.s,self.v = torch.svd(self.W)

            ΔW = h_pos.mm(v_pos.t())/self.mb_s - h_neg_v.mm(v_neg.t())/self.num_pcd
            self.s += self.lr*torch.diag(torch.mm(torch.mm(self.u.t(),ΔW),self.v)) - 2*lr_reg *self.s
            self.W = torch.mm(torch.mm(self.u,torch.diag(self.s)),self.v.t())

        if self.UpdFieldsVis:
            self.vbias += torch.sum(v_pos,1)*lr_p - torch.sum(v_neg,1)*lr_n + self.TempUpd*self.TempUpd_VB*torch.randn(self.Nv, device=self.device, dtype=self.dtype)

        if self.UpdFieldsHid:    
            self.hbias += torch.sum(h_pos,1)*lr_p - torch.sum(h_neg_m,1)*lr_n + self.TempUpd*self.TempUpd_HB*torch.randn(self.Nh, device=self.device, dtype=self.dtype)
                

    # Update weights and biases
    def updateWeightsCentered(self,v_pos,h_pos_v,h_pos_m,v_neg,h_neg_v,h_neg_m,ν=0.2,ε=0.01):

        # self.HidDataAv = (1-ν)*self.HidDataAv + ν*torch.mean(h_pos_m,1)
        self.VisDataAv = torch.mean(v_pos,1)
        self.HidDataAv = torch.mean(h_pos_m,1)
        Xc_pos = (v_pos.t() - self.VisDataAv).t()
        Hc_pos = (h_pos_m.t() - self.HidDataAv).t()

        Xc_neg = (v_neg.t() - self.VisDataAv).t()
        Hc_neg = (h_neg_m.t() - self.HidDataAv).t()

        NormPos = 1.0/self.mb_s
        NormNeg = 1.0/self.num_pcd

        siτa_neg = Hc_neg.mm(Xc_neg.t())*NormNeg
        si_neg = torch.sum(v_neg,1)*NormNeg
        τa_neg = torch.sum(h_neg_m,1)*NormNeg

        ΔW = Hc_pos.mm(Xc_pos.t())*NormPos -  siτa_neg - 2*self.regL2*self.W

        EffLR = self.lr
        if self.UpdWeights:
            self.W += ΔW*EffLR 

        if self.UpdFieldsVis:
            ΔVB = torch.sum(v_pos,1)*NormPos - si_neg - torch.mv(ΔW.t(),self.HidDataAv) - 2*self.regL2*self.vbias            
            self.vbias += EffLR*ΔVB

        if self.UpdFieldsHid:
            ΔHB = torch.sum(h_pos_m,1)*NormPos - τa_neg - torch.mv(ΔW,self.VisDataAv) - 2*self.regL2*self.hbias
            self.hbias += EffLR*ΔHB 
            


    # Update weights and biases
    def updateWeightsCentered_MF(self,v_pos,h_pos,v_neg,h_neg,ν=0.01):

        # self.HidDataAv = (1-ν)*self.HidDataAv + ν*torch.mean(h_pos_m,1)
        self.VisDataAv = torch.mean(v_pos,1)
        self.HidDataAv = torch.mean(h_pos,1)
        Xc_pos = (v_pos.t() - self.VisDataAv).t()
        Hc_pos = (h_pos.t() - self.HidDataAv).t()

        Xc_neg = (v_neg.t() - self.VisDataAv).t()
        Hc_neg = (h_neg.t() - self.HidDataAv).t()

        NormPos = 1.0/self.mb_s
        NormNeg = 1.0/self.num_pcd
        # NormL2 = self.regL2

        OnsagerCorr = 0
        if self.FIT_TAP:
            OnsagerCorr = self.W*( torch.mm( h_neg - torch.square(h_neg), (v_neg - torch.square(v_neg)).t() ) )*NormNeg


        ΔW = Hc_pos.mm(Xc_pos.t())*NormPos -  Hc_neg.mm(Xc_neg.t())*NormNeg - OnsagerCorr - 2*self.regL2*self.W

        #if self.NatGrad:
        #    FW = 

        if self.UpdWeights:
            # ΔW_ia = Hc_pos.mm(Xc_pos.t())*NormPos -  NegTerm_ia*NormNeg - 2*self.regL2*self.W + self.TempUpd*self.TempUpd_W*torch.randn(size=(self.Nh,self.Nv), device=self.device, dtype=self.dtype)
            self.W += ΔW*self.lr  + self.TempUpd*self.TempUpd_W*torch.randn(size=(self.Nh,self.Nv), device=self.device, dtype=self.dtype)

        if self.UpdFieldsVis:
            ΔVB = torch.sum(v_pos,1)*NormPos - torch.sum(v_neg,1)*NormNeg - torch.mv(ΔW.t(),self.HidDataAv)
            self.vbias += self.lr*ΔVB + self.TempUpd*self.TempUpd_VB*torch.randn(self.Nv, device=self.device, dtype=self.dtype)

        if self.UpdFieldsHid:
            ΔHB = torch.sum(h_pos,1)*NormPos - torch.sum(h_neg,1)*NormNeg - torch.mv(ΔW,self.VisDataAv)
            self.hbias += self.lr*ΔHB  + self.TempUpd*self.TempUpd_HB*torch.randn(self.Nh, device=self.device, dtype=self.dtype)

        self.W2 = torch.square(self.W)

    # Update only biases
    def updateFields(self,v_pos,h_pos,v_neg,h_neg):
        lr_p = self.lr/self.mb_s
        lr_n = self.lr/self.num_pcd
        self.vbias += lr_p*torch.sum(v_pos,1) - lr_n*torch.sum(v_neg,1) + self.TempUpd*torch.randn(self.Nv, device=self.device, dtype=self.dtype)
        self.hbias += lr_p*torch.sum(h_pos,1) - lr_n*torch.sum(h_neg,1) + self.TempUpd*torch.randn(self.Nh, device=self.device, dtype=self.dtype)
    
    # Compute positive and negative term
    def fit_batch(self,X):
        h_pos_v, h_pos_m = self.SamplerHiddens(X)
        if self.CDLearning:
            self.X_pc = X
            self.X_pc,_,h_neg_v,h_neg_m = self.GetAv()
        else:
            self.X_pc,_,h_neg_v,h_neg_m = self.GetAv()

        if self.UpdCentered:
            self.updateWeightsCentered(X,h_pos_v,h_pos_m,self.X_pc,h_neg_v,h_neg_m)
        else:
            self.updateWeights(X,h_pos_m,self.X_pc,h_neg_v,h_neg_m)

    # Compute positive and negative term
    def fit_batch_MF(self,X):
        _, h_pos = self.SamplerHiddens(X)
        self.X_pc,h_neg = self.GetAv_MF()
        if self.UpdCentered:
            self.updateWeightsCentered_MF(X,h_pos,self.X_pc,h_neg)
        #else:
        #    self.updateWeights(X,h_pos_m,self.X_pc,h_neg_v,h_neg_m)


    # Compute positive and negative term
    def fit_batch_TAP(self,X):
        _, h_pos = self.SamplerHiddens(X)
        self.X_pc,h_neg = self.GetAv_TAP()
        if self.UpdCentered:
            self.updateWeightsCentered_MF(X,h_pos,self.X_pc,h_neg)


    # return the mininbatch
    def getMiniBatches(self,X,m):
        idx = np.random.randint(X.shape[1],size=self.mb_s)
        return X[:,idx]

    # Iterating nMF fixed point
    def SamplingMF(self,X,it_mcmc=0):
        if it_mcmc==0:
            it_mcmc = self.gibbs_steps
        _,mh = self.SamplerHiddens(X)
        _,mv = self.SampleVisibles01(mh)

        for t in range(it_mcmc):
            _,mh = self.SamplerHiddens(mv)
            _,mv = self.SampleVisibles01(mh)
        
        return mv,mh

    # Iterating TAP fixed point
    def SamplingTAP(self,X,it_mcmc=0):
        if it_mcmc==0:
            it_mcmc = self.gibbs_steps

        _,mh = self.SampleHiddens01(X)
        _,mv = self.SampleVisibles01(mh)

        for t in range(it_mcmc):
            _,mh = self.SampleHiddens01TAP(mv,mh)
            _,mv = self.SampleVisibles01TAP(mh,mv)
        
        return mv,mh

    def fit(self,X,ep_max=0,B=1000,NS=None,it_mcmc=None,output_vcf_file="CRBM_output"):

        if self.Ns == -1:
            self.Ns = X.shape[1]

        if ep_max==0:
            ep_max = self.ep_max

        NB = int(X.shape[1]/self.mb_s)+1

        if self.ep_tot==0:
            self.VisDataAv = torch.mean(X,1)

        self.W2 = torch.square(self.W)

        #_,h_av = self.SamplerHiddens(X)
        #self.HidDataAv = torch.mean(h_av,1)

        '''if (len(self.list_save_time)>0) & (self.up_tot == 0):
            f = h5py.File('AllParameters'+self.file_stamp+'.h5','w')
            f.create_dataset('alltime',data=self.list_save_time)
            f.close()

        if (len(self.list_save_rbm)>0) & (self.ep_tot == 0):
            f = h5py.File('RBM'+self.file_stamp+'.h5','w')   
            f.create_dataset('lr',data=self.lr)
            f.create_dataset('l2',data=self.regL2)
            f.create_dataset('Nv',data=self.Nv)
            f.create_dataset('Nh',data=self.Nh)
            f.create_dataset('NGibbs',data=self.gibbs_steps)
            f.create_dataset('UpdByEpoh',data=NB)
            f.create_dataset('AnnealingSteps',data=self.anneal_steps)
            f.create_dataset('miniBatchSize',data=self.mb_s)
            f.create_dataset('numPCD',data=self.num_pcd)
            f.create_dataset('alltime',data=self.list_save_rbm)

            _, FE_AIS_R, _ = self.ComputeFE(nβ=B)
            FE_0 = (self.Nv+self.Nh)*torch.log(torch.tensor(2.0))
            FE_AIS = (FE_AIS_R+FE_0)/(self.Nv+self.Nh)

            f.create_dataset('W_0',data=self.W.cpu())
            f.create_dataset('vbias_0',data=self.vbias.cpu())
            f.create_dataset('hbias_0',data=self.hbias.cpu())
            f.create_dataset('FE_AIS_0',data=FE_AIS.cpu())
            
            f.close()'''

        # INIT THE STATE of the MACHINE
        self.V_STATE = torch.bernoulli(torch.rand((self.Nv+self.Nh2,self.num_pcd), device=self.device, dtype=self.dtype))
        self.H_STATE,_ = self.SampleHiddens01(self.V_STATE)            


        for t in range(ep_max):
            print("IT ",self.ep_tot)
            self.ep_tot += 1


            Xp = X[:,torch.randperm(X.size()[1])]
            for m in tqdm(range(NB)):
                if self.ResetPermChainBatch:
                    self.X_pc = torch.bernoulli(torch.rand((self.Nv+self.Nh2,self.num_pcd), device=self.device, dtype=self.dtype))
                    self.V_STATE = self.X_pc
                    self.H_STATE,_ = self.SampleHiddens01(self.V_STATE)             
                
                Xb = self.getMiniBatches(Xp,m)
                # FIXING PART
                self.X_pc[:self.FixNodes,:] = Xb[:self.FixNodes,:]

                if self.FIT_MF:
                    self.fit_batch_MF(Xb)
                elif self.FIT_TAP:
                    self.fit_batch_TAP(Xb)
                else:
                    self.fit_batch(Xb)                
                

                '''if self.up_tot in self.list_save_time:
                    f = h5py.File('AllParameters'+self.file_stamp+'.h5','a')
                    print('param'+str(self.up_tot))
                    f.create_dataset('W_'+str(self.up_tot),data=self.W.cpu())
                    f.create_dataset('vbias_'+str(self.up_tot),data=self.vbias.cpu())
                    f.create_dataset('hbias_'+str(self.up_tot),data=self.hbias.cpu())
                    #if self.ResetPermChainBatch == False:
                    #    f.create_dataset('PCD'+str(self.up_tot),data=self.X_pc.cpu())
                    
                    f.close()'''

                self.up_tot += 1




            if (NS is not None) and (self.ep_tot in self.list_save_rbm):

                '''_, FE_AIS_R, _ = self.ComputeFE(nβ=B)
                FE_0 = (self.Nv+self.Nh)*torch.log(torch.tensor(2.0))
                FE_AIS = (FE_AIS_R+FE_0)/(self.Nv+self.Nh)

                f = h5py.File('RBM'+self.file_stamp+'.h5','a')
                f.create_dataset('W_'+str(self.ep_tot),data=self.W.cpu())
                f.create_dataset('vbias_'+str(self.ep_tot),data=self.vbias.cpu())
                f.create_dataset('hbias_'+str(self.ep_tot),data=self.hbias.cpu())
                f.create_dataset('FE_AIS_'+str(self.ep_tot),data=FE_AIS.cpu())
                if self.ResetPermChainBatch == False:
                        f.create_dataset('PCD_'+str(self.ep_tot),data=self.X_pc.cpu())
                f.close()'''

                vinit = torch.bernoulli(torch.rand((self.Nv,NS), device=self.device, dtype=self.dtype))
                vs,vm,_,_ = self.Sampling(vinit,it_mcmc=it_mcmc)
   
                ss = [bytes([int(aa) for aa in a]) for a in vs.transpose(0,1).tolist()]
                with open("{}{}.pickle".format(output_vcf_file,self.ep_tot), "wb") as f:
                    pickle.dump(ss,f)
    





# Script Learning Gene805
#generating code adapted from:
#https://gitlab.inria.fr/ml_genetics/public/artificial_genomes

import torch
import numpy as np
import matplotlib.pyplot as plt
import h5py

import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
import click
from experiment_tools import parse_VCF_to_genome_strings, parse_genome_strings_to_VCF





def main_CRBM(inpt, NS, ep_max=2001, B=1000, it_mcmc=50, gpu=False, dump_output_interval=50,output_vcf_file="CRBM_output",FixNodes=300,Nh=500):
    # CHOOSE CPU OR GPU
    if not gpu:
        device = torch.device("cpu") 
    else:
        #device = torch.device("cuda:1")
        device = torch.device("cuda")
    dtype = torch.float

    X = torch.tensor(np.array([list(a) for a in inpt]).T).float().to(device)

    Nv = X.shape[0]
    Ns = X.shape[1]
    print('NumSamples=',Ns)
    print('ShapeX : ',X.shape)

    # Number of hidden nodes
    #Nh  = 500 #500 #2000
    # Learning rate
    lr = 0.005 #0.001
    # L2 Regularization
    l2 = 0.0
    # Number of Gibbs steps to compute the negative term of the gradient.
    NGibbs = 50
    # minibatch size
    nMB = 500 #500 #1252
    # Nb of parallel chains to compute the negative term of the gradient.
    nNeg = 500 #500 #1252

    myRBM = CRBM(num_visible=Nv,
                    num_hidden=Nh,
                    device=device,
                    lr=lr,
                    regL2=l2,
                    gibbs_steps=NGibbs,
                    UpdCentered=True,
                    mb_s=nMB,
                    num_pcd=nNeg)

    # Initialize the visible biases
    myRBM.SetVisBias(X)
    # Fix part of the dataset
    myRBM.FixNodes = FixNodes
    # Use Out-of-Equilibrium learning
    myRBM.ResetPermChainBatch = True
    # STAMP for the file registering the weigths
    stamp='TrainingGene10K_5KP1_CDT_OOELearning_Nh'+str(Nh)+'_lr'+str(lr)+'_l2'+str(l2)+'_Rdm_NGibbs'+str(NGibbs)
    myRBM.file_stamp = stamp

    # Number of epochs
    #ep_max = 20001
    # Frequency of saving the weights
    fq_msr = dump_output_interval #200
    myRBM.list_save_rbm = np.arange(1,ep_max+2,fq_msr)

    myRBM.fit(X,ep_max=ep_max,B=B,NS=NS,it_mcmc=it_mcmc,output_vcf_file=output_vcf_file)

    return


    fname = 'RBM'+stamp+".h5" #TrainingGene10K_5KP1_CDT_OOELearning_Nh2000_lr0.001_l20.0_Rdm_NGibbs50.h5'
    f = h5py.File(fname,'r')
    Nh = f['Nh'][()]
    Nv = f['Nv'][()]
    l2 = f['l2'][()]
    NGibbs = f['NGibbs'][()]

    # Creating Object RBM
    RBMGene = CRBM(num_visible=Nv,
                    num_hidden=Nh,
                    device=device,
                    regL2=l2,
                    gibbs_steps=NGibbs,
                    UpdCentered=True)

    # Loading the last epoch
    ep_last = f['alltime'][:][-1]
    print('Ep=',ep_last)
    RBMGene.W = torch.tensor(f['W_'+str(ep_last)][:]).to(device)
    RBMGene.vbias = torch.tensor(f['vbias_'+str(ep_last)][:]).to(device)
    RBMGene.hbias = torch.tensor(f['hbias_'+str(ep_last)][:]).to(device)

    # Generate new samples
    #NS = 1000
    #idx_perm = torch.randperm(NS)
    vinit = torch.bernoulli(torch.rand((Nv,NS), device=RBMGene.device, dtype=RBMGene.dtype))
    #vinit[:5000,:] = Xseed[:5000,idx_perm[:NS]]
    vs,vm,_,_ = RBMGene.Sampling(vinit,it_mcmc=it_mcmc) #NGibbs)
    return [bytes([int(aa) for aa in a]) for a in vs.transpose(0,1).tolist()]



@click.command()
@click.argument('input_vcf_file', type=click.types.Path())
@click.argument('output_vcf_file', type=click.types.Path())
@click.argument('number_of_genomes', type=click.INT, default=1)
@click.option('--ep_max', type=click.INT, default=2001)
@click.option('--b', type=click.INT, default=1000)
@click.option('--it_mcmc', type=click.INT, default=500)
@click.option('--gpu', type=click.BOOL, default=False)
@click.option('--dump_output_interval', type=click.INT, default=30)
@click.option('--nh', type=click.INT, default=500)
@click.option('--fixnodes', type=click.INT, default=300)
def CRBM_run(input_vcf_file, output_vcf_file, number_of_genomes,ep_max,b,it_mcmc,gpu,dump_output_interval,nh,fixnodes):
    if input_vcf_file.split(".")[-1]=="pickle":
        with open(input_vcf_file,"rb") as f:
            s,ploidy = pickle.load(f)
    else:
        s,ploidy = parse_VCF_to_genome_strings(input_vcf_file)
    ss = main_CRBM(s, number_of_genomes,ep_max=ep_max,B=b,it_mcmc=it_mcmc,gpu=gpu,output_vcf_file=output_vcf_file,dump_output_interval=dump_output_interval,Nh=nh,FixNodes=fixnodes)

if __name__ == '__main__':
    CRBM_run()





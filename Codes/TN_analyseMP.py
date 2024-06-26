#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Apr  7 22:52:59 2021

@author: grogroda
"""

import NetworkGeneration as ng
from matplotlib import pyplot as plt
import time
import numpy as np
from scipy.optimize import curve_fit
import multiprocessing as mp

'''
This code will be used to test and analyse data from the TN_model_generate function
of the NetworkGeneration.py module. This version of the code uses a module called
multiprocessing, which I'm using here purely to make the code run faster. As
you will notice, both codes work, but since I wanted to simulate very big networks
a huge number of times, I needed to adapt the code to run it in a cluster, that's
why I'm making a separate code here in case you want to work with a more efficient
version of the analysis code.
'''

def simular(n, alpha_A, alpha_G, N):
    '''
    This will create n networks with the TN_model, using the parameters shown,
    and print the graph of p(e) x e where p(e) is the probability to find a node 
    with energy e in the final network.
    '''
    
    cores=mp.cpu_count()
    pool=mp.Pool(processes=cores)
    energies=[]
    pool_list=[]
    
    for i in range(n):
        p=pool.apply_async(ng.TN_model_generate, (alpha_A, alpha_G, N))
        pool_list.append(p)
        #print('Simulation', 100*len(pool_list)/n, '% completed!')
            
    networks=[p.get() for p in pool_list]
    
    for nk in networks:
        energies+=[node.weight for node in nk.nodes]
    
    return energies

def analisar(energy_list, bins, q_fit=False): 
    
    #REVIEW AND FIX THIS PART OF THE CODE!¨
    
    start, finish=min(energy_list), max(energy_list)
    bins_list=list(np.logspace(np.log(start), np.log(finish), num=bins))
    hist, edges=np.histogram(energy_list, bins=bins_list, density=True)
    hist_list=list(hist)
    hist_list.append(1/len(energy_list))
            
    if q_fit==True:
        
        def q_dist(x, q, bq, Z):
            
            return 1/Z*(1-bq*(1-q)*x)**(1/(1-q))
        
        parameters, cov_matrix=curve_fit(q_dist, bins_list, hist_list)
        q=parameters[0]
        bq=parameters[1]
        Z=parameters[2]
    
    print(len(bins_list), len(hist_list))
    plt.scatter(bins_list, hist_list, c='k')
    if q_fit==True:
        plt.plot(bins_list, [1/Z*(1-bq*(1-q)*x)**(1/(1-q)) for x in bins_list])
        print('Z=', Z, ', q=', q, ' & \u03B2=', bq)
        print('Covariance Matrix:')
        print(cov_matrix)
        
    plt.xlim((0.000005, 50))
    plt.ylim((0.000008, 10))
    plt.xscale('log')
    plt.yscale('log')
    plt.xlabel('\u03B5')
    plt.ylabel('P(\u03B5)')
    plt.show()
    
if __name__=='__main__':
    t0=time.time()
    energies=simular(100, 2, 1, 1000)
    analisar(energies, 100, q_fit=False)
    print('Execution time:', time.time()-t0)
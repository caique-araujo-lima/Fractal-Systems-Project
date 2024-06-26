#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Mar  5 12:09:12 2021

@author: grogroda
"""

import NetworkGeneration as ng
from matplotlib import pyplot as plt
import time
import numpy as np
from scipy.optimize import curve_fit

'''
This code will be used to test and analyse data from the TN_model_generate function
of the NetworkGeneration.py module. 
'''

def simular(n, alpha_A, alpha_G, N):
    '''
    This will create n networks with the TN_model, using the parameters shown,
    and print the graph of p(e) x e where p(e) is the probability to find a node 
    with energy e in the final network.
    '''
    
    energies=[]
    
    for i in range(n):
        nk=ng.TN_model_generate(alpha_A, alpha_G, N)
        energies+=[node.weight for node in nk.nodes]
        print('Simulation', i+1, 'of', n, 'is complete!')
        
    return energies

def analisar(energy_list, bins, q_fit=False): 
    
    #REVIEW AND FIX THIS PART OF THE CODE!¨
    
    start, finish=min(energy_list), max(energy_list)
    bins_list=list(np.logspace(np.log(start), np.log(finish), num=bins))
    hist, edges=np.histogram(energy_list, bins=bins_list, density=True)
    hist_list, edges_list=list(hist), list(edges)
    
    bins_midlist=[]
    for i in range(len(edges_list)-1):
        mid=(edges_list[i+1]-edges_list[i])/2    
        bins_midlist.append(mid)
        
    if q_fit==True:
        
        def q_dist(x, q, bq, Z):
            
            return 1/Z*(1-bq*(1-q)*x)**(1/(1-q))
        
        parameters, cov_matrix=curve_fit(q_dist, bins_midlist, hist_list)
        q=parameters[0]
        bq=parameters[1]
        Z=parameters[2]
    
    print(len(bins_midlist), len(hist_list))
    plt.scatter(bins_midlist, hist_list, c='k', marker='.')
    if q_fit==True:
        plt.plot(bins_midlist, [1/Z*(1-bq*(1-q)*x)**(1/(1-q)) for x in bins_midlist])
        print('Z=', Z, ', q=', q, ' & \u03B2=', bq)
        print('Covariance Matrix:')
        print(cov_matrix)
    
    q, bq, Z=1.05, 8.1, 0.95
    plt.plot(bins_list, [1/Z*(1-bq*(1-q)*x)**(1/(1-q)) for x in bins_list])    
    plt.xlim((0.000001, 30))
    plt.ylim((0.000001, 20))
    plt.xscale('log')
    plt.yscale('log')
    plt.xlabel('\u03B5')
    plt.ylabel('P(\u03B5)')
    plt.show()
    
if __name__=='__main__':
    t0=time.time()
    energies=simular(100, 2, 1, 100)
    analisar(energies, 100, q_fit=False)
    print('Execution time:', time.time()-t0)
    
#pedir para mostrar o q-exp esperado
    
    

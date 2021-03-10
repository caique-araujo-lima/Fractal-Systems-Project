#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Mar  5 12:09:12 2021

@author: grogroda
"""

import NetworkGeneration as ng
from matplotlib import pyplot as plt
import time

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
        print('Simulation ', i+1, ' of ', n, ' is complete!')
        
    return energies

def analisar(energy_list, bins): #N=number of bins
    
    densities=[]
    bins_list=[]
    start, finish=min(energy_list), max(energy_list)
    interval=(finish-start)/bins
    ii, ie=start, start+interval
    
    for i in range(bins):
        density=0
        bin_energies=[]
        for energy in energy_list:
            if energy>=ii and energy<=ie:
                density+=1
                bin_energies.append(energy)
                
        densities.append(density)
        print(bin_energies)
        average_energy=sum(bin_energies)/len(bin_energies)
        bins_list.append(average_energy)
        ii=ie
        ie=ii+interval
    
    #plt.scatter(energy_list, [1 for i in range(len(energy_list))], marker='.')
    plt.scatter(bins_list, densities)
    plt.xlabel('\u03B5')
    plt.ylabel('P(\u03B5)')
    plt.show()
    
if __name__=='__main__':
    t0=time.time()
    energies=simular(150, 1, 1, 200)
    analisar(energies, 20)
    print('Execution time:', time.time()-t0)
    
    

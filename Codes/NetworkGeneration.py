#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
This module is meant to store functions that generate fractal networks according
to various algorithms.
"""

import random
import networkx as nx
import matplotlib.pyplot as plt

def hubs_generate(p=0.7,m=3,N=2, draw=False, save=False): 
    '''
    This function generates a fractal network using an algorithm presented in
    one of the references, it is based on the principle of repulsion between hubs.
    p is the probability factor (0<p<1), m is a variable associated with the 
    algorithm and N is the number of interations (recommended 0<N<4). If draw is
    set to True by the user, the function will print the network. If save is set
    to True by the user, it saves a .png image of the network.
    '''
    
    if save==True: #if save is true and draw is false, problems would happen
        draw=True
    
    #starting network (3-edged star):

    nk=nx.Graph()
    
    nk.add_edge(1,2)
    nk.add_edge(1,3)
    nk.add_edge(1,4)

    c=1 #counter

    for i in range(N): #starts the generation: N iterations
        #first step
        old_edges=list(nk.edges) #list of edges before the iteration is done
        old_nodes=list(nk.nodes) #list of nodes before the iteration is done
        new_nodes=[] #list of nodes being created during the iteration
        
        '''
        The first loop will be the first part of the algorithm: simply creating
        new nodes connected to the old nodes according to the parameters. The 
        second loop will be the random part of the algorithm: determines
        randomly some nodes to disconnect and creates new connections according 
        to the algorithm.
        '''
        
        for node in old_nodes:
            for j in range(m*nk.degree(node)):
                nk.add_edge(node, 5+c)
                new_nodes.append(5+c)
                c+=1
    
        for edge in old_edges:
            if random.random()<=p:
                continue
            else:
                nk.remove_edge(edge[0], edge[1]) #remove uma aresta entre dois vertices antigos
                nk.add_edge(random.choice(list(nk.adj[edge[0]])), random.choice(list(nk.adj[edge[1]]))) #adiciona uma aresta entre o nó e um vértice novo
    
    if draw==True:
        nx.draw(nk, show_labels=True, node_size=12)
        
    if save==True:
        plt.savefig('my_network.png')

#the following lines are meant to test this module

if __name__=='__main__':
    hubs_generate(0.7,3,2,True)

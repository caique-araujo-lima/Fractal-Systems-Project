#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
This module is meant to store functions that generate fractal networks according
to various algorithms.
"""

import random
import networkx as nx
import matplotlib.pyplot as plt

def hubs_generate(p,m,N, draw=False, save=False): 
    '''
    This function generates a fractal network using an algorithm presented in
    one of the references, it is based on the principle of repulsion between hubs.
    p is the probability factor (0<p<1), m is a variable associated with the 
    algorithm and N is the number of interations (recommended 0<N<4). If draw is
    set to True by the user, the function will print the network.
    '''
    
    if save==True: #if save is true and draw is false, problems would happen bellow
        draw=True
    
    #starting network (3-edged star):

    nk=nx.Graph()
    
    nk.add_edge(1,2)
    nk.add_edge(1,3)
    nk.add_edge(1,4)
    nk.add_edge(1,5)

    c=1 #contador

    for i in range(N):
        #first step
        old_edges=list(nk.edges)
        old_nodes=list(nk.nodes)
        new_nodes=[]
        for node in old_nodes:
            for j in range(m*nk.degree(node)):
                nk.add_edge(node, 6+c)
                new_nodes.append(6+c)
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

if __name__=='__main__':
    hubs_generate(0.7,3,2,True, True)

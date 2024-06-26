#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
This module is meant to store functions that generate networks according with
various characteristics, according to various algorithms.
"""

import random
import networkx as nx
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import rv_continuous
import math
import time

def hubs_generate(p=0.7,m=3,N=2, draw=False, save=False): 
    '''
    This function generates a fractal network using an algorithm presented in
    one of the references (Molontay's M.Sc. thesis), it is based on the principle
    of repulsion between hubs.
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
                nk.add_edge(node, 4+c)
                new_nodes.append(4+c)
                c+=1
    
        for edge in old_edges:
            if random.random()<=p:
                continue
            else:
                nk.remove_edge(edge[0], edge[1]) 
                nk.add_edge(random.choice(list(nk.adj[edge[0]])), random.choice(list(nk.adj[edge[1]]))) #adiciona uma aresta entre o nó e um vértice novo
    
    if draw==True:
        nx.draw(nk, show_labels=True, node_size=12)
        
    if save==True:
        plt.savefig('my_network.png')
        
    return nk

#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#

class Geo_Node:
    
    '''
    For some algorithms, we will need networks that take into account the euclidean
    positions and distances between the nodes, which is not (to my knowledge) 
    supported by networkx, so this class and the Geo_Network class will be created
    in order to create such networks. The present class will be used for each 
    individual node.
    '''
    
    def __init__(self, position, label, weight=1.0):
        '''
        The position has to be any 2 valued (x,y) set (a tuple, a list, whatever) 
        containing the x and y component of the position of the node. Maybe
        in the future I can work with z components. The weight of the node
        is set to 1 (in case your network in unweighted), otherwise you can
        set a weight yourself.
        '''
        
        self.label=label #every node has a label to distinguish it from the others,
        #it can be a number for example.
        self.x=position[0]
        self.y=position[1]
        self.position=(self.x, self.y)
        self.weight=weight
        self.neighbours=[] #this list contains all the neighbours of the node, 
        #every node that is directly connected to it.
        
    def update_weight(self, edge_dict):
        #the edge_dict has to be the dictionary of edges available with the 
        #Geo_Network class.
        
        new_weight=0
        
        for edge in edge_dict:
            if self in edge:
                new_weight+=edge_dict[edge]/2

class Geo_Network:
    
    '''
    Read the Geo_Nodes class description first. This class will store the network
    itself of that kind of network, and will have functions that concern the whole
    network.
    '''
    
    def __init__(self, edges_list=None):
        '''
        The network starts completely empty if you don't initiate it with any
        arguments, and then you can build the network yourself. If, on the other
        hand, you have a pre-made network and want to use it, you can do it, the
        edges_list argument receives a list on the format [(A,B,w1), (A,C,w2), (B,D,w3), etc]
        containing all the edges of the network, where A, B, C, D, etc, are nodes
        (Geo_Node format) of your network and (A,B,w) represents an edge between
        nodes A and B with weight w.
        '''
        
        if edges_list!=None:
            
            self.edges=[(edge[0], edge[1]) for edge in edges_list]
            self.nodes=[]
            self.edges_weights={} #dict storing the weights of the edges
            
            for edge in edges_list:
                if len(edge)==3:
                    self.edges_weights[edge]=edge[3]
            
            for tup in self.edges:
                
                if tup[0] not in self.nodes:
                    self.nodes.append(tup[0])
                    
                if tup[1] not in self.nodes:
                    self.nodes.append(tup[1])
                    
            xsum=0
            ysum=0
            weight_sum=0
        
            for node in self.nodes:
                xsum+=node.weight*node.x
                ysum+=node.y*node.weight
                weight_sum+=node.weight
            
            self.center_mass=(xsum/weight_sum, ysum/weight_sum)
                    
        else:
            self.nodes=[]
            self.edges=[]
            self.center_mass=None
            self.edges_weights={}
            
    def add_node(self, node): #node has to be an object of the type Geo_Node
        
        self.nodes.append(node)
        
    def add_edge(self, node1, node2, weight):
        '''
        This function can create an edge between two preexisting nodes, or you
        can create new nodes from it. If you do self.add_edge(A,B), both A and
        B still not in the network, they will automatically be put in the network,
        along with the edge between them. node1 and node2 obviously have to be
        of the class Geo_Node.
        '''
        
        self.edges.append((node1, node2))
        self.edges_weights[(node1, node2)]=weight
        
        if node1 not in self.nodes:
            self.nodes.append(node1)
            
        if node2 not in self.nodes:
            self.nodes.append(node2)
            
    def euclid_distance(self, node1, node2):
        #calculate the euclidean distance between node1 and node2
        
        distance=((node1.x-node2.x)**2+(node1.y-node2.y)**2)**0.5
        
        return distance
    
    def update_center(self):
        #update the center of mass of the network
        xsum=0
        ysum=0
        weight_sum=0
        
        for node in self.nodes:
            xsum+=node.weight*node.x
            ysum+=node.weight*node.y
            weight_sum+=node.weight
            
        self.center_mass=(xsum/weight_sum, ysum/weight_sum)      
        
def print_Geo_Network(nk, title='My Network', save=False):
    '''
    This function takes as an argument an object of the class Geo_Network, and
    it prints, using matplotlib, the network with simple lines representing edges
    and dots representing nodes. In the future, I'll try to work out a way to
    display the weight of the nodes and edges using different sizes and/or colors.
    You can set the title of the network with the title argument. If save is set
    to True, it will save a .png image of the network on the same directory as
    your code.
    '''
    
    x_list, y_list=[],[]
    
    for node in nk.nodes:
        x_list.append(node.x)
        y_list.append(node.y)
    
    plt.figure()
    plt.title(title)
    plt.xlabel('x')
    plt.ylabel('y')
    plt.scatter(x_list, y_list, marker='o', color='midnightblue')
        
    plt.show()
    
    if save==True:
        plt.savefig('my_network.png')
        
    #THIS FUNTION IS STILL NOT WORKING PROPERLY!

#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#

w0, eta=1, 1

class exponential(rv_continuous):
    '''
    This is a VERY confusing part of the code. This is supposed to create a custom
    probability distribution function, equation 3 in the article. This is what is
    (apparently) called an abstract base class (ABC), its kind of a base class where
    you can build the "rest" of the class by yourself. In this case, we give this class
    a distribution function, and the class takes care of making it work with every
    other function and class in the module and in python. Here is the link for the class:
    https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.rv_continuous.html
    '''   
    def _pdf(self, x): 
        
        return eta/(w0*math.gamma(1/eta))*np.exp(-(x/w0)**eta)
    
stretched_exponential=exponential(name='stretched_exponential', a=0)

a, b=1, 2

class exponential2(rv_continuous):
    '''
    This is just another custom probability distribution (also continuous) based
    on an idea prof. Tsallis gave to me. Since I wasn't able to integrate the 
    distribution exp(a/w-bw) analytically to find the normalization factor, I used
    Wolfram Mathematica to numerically integrate and find this factor. If, however,
    you know how to solve this integral analytically, please contact me.
    '''   
    def _pdf(self, x): 
        
        return (1/227.446)*np.exp(a/x-b*x) 
    
stretched_exponential2=exponential2(name='stretched_exponential2', a=0.1)

class alpha_G_prob(rv_continuous):
    
    def _pdf(self, x, alpha_G, d):
        
        return (d+alpha_G-1)*(1/x**(d+alpha_G))
    
alpha_dist=alpha_G_prob(name='alpha_dist', a=1)
   
def TN_model_generate(alpha_A, alpha_G, N):
    
    '''
    This function will create a network based on a network model presented by 
    Constantino Tsallis in the paper available in the references text. The model
    is still unamed, so I named it for the purposes of this code as Tsallis Network
    model (explaining why TN_model). The parameters alpha are, obviously, the same
    alphas from the article used as reference and N is the number of iterations.
    The dimension, for now, will be always 2 for simplicity.
    '''
    
    nk=Geo_Network()
    node1=Geo_Node((0,0), 1)
    nk.add_node(node1)
    nk.update_center()
    
    r=alpha_dist.rvs(alpha_G, 2) #take a look at the pareto variate prob
    #distribution to understand why I'm using it, I'm also assuming the module
    #uses xm=1 to be compatible with the r>=1 of the article.
    o=random.uniform(0, 2*np.pi) #Here I'm randomly choosing the angular position
    node2_x=nk.center_mass[0]+r*np.cos(o) #of the 2nd node, since it is apparently 
    node2_y=nk.center_mass[1]+r*np.sin(o) #arbitrary
    
    node2=Geo_Node((node2_x, node2_y), 1)
    nk.add_node(node2)
    edge12_weight=stretched_exponential.rvs()
    
    nk.add_edge(node1, node2, edge12_weight)
    node1.weight=edge12_weight/2
    node2.weight=edge12_weight/2
    
    nk.update_center()
    
    for i in range(2,N):
        r=alpha_dist.rvs(alpha_G, 2)
        o=random.uniform(0, 2*np.pi) 
        nodei_x=nk.center_mass[0]+r*np.cos(o) 
        nodei_y=nk.center_mass[1]+r*np.sin(o) 
        nodei=Geo_Node((nodei_x, nodei_y),1)
        nk.add_node(nodei)
        
        connections_list=random.choices(nk.nodes, weights=[node.weight/nk.euclid_distance(nodei, node) for node in nk.nodes], k=1)
        
        for connection in connections_list:
            edgeij_weight=stretched_exponential.rvs()
            nk.add_edge(nodei, connection, edgeij_weight)
        
            if nodei.weight==1.0:
                nodei.weight=edgeij_weight/2
            
            else:
                nodei.weight+=edgeij_weight/2
            
            connection.weight+=edgeij_weight/2
                
        for node in nk.nodes:
            node.update_weight(nk.edges_weights)
                
            
        nk.update_center()
        #print('Iteration', i+1, 'is complete!')
    
    return nk

#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#---#

if __name__=='__main__':
    t0=time.time()
    hubs_generate(0.5, 2, 3, draw=True)
    print('Time of execution:', time.time()-t0)

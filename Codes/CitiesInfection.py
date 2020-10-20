#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Oct 20 14:17:09 2020
@author: grogroda

This code tries to generate a Monte Carlo simulation of the spread of a virus
along a network of cities. The network is built according to a fractal network
model, according to the reference 1 in the references.txt document. Every city
will have a list of ints that can be -1, 0 ou k for k in [1,14]. Every cell of 
the list represents a citizen, in which 0 represents a person susceptible to 
infection, k represents the number of days in which an individual has been 
infected, and -1 represents a person that has recovered and is now immune to
infection, similarly to the SIR model. I assume after 14 days of infection the
person becomes immune, either by healing naturally or by dying.
"""

import networkx as nx
import numpy as np
from matplotlib import pyplot as plt
import random
from NetworkGeneration import hubs_generate

#-----------------------------------------------------------------------------#
                
def travel_prob(a=2.2, d): #probability of someone traveling to a city at distance 
                           #d of them, a is just a constant.
    
    return np.exp(-a*d)

def NumberofNeighbors(graph, node_label):
    
    neighbors=[n for n in graph.neighbors(node_label)]
    
    return len(neighbors)

class Person():
    '''
    This classe will be used to store information about the individuals in the
    whole network, the code will therefore be very heavy, but I believe this is
    the best approach for an approximation of small populations. The current_city
    and home_city attributes store the information about where the person lives
    and where they are in a given moment in time.
    '''
    
    def __init__(self, home_city, current_city, list_index):
        
        self.index=list_index #list index of the person in their current city
        self.susceptible=True
        self.infected=False
        self.immune=False
        self.home_city=home_city
        self.current_city=current_city
        self.days_infected=0 #number of days the person has been infected
        self.days_out_home=0
        
    def get_infected(self):
        
        self.infected=True
        self.susceptible=False
        
    def heal(self):
        
        self.infected=False
        self.immune=True
        
    def travel(self, destination): #destination has to be a City object
        
        self.current_city.people_in.pop(self.index) #pops the person from the list of the current city
        self.current_city=destination #sets a new current city
        self.current_city.people_in.append(self) #puts the person in the list of that city
        self.index=len(self.current_city.people_in)-1 #sets the new index, which is the last index of the list
        
    def pass_day(self): #when a day passes, a few things happen
        
        if self.days_infected==14: #there is a 14 day limit for the person to heal
            self.heal()
        
        if self.infected==True: 
            self.days_infected+=1
        
        if self.days_out_home==avg_time_trip: #if they spend a lot of time out of their home city
            self.travel(self.home_city) #they go back home
        
        if self.current_city!=self.home_city:
            self.days_out_home+=1
            

class City():
    '''
    This class is directed at objects meant to represent cities in a network of
    cities. The arguments to initialize this class are: a networkx node (node)
    and an int that represents the population of the city (population).
    '''
    
    def __init__(self, node, populationm, label):
        
        self.label=label
        self.node=node
        self.citizens=[Person(self, self, i) for i in range(population)] #the city starts with a healthy population
        self.population=population
        self.people_in=[person for person in self.citizens] 
        #self.people_in stores the people in the city at a given moment, including
        #travelers and excluding people that traveled from the city
        
        infected=0
        
        for person in self.citizens:
            if person>0:
                infected+=1
                
        self.infected=infected
        
    def Internal_infection(self):
        
        for person in self.people_in: #for each citizen
            if person.infected==True: #the infected ones will test to see if they will infect someone
                
                for contact in range(avg_contact): #for each person they get contact with
                    if self.people_in[contact].susceptible==True and random.random()<=infection_prob:
                        
                        self.people_in[contact].get_infected() #there is a random chance of that contact becoming infected

#-----------------------------------------------------------------------------#

def Simulation(no_days=30, infection_prob=0.3, avg_contact=8, avg_time_trip=4):
        '''
        This will make the job of the main function for the simulation. All the 
        parameters have a standard value, but you can change them: no_days says
        the number of days of simulation; infection_prob is the probability with
        which a susceptible person, if in contact with an infected person, gets
        infected; avg_contact is the number of contacts a person has during one
        day and avg_time_trip is the limit to which a person can spend outside
        of their home city.
        '''
        
        city_network=hubs_generate(draw=True)
        nodes_list=list(city_network.nodes)
        
        #The population of each city will be proportional to the number of connections of the city
        #The four starting cities will be created separately        
        center=City(nodes_list[0], 2000*NumberofNeighbors(city_network, 1),1)
        subcenter1=City(nodes_list[1], 2000*NumberofNeighbors(city_network, 2), 11)
        subcenter2=City(nodes_list[2], 2000*NumberofNeighbors(city_network, 3), 12)
        subcenter3=City(nodes_list[3], 2000*NumberofNeighbors(city_network, 4), 13)
        cities_list=[center, subcenter1, subcenter2, subcenter3]
        
        for i in range(4, city_network.number_of_nodes()):
            new_city=City(nodes_list[i], 2000*NumberofNeighbors(city_network, i+1), 100+i)
            cities_list.append(new_city)
            
        distances=nx.all_pairs_shortest_path_length(city_network)
        #dict of the distances between nodes. distances[n1][n2] gives the distance
        #between nodes n1 and n2.
            
        for day in range(no_days):
            
            for city in cities_list:
                city.Internal_infection() #processes the internal infection before trips
                
                for destination in cities_list:
                    if distances[city][destination]!=0:
                        
                        travelers=travel_prob(d=distances[city.node][destination.node])*city.population
                        
                        for i in range(travelers):
                            traveler=random.choice(city.people_in)
                            traveler.travel(destination)
                            
            for city in cities_list:
                for person in city.people_in:
                    
                    person.pass_day
                    
'''
I haven't tested this code yet, the last time I used a simillar approach for this
with an incredibly higher population, my computer crashed, so be warned that 
problems might happen and I'm still in the process of finishing this code and
enhancing it.
'''


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
from scipy import stats
from NetworkGeneration import hubs_generate
import time

#--------------------------------------------------------------------------
a=1.9   
inf_prob=0.3

def travel_prob(d, l=a): #probability of someone traveling to a city at distance 
                           #d of them, a is just a constant.    
    return np.exp(-l*d)

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
    
    def __init__(self, home_city, current_city, heal_prob=0.1):
        
        self.susceptible=True
        self.infected=False
        self.immune=False
        self.home_city=home_city
        self.current_city=current_city
        self.days_infected=0 #number of days the person has been infected
        self.days_out_home=0
        self.heal_prob=heal_prob
        
    def get_infected(self):
        
        self.infected=True
        self.susceptible=False
        
    def heal(self):
        
        self.infected=False
        self.immune=True
        
    def travel(self, destination, index): #destination has to be a City object, 
        #and index is the index the person is in the list of people in the city
        
        self.current_city.people_in.pop(index) #pops the person from the list of the current city
        self.current_city=destination #sets a new current_city
        self.current_city.people_in.append(self) #puts the person in the list of that city
        
    def pass_day(self, index): #when a day passes, a few things happen
        
        if self.days_infected==14: #there is a 14 day limit for the person to heal
            self.heal()
        
        if self.infected==True: 
            self.days_infected+=1
        
        if self.days_out_home==5: #if they spend a lot of time out of their home city
            self.travel(self.home_city, index) #they go back home
        
        if self.current_city!=self.home_city:
            self.days_out_home+=1
            
        if random.random()<self.heal_prob:
            self.heal()
            
class City():
    '''
    This class is directed at objects meant to represent cities in a network of
    cities. The arguments to initialize this class are: a networkx node (node)
    and an int that represents the population of the city (population).
    '''
    
    def __init__(self, node, population, label):
        
        self.label=label
        self.node=node
        self.citizens=[Person(self, self) for i in range(population)] #the city starts with a healthy population
        self.population=population
        self.people_in=[] 
        #self.people_in stores the people in the city at a given moment, including
        #travelers and excluding people that traveled from the city
        
        for i in range(len(self.citizens)):
            self.people_in.append(self.citizens[i])
        
        self.infected=0
        
    def Internal_infection(self, avg_contact, infection_prob):
        
        for person in self.people_in: #for each citizen
            if person.infected==True: #the infected ones will test to see if they will infect someone
                
                for contact in range(avg_contact): #for each person they get contact with
                    if self.people_in[contact].susceptible==True and random.random()<=infection_prob:
                        
                        self.people_in[contact].get_infected() #there is a random chance of that contact becoming infected
                        
    def update_infected(self):
        
        self.infected=0
        
        for person in self.citizens:
            if person.infected==True:
                
                self.infected+=1

#----------------------------------------------------------------------------

def Simulation(no_days=60, infection_prob=inf_prob, avg_contact=8, avg_time_trip=4, Npatient0=1):
    '''
    This will make the job of the main function for the simulation. All the 
    parameters have a standard value, but you can change them: no_days says
    the number of days of simulation; infection_prob is the probability with
    which a susceptible person, if in contact with an infected person, gets
    infected; avg_contact is the number of contacts a person has during one
    day and avg_time_trip is the limit to which a person can spend outside
    of their home city.
    '''
               
    city_network=hubs_generate(m=2, N=3,draw=True)
    nodes_list=list(city_network.nodes)
    network_infected_list=[]
        
    #The population of each city will be proportional to the number of 
    #connections of the city. The four starting cities will be created 
    #separately.
    center=City(nodes_list[0], 2000*NumberofNeighbors(city_network, 1),1)
    subcenter1=City(nodes_list[1], 2000*NumberofNeighbors(city_network, 2), 11)
    subcenter2=City(nodes_list[2], 2000*NumberofNeighbors(city_network, 3), 12)
    subcenter3=City(nodes_list[3], 2000*NumberofNeighbors(city_network, 4), 13)
    cities_list=[center, subcenter1, subcenter2, subcenter3]
        
    for i in range(4, city_network.number_of_nodes()):
        new_city=City(nodes_list[i], 2000*NumberofNeighbors(city_network, i+1), 100+i)
        cities_list.append(new_city)
            
    distances=dict(nx.all_pairs_shortest_path_length(city_network))
    #dict of the distances between nodes. distances[n1][n2] gives the distance
    #between nodes n1 and n2.
         
    #N patients 0 in the central city:
    for i in range(Npatient0):
        rindex=random.randint(0, center.population-1)
        center.citizens[rindex].get_infected()
            
    #time simulation:
    for day in range(no_days):
            
        for city in cities_list:
            city.Internal_infection(avg_contact, infection_prob) #processes the internal infection before trips
                
            for destination in cities_list:
                if distances[city.node][destination.node]!=0:
                        
                    travelers=int(travel_prob(d=distances[city.node][destination.node])*len(city.people_in))
                        
                    for i in range(travelers):
                        traveler_index=random.randint(0,len(city.people_in)-1)
                        city.people_in[traveler_index].travel(destination, traveler_index)
            
        network_infected=0                
        for city in cities_list:
            city.update_infected()
            network_infected+=city.infected
            c=0 #counter
                
            while c<len(city.people_in):
                
                city.people_in[i].pass_day(i)
                c+=1
                
        network_infected_list.append(network_infected)
        print('Day ', day, ' simulated!')
        
    return cities_list, no_days, network_infected_list
                    
# -------------------------------------------------------------------------
                    
def Analyse_data(simulation_data, show_timeplot=True, show_logplot=True, save_timeplot=False, save_logplot=False):
    '''
    This function receives the result return of the Simulation function and plots
    the logarithm of the number of infected people on the cities with the 
    logarithm of the population of the corresponding city if show_logplot==True.
    In the future, I also intend to implement a linear regression of this plot.
    If show_timeplot==True, the function plots the time evolution of the disease.
    '''
    cities_list, days, infected_list=simulation_data
    
    if show_timeplot==True:
        days_list=[n+1 for n in range(days)]
        
        plt.figure()
        plt.title('Time evolution of the simulation')
        plt.plot(days_list, infected_list)
        plt.xlabel('Day')
        plt.ylabel('Non-cumulative Infected')
        plt.show()
        
        print('a=', a, '& Infection Prob.=', inf_prob)
        print('Number of Cities:', len(cities_list))
        
        if save_timeplot==True:
            plt.savefig('time_plot.png')
    
    if show_logplot==True:
        log_pop=[]
        log_infected=[]
        
        for city in cities_list:
            log_pop.append(np.log(city.population))
            log_infected.append(np.log(city.infected))
            
        slope, intercept, r, p, stdev=stats.linregress(log_pop, log_infected)
        
        x_list=[min(log_pop)+i*(max(log_pop)-min(log_pop))/10 for i in range(11)]
            
        plt.figure()
        plt.title('Logarithm plot of the simulation')
        plt.scatter(log_pop, log_infected)
        plt.plot(x_list, [slope*x+intercept for x in x_list], 'k')
        plt.xlabel('log(P)')
        plt.ylabel('log(I)')
        plt.show()
        
        print('Number of Cities:', len(cities_list))
        print('Slope: ', slope, '\nIntercept:', intercept, '\nStandard Deviation:', stdev)
        print('a=', a, '& Infection Prob.=', inf_prob)
        
        if save_logplot==True:
            plt.savefig('log_plot.png')
        
# -----------------------------------------------------------------------
            
def main():   
    simulation=Simulation()
    Analyse_data(simulation_data=simulation)

start_time=time.time()

if __name__=='__main__':
    main()   
    
print('Execution time: %s seconds' % (time.time() - start_time))
                    
'''
The code is working, but the results are not the ones expected.
'''


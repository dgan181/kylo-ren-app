#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jul 24 16:55:40 2020


"""

import sys
import pickle
from gen_utils import generate_leadsheet


'''Deployment Mode'''
'''Event Based Represenation'''
'''2 Models: Transformer, LSTM-based'''
'''See the parameters below to Adjust'''



'''1. Load Global Variables and Dictionaries'''
#load pickles for onehotencoders
encoders_trans = './aux_files/chords_encoders_all.pickle'
with open(encoders_trans, 'rb') as handle:
    TransEncoders = pickle.load(handle)
#[Encoder, Decoder]

#load valence and density test templates for setting the Encoder seq
val_temp_path = './aux_files/Valence_Templates.pickle'
with open(val_temp_path, 'rb') as handle:
    val_templates = pickle.load(handle)
    
dense_temp_path = './aux_files/Density_Templates.pickle'
with open(dense_temp_path, 'rb') as handle:
    dense_templates = pickle.load(handle)

##-------This has been added----------
temp = float(sys.argv[1])
timsig_n = sys.argv[2]
timsig_d = sys.argv[3]
time = "[" + str(timsig_n) + ", " + str(timsig_d) + "]"
num_bars = int(sys.argv[4])
val = str(sys.argv[5])
den = str(sys.argv[6])
modl = str(sys.argv[7])
print("We're in the generate script and have succesfully input the parameters")
##-------------------------------------

'''2. Set User Music Parameters'''
temperature = temp#for sampling, below 1.0 makes more safe predictions. Optimal Range 0.5 to 1.5
timesig = time #Available options 4/4 3/4 12/8 2/2 2/4 6/8
numOfBars = num_bars #number of desired bars #8-40
valence = val #desired average valence for chord arrangement from -2 to +2
density = den #desired average density for every bar: low, med, hig
model = modl #model selection: transformer or lstm

print(temperature , timesig, numOfBars, valence, density , model )




# '''2. Set User Music Parameters'''
# temperature = 0.9#for sampling, below 1.0 makes more safe predictions. Optimal Range 0.5 to 1.5
# timesig = str([4,4]) #Available options 4/4 3/4 12/8 2/2 2/4 6/8
# numOfBars = 12 #number of desired bars #8-40
# valence = '2' #desired average valence for chord arrangement from -2 to +2
# density = 'med' #desired average density for every bar: low, med, hig
# model = 'transformer' #model selection: transformer or lstm

'''3. Call the function to Generate'''

generate_leadsheet(temperature,timesig,numOfBars,valence,density,model,TransEncoders,
                   val_templates,dense_templates)





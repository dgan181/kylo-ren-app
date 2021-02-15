#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
# os.system("conda activate Music21")
# os.popen("conda activate Music21")
print("Hey, I'm the generate script")
"""
Created on Fri Jul 24 16:55:40 2020
# 
# @author: bougatsas
# """
import sys
import ast
import pickle
from tensorflow.keras import models
from aux_files.gen_aux import create_static_conditions,chords_mel_mid, chords_inf_model_ev, \
    generate_chord_durs_ev_seq

''' Input parameters
'''

arg1 = float(sys.argv[1])
# arg2 = sys.argv[2].strip('[]').split(',')
# arg2 = map(float, sys.argv[2].strip('[]').split(','))
arg2 = str(ast.literal_eval(sys.argv[2]))
arg3 = int(sys.argv[3])
arg4 = str(sys.argv[4])

print('hello again')
print(arg1,arg2,arg3,arg4)
print(type(arg1), type(arg2), type(arg3), type(arg4))

'''Change these parameters to adjust the Generation'''
""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
'''Set Global and Music Parameters'''
# temperature = 0.9#for sampling, below 1.0 makes safier predictions
# timesig = str([4,4]) #4/4 3/4 etc
# numOfBars = 16 #number of desired bars #8-40
# valence = '2' #desired valence for chord arrangement from -2 to +2
# print(temperature, timesig, numOfBars, valence)
# print(type(temperature), type(timesig), type(numOfBars), type(valence))


# if (arg1==temperature and arg2==timesig and arg3==numOfBars and arg4==valence):
#     print("we're good to run the script")


temperature = arg1#for sampling, below 1.0 makes safier predictions
timesig = arg2 #4/4 3/4 etc
numOfBars = arg3 #number of desired bars #8-40
valence = arg4 #desired valence for chord arrangement from -2 to +2
# print(temperature, timesig, numOfBars, valence)
# print(type(temperature), type(timesig), type(numOfBars), type(valence))



""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""


'''Do not edit after this line'''
""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

'''Valence Mode'''
'''Seq2Seq'''

'''Restore the models and load pickles for onehotencoders'''

encoders_trans = './aux_files/chords_encoders_all.pickle'


with open(encoders_trans, 'rb') as handle:
    TransEncoders = pickle.load(handle)
#[Encoder, Decoder]


enc_vocab= len(TransEncoders[0].categories_[0])
dec_vocab = len(TransEncoders[1].categories_[0])


#load valence templates for both representations
val_temp_path = './aux_files/Valence_Templates.pickle'
with open(val_temp_path, 'rb') as handle:
    val_templates = pickle.load(handle)



'''Encoder Decoder with Inference Models'''
LSTM_dim = 768
model_seq = models.load_model('./aux_files/ChordDurMel_LSTM.h5')
encoder_seq, decoder_seq= chords_inf_model_ev(model_seq, LSTM_dim) #2.seq2seq lstm


'''Generation Stage'''
stop_condition = False
while not stop_condition:
    try:
        print('Generating with seq2seq model...')
        '''Seq2seq BLSTM-LSTM'''
        allChords, allDurs, allMels = generate_chord_durs_ev_seq(encoder_seq, decoder_seq, TransEncoders,
                                    val_templates, timesig, temperature, numOfBars, valence)

        #create static instances for midi conversion

        f_chords, f_durs, f_melody, f_bars = create_static_conditions(allChords, allDurs, allMels)

        '''Save to midi file'''
        #default path is ./generations folder
        chords_mel_mid(f_chords,f_durs,f_bars,f_melody,timesig,'_seq2seq')
        print('Done!')
        stop_condition = True
    except IndexError:
        print('Exception Raised. Generation aborted. Trying again')




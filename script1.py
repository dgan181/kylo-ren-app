#  -----------------------------------------------

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
from Backend.seq2seq_test.aux_files.gen_aux import create_static_conditions,chords_mel_mid, chords_inf_model_ev, \
    generate_chord_durs_ev_seq
# ''' Input parameters
# '''

temp = float(sys.argv[1])
timsig_n = sys.argv[2]
timsig_d = sys.argv[3]
time = "[" + str(timsig_n) + ", " + str(timsig_d) + "]"
num_bars = int(sys.argv[4])
val = str(sys.argv[5])
print("We're in the generate script and have succesfully input the parameters")

'''Change these parameters to adjust the Generation'''
""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
'''Set Global and Music Parameters'''

#Default Global Parameters
# temperature = 0.9#for sampling, below 1.0 makes safier predictions
# timesig = str([4,4]) #4/4 3/4 etc
# numOfBars = 16 #number of desired bars #8-40
# valence = '2' #desired valence for chord arrangement from -2 to +2


temperature = temp#for sampling, below 1.0 makes safier predictions
timesig = time #4/4 3/4 etc
numOfBars = num_bars #number of desired bars #8-40
valence = val #desired valence for chord arrangement from -2 to +2

#If you need to check you inputs
# print(temperature, timesig, numOfBars, valence)
# print(type(temperature), type(timesig), type(numOfBars), type(valence))



""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""


'''Do not edit after this line'''
""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

'''Valence Mode'''
'''Seq2Seq'''

'''Restore the models and load pickles for onehotencoders'''

encoders_trans = './Backend/seq2seq_test/aux_files/chords_encoders_all.pickle'


with open(encoders_trans, 'rb') as handle:
    TransEncoders = pickle.load(handle)
#[Encoder, Decoder]


enc_vocab= len(TransEncoders[0].categories_[0])
dec_vocab = len(TransEncoders[1].categories_[0])


#load valence templates for both representations
val_temp_path = './Backend/seq2seq_test/aux_files/Valence_Templates.pickle'
with open(val_temp_path, 'rb') as handle:
    val_templates = pickle.load(handle)



'''Encoder Decoder with Inference Models'''
LSTM_dim = 768
model_seq = models.load_model('./Backend/seq2seq_test/aux_files/ChordDurMel_LSTM.h5')
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

print("This generate script is done")


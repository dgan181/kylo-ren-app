#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Aug  4 20:01:38 2020


"""
import json
import string
import numpy as np
import music21 as m21
import tensorflow as tf
#tf.compat.v1.disable_eager_execution()
from fractions import Fraction
from random import choice,randint
from copy import deepcopy
from aux_files import Encoder, Decoder


def generate_leadsheet(temperature,timesig,numOfBars,valence,density,model,
                       TransEncoders,val_templates,dense_templates):
    
    '''0. Set Global Variables for the Generation'''
    #for event based representation get Encoder-Decoder vocab
    enc_vocab= len(TransEncoders[0].categories_[0])
    dec_vocab = len(TransEncoders[1].categories_[0])
    
    LSTM_dim = 768 # the size of units of the implemented LSTM layers
    '''1. Create the Encoder Sequence'''
    
    enc_list = create_encoder_ev(TransEncoders,timesig,numOfBars,val_templates,dense_templates,
                                 valence,density)
    
    '''2. Load the Inference Model'''
    if model == 'transformer':
        nnModel = chord_trans_ev_model(enc_vocab,dec_vocab)
    else: #Lstm
    #load model weights and create inference
        model_seq = tf.keras.models.load_model('./aux_files/ChordDurMel_LSTM.h5')
        nnModel = chords_inf_model_ev(model_seq, LSTM_dim) #2 Models
        
    '''3. Generate the Lead Sheet'''
    allChords, allDurs, allMels = call_generation(temperature,timesig,numOfBars,
                                            TransEncoders,model,nnModel,enc_list)
    
    '''4. Generate the MIDI and musicXML files'''
    #create static conditions
    f_chords, f_durs, f_melody, f_bars = create_static_conditions(allChords, allDurs, allMels)
    #save midi file
    chords_mel_mid(f_chords,f_durs,f_bars,f_melody,timesig,model)
                


def call_generation(temperature,timesig,numOfBars,TransEncoders,model,nnModel,enc_list):
    #preparation of data
    dec_seq_length = 359
    enc_seq_length = 263
    
    #start generation
    if model == 'transformer':
        allChords, allDurs, allMels = generate_chord_durs_ev_trans(nnModel, enc_list,
                        timesig, temperature, numOfBars, TransEncoders, enc_seq_length, 
                        dec_seq_length)
    else: #LSTM
        allChords, allDurs, allMels = generate_chordur_ev_seq(nnModel[0], nnModel[1], 
                        enc_list, timesig, temperature, numOfBars, TransEncoders, 
                        enc_seq_length, dec_seq_length)    
        
    return allChords, allDurs, allMels
                

def generate_chordur_ev_seq(nnEncoder, nnDecoder, enc_list, timesig, temperature,
                      numOfBars, TransEncoders, enc_seq_length, dec_seq_length):
  # Encode the input as state vectors.
  
  dec_sos_idx = int(np.where(TransEncoders[1].categories_[0] == 'sos')[0])+1 #shifted by 1
  dec_eos_idx = int(np.where(TransEncoders[1].categories_[0] == 'eos')[0]) 
  
  pad_length = enc_seq_length-len(enc_list)
  enc_inp = np.array(enc_list+pad_length*[0]).reshape(1,-1)

  isValid = False #variable to check if the decoded out is indeed a) numOfBars bars
                    #and b) the durations of each bar is timesig duration
  cnt_valid = 1 #counter for the attempts
  while not isValid:
      print('Generating...Attempt no:',cnt_valid)
      #call Encoder first
      enc1_h, enc1_c, enc2_h, enc2_c, enc3_h, enc3_c  = nnEncoder.predict([enc_inp])
      s1_values = [enc1_h, enc1_c]
      s2_values = [enc2_h, enc2_c]
      s3_values = [enc3_h, enc3_c]
      
      # Prepare empty target sequences of length 1 for the decoder and 
      #put to the target seqs the last item from the encoder/seed
      cnt = 0
      dec_inp = np.array(dec_sos_idx).reshape(1,1)
       
      decoded_out = []
      
      #start generating and call Decoder
      stop_condition = False
      while not stop_condition:
          #call the decoder
          dec_out, dec1_h, dec1_c, dec2_h, dec2_c, dec3_h, dec3_c = nnDecoder.predict(
                [dec_inp]+s1_values+s2_values+s3_values)
          
          #sample the predictions with temperature(diversity)
          dec_pred = sample(dec_out.reshape(dec_out.shape[-1],), temperature)
    
          if dec_pred == dec_eos_idx or len(decoded_out) >= dec_seq_length:
             stop_condition = True
             #Success
             cnt = 0
             
          #add it to the sequences
          decoded_out.append(dec_pred)
                 
          #prepare for the next cycle  
          cnt += 1
          dec_inp = np.array(decoded_out[-1]+1).reshape(1,1)    
          
          # Update states
          s1_values = [dec1_h, dec1_c]
          s2_values = [dec2_h, dec2_c]
          s3_values = [dec3_h, dec3_c]

      #convert them to tokens
      allChords, allDurs, allMels = convert_to_ChordDurMels(decoded_out,TransEncoders)
      #check if it is valid out
      is_ok = validation_check (allChords, allDurs, allMels, timesig, numOfBars)
      if is_ok:
          print('Success!')
          isValid = True
      else:
          print('Failure.')
          cnt_valid += 1    
          
  return allChords, allDurs, allMels 


def generate_chord_durs_ev_trans(nnModel, enc_list,timesig, temperature, numOfBars, 
                                 TransEncoders, enc_seq_length, dec_seq_length):
    
    dec_sos_idx = int(np.where(TransEncoders[1].categories_[0] == 'sos')[0])+1 #shifted by 1
    dec_eos_idx = int(np.where(TransEncoders[1].categories_[0] == 'eos')[0]) 
    
    pad_length = enc_seq_length-len(enc_list)
    enc_inp = np.array(enc_list+pad_length*[0]).reshape(1,-1)
    
    dec_inp = [dec_sos_idx]
    dec_out = []
    
    isValid = False #variable to check if the decoded out is indeed a) numOfBars bars
                    #and b) the durations of each bar is timesig duration
    cnt_valid = 1 #counter for the attempts
    while not isValid:
        print('Generating...Attempt no:',cnt_valid)
        #start generating
        for _ in range(dec_seq_length):
           allPreds = nnModel.predict([enc_inp, np.array(dec_inp).reshape(1,-1)])
           aPred = allPreds[-1]
           #apply diversity
           token_pred = sample(aPred[-1,:].reshape(aPred.shape[-1],), temperature)
           dec_out.append(token_pred)
           if token_pred == dec_eos_idx:
               #EOS
               break
           else:
               #prepare for the next cycle
               dec_inp.append(token_pred+1)
        #convert them to tokens
        allChords, allDurs, allMels = convert_to_ChordDurMels(dec_out,TransEncoders)
        #check if it is valid out
        is_ok = validation_check (allChords, allDurs, allMels, timesig, numOfBars)
        if is_ok:
            print('Success!')
            isValid = True
        else:
            print('Failure.')
            cnt_valid += 1
            dec_inp = [dec_sos_idx]
            dec_out = []
    
    return allChords, allDurs, allMels 

def validation_check (allChords, allDurs, allMels, timesig, numOfBars):
    
    isValid = False
    
    #1. Check if they do not have the same length
    length = len(allChords)
    if any(len(lst) != length for lst in [allDurs, allMels]):
        return isValid

    #2. Check if all have numOfBars+1 'bar' events
    chords_bar_idxs = [i for i, x in enumerate(allChords) if x == 'bar']
    durs_bar_idxs = [i for i, x in enumerate(allDurs) if x == 'bar']
    mels_bar_idxs = [i for i, x in enumerate(allMels) if x == 'bar']
    if any(len(lst) != numOfBars+1 for lst in [chords_bar_idxs, durs_bar_idxs, mels_bar_idxs]):
        return isValid
    
    #3. Check of there is problem with duration of each bar according to the timesig
    timesig = json.loads(timesig)
    bar_lgt = 4*int(timesig[0])/int(timesig[1])
    total_dur = numOfBars*bar_lgt
    bar_idxs_d = {i for i, x in enumerate(allDurs) if x == "bar"}
    f_durs = [v for i, v in enumerate(allDurs) if i not in bar_idxs_d]
    f_durs_float = string_durs_to_float(f_durs)
    f_durs_cnt = sum(f_durs_float)
    if total_dur != f_durs_cnt:
        return isValid
    #check completed
    isValid = True
    
    return isValid

    
    

def chords_inf_model_ev(model_tr, LSTM_dim):
    
    '''Inference Model for event_based Enc-Dec'''
    # Encoder
    enc_inputs = model_tr.get_layer('input_var1').input

    encoder_shared_emb = model_tr.get_layer('encoder_embedding')    
    enc_emb = encoder_shared_emb(enc_inputs)
    
    
    encoder_1 = model_tr.get_layer('encoder_blstm_1')
    encoder1_outputs, forward1_h, forward1_c, backward1_h, backward1_c = encoder_1(enc_emb)
    state1_h = tf.keras.layers.Concatenate()([forward1_h, backward1_h])
    state1_c = tf.keras.layers.Concatenate()([forward1_c, backward1_c])
    encoder1_states = [state1_h, state1_c] 

    encoder_2 = model_tr.get_layer('encoder_blstm_2')
    encoder2_outputs, forward2_h, forward2_c, backward2_h, backward2_c = encoder_2(encoder1_outputs)
    state2_h = tf.keras.layers.Concatenate()([forward2_h, backward2_h])
    state2_c = tf.keras.layers.Concatenate()([forward2_c, backward2_c])
    encoder2_states = [state2_h, state2_c]    
    
    encoder_3 = model_tr.get_layer('encoder_blstm_3')
    encoder3_outputs, forward3_h, forward3_c, backward3_h, backward3_c = encoder_3(encoder2_outputs)
    state3_h = tf.keras.layers.Concatenate()([forward3_h, backward3_h])
    state3_c = tf.keras.layers.Concatenate()([forward3_c, backward3_c])
    encoder3_states = [state3_h, state3_c] 
    
    encoder_model = tf.keras.models.Model([enc_inputs], 
                                 encoder1_states+encoder2_states+encoder3_states)
    
    # Decoder
    dec_inputs = model_tr.get_layer('input_var2').input

    
    decoder_shared_emb = model_tr.get_layer('decoder_embedding')
    dec_emb = decoder_shared_emb(dec_inputs)
    
       
    decoder1 = model_tr.get_layer('decoder_lstm_1')
    decoder1_state_input_h = tf.keras.layers.Input(shape=(LSTM_dim*2,))
    decoder1_state_input_c = tf.keras.layers.Input(shape=(LSTM_dim*2,))
    decoder1_states_inputs = [decoder1_state_input_h, decoder1_state_input_c]  
    decoder1_outputs, decoder1_h, decoder1_c = decoder1(dec_emb, initial_state=decoder1_states_inputs)
    decoder1_states = [decoder1_h, decoder1_c]
    
  
    decoder2 = model_tr.get_layer('decoder_lstm_2')
    decoder2_state_input_h = tf.keras.layers.Input(shape=(LSTM_dim*2,))
    decoder2_state_input_c = tf.keras.layers.Input(shape=(LSTM_dim*2,))
    decoder2_states_inputs = [decoder2_state_input_h, decoder2_state_input_c]  
    decoder2_outputs, decoder2_h, decoder2_c = decoder2(decoder1_outputs, initial_state=decoder2_states_inputs)
    decoder2_states = [decoder2_h, decoder2_c]    
    
    decoder3 = model_tr.get_layer('decoder_lstm_3')
    decoder3_state_input_h = tf.keras.layers.Input(shape=(LSTM_dim*2,))
    decoder3_state_input_c = tf.keras.layers.Input(shape=(LSTM_dim*2,))
    decoder3_states_inputs = [decoder3_state_input_h, decoder3_state_input_c]  
    decoder3_outputs, decoder3_h, decoder3_c = decoder3(decoder2_outputs, initial_state=decoder3_states_inputs)
    decoder3_states = [decoder3_h, decoder3_c]  
    
    decoder_dense_melody = model_tr.get_layer('out_var1')
    decoder_outputs_melody = decoder_dense_melody(decoder3_outputs)
    
    decoder_model = tf.keras.models.Model([dec_inputs]+decoder1_states_inputs+decoder2_states_inputs+decoder3_states_inputs,
                                [decoder_outputs_melody]+decoder1_states+decoder2_states+decoder3_states)
    
    return encoder_model, decoder_model



def chord_trans_ev_model(enc_vocab,dec_vocab):
    #create the architecture first
    
    num_layers = 4  #4
    d_model = 48 #for Embedding 
    dff = 1536 #for Dense
    num_heads = 8 #8
    dropout_rate = 0.1

    enc_input = tf.keras.layers.Input(shape=(None,), name = 'input_var1')
    dec_input = tf.keras.layers.Input(shape=(None,), name = 'input_var2')
    
    encoder = Encoder(enc_vocab+1, num_layers = num_layers, d_model = d_model, num_heads = num_heads, dff = dff, dropout = dropout_rate)
    decoder = Decoder(dec_vocab+1, num_layers = num_layers, d_model = d_model*4, num_heads = num_heads, dff = dff, dropout = dropout_rate)
    
    x = encoder(enc_input)
    x = decoder([dec_input, x] , mask = encoder.compute_mask(enc_input))
    
    dec_output = tf.keras.layers.Dense(dec_vocab, activation='softmax', name = 'out_var1')
    out = dec_output(x)
    
    model = tf.keras.models.Model(inputs=[enc_input, dec_input], outputs=out)
    
    #load the weights
    model.load_weights('./aux_files/ChordDurMel_Trans_w.h5')
    
    return model
  


def sample(preds, temperature=1.0):
    '''
    @param preds: a np.array with the probabilities to all categories
    @param temperature: the temperature. Below 1.0 the network makes more "safe"
                        predictions
    @return: the index after the sampling
    '''
    # helper function to sample an index from a probability array
    preds = np.asarray(preds).astype('float64')
    preds = np.log(preds) / temperature
    exp_preds = np.exp(preds)
    preds = exp_preds / np.sum(exp_preds)
    probas = np.random.multinomial(1, preds, 1)
   
    return np.argmax(probas)  


def create_encoder_ev(TransEncoders,timesig,numOfBars,val_templates,dense_templates,valence,density):
    
    #create the encoder part. First define idxs   
    enc_sos_idx = int(np.where(TransEncoders[0].categories_[0] == 'sos')[0])+1 #all shifted
    enc_eos_idx = int(np.where(TransEncoders[0].categories_[0] == 'eos')[0])+1
    enc_bar_idx = int(np.where(TransEncoders[0].categories_[0] == 'bar')[0])+1
    enc_timesig_idx = int(np.where(TransEncoders[0].categories_[0] == timesig)[0])+1
    
    
    #select a random valence and density template 
    #select a template from >= numOfbars with the suggested average from the user
    stop_condition = False
    while not stop_condition:
        try:
            #set a random length to get a template
            lgt_r = str(randint(numOfBars,40))
            #check if the valence avg exists as an option
            enc_val = deepcopy(choice(list(val_templates[lgt_r][valence]))) 
            enc_val = enc_val[:numOfBars]

        except:
            continue
        stop_condition = True
    #do the same for density
    stop_condition = False
    while not stop_condition:
        try:
            #set a random length to get a template
            lgt_r = str(randint(numOfBars,40))
            #check if the valence avg exists as an option
            enc_den = deepcopy(choice(list(dense_templates[lgt_r][density]))) 
            enc_den = enc_den[:numOfBars]

        except:
            continue
        stop_condition = True                
        
    enc_list = [enc_sos_idx,enc_bar_idx]
    for i in range(0,numOfBars):
        #check for Grouing
        if i == 0:
           curr_group_idx = int(np.where(TransEncoders[0].categories_[0] == 'start1')[0])+1
        elif i == 1:
           curr_group_idx = int(np.where(TransEncoders[0].categories_[0] == 'start2')[0])+1
        elif i == numOfBars-2:
           curr_group_idx = int(np.where(TransEncoders[0].categories_[0] == 'end1')[0])+1
        elif i == numOfBars-1:
           curr_group_idx = int(np.where(TransEncoders[0].categories_[0] == 'end2')[0])+1
        else:
           curr_group_idx = int(np.where(TransEncoders[0].categories_[0] == '-')[0])+1
        #get the Valence Idx for this current bar
        aVal = str(enc_val[i])
        curr_val_idx = int(np.where(TransEncoders[0].categories_[0] == aVal)[0])+1
        #get the Density Idx for this current bar
        aDen = str(enc_den[i])
        curr_den_idx = int(np.where(TransEncoders[0].categories_[0] == aDen)[0])+1
        #apply with that order TimeSig,Grouping,Valence and bar
        enc_list.extend([enc_timesig_idx,curr_group_idx,curr_val_idx,curr_den_idx,enc_bar_idx ])

        
    enc_list.append(enc_eos_idx)
    
    return enc_list
        
def convert_to_ChordDurMels(dec_out,TransEncoders):
    
    dec_bar_idx = int(np.where(TransEncoders[1].categories_[0] == 'bar')[0])
    
    bar_idxs = [i for i, x in enumerate(dec_out) if x == dec_bar_idx]
    
    allChords = ['bar']
    allDurs = ['bar']
    allMels = ['bar']
    
    for i in range(0,len(bar_idxs)-1):
        #get the range
        leftR = bar_idxs[i]+1
        rigtR = bar_idxs[i+1]
        
        #first for chords  
        for c in range(leftR,rigtR,3):
            aChord_idx = dec_out[c]
            aChord = str(TransEncoders[1].categories_[0][aChord_idx])
            allChords.append(aChord)
            
        for m in range(leftR+1,rigtR,3):
            aMel_idx = dec_out[m]
            aMel = str(TransEncoders[1].categories_[0][aMel_idx])
            allMels.append(aMel)
            
        #then for durs
        for d in range(leftR+2,rigtR,3):
            aDur_idx = dec_out[d]
            aDur= str(TransEncoders[1].categories_[0][aDur_idx])
            allDurs.append(aDur)  
            
        #add bar events
        allChords.append('bar')
        allDurs.append('bar')
        allMels.append('bar')
        
    return allChords,allDurs,allMels
                     


def create_static_conditions(allChords, allDurs, allMels):
    #set grouping flags
    bar_idxs = [i for i, x in enumerate(allDurs) if x == "bar"]
        
    #get bar indications
    bar_info = len(allDurs)*['no_bar']
    bar_info[0] = 'bar'
    for i in bar_idxs[:-1]:
        bar_info[i+1] = 'bar'
    
    #remove the bar idxs
    bar_idxs_d = {i for i, x in enumerate(allDurs) if x == "bar"}
    f_chords = [v for i, v in enumerate(allChords) if i not in bar_idxs_d]
    f_durs = [v for i, v in enumerate(allDurs) if i not in bar_idxs_d]
    f_melody = [v for i, v in enumerate(allMels) if i not in bar_idxs_d]
    f_bars = [v for i, v in enumerate(bar_info) if i not in bar_idxs_d]
    
    
    return f_chords, f_durs, f_melody, f_bars



def string_durs_to_float(bar_durs):
    #auxilliary function to 
    
    #create new list
    float_durs = []
    for b in bar_durs:
        if '/' in b:
            nom = int(b.split('/')[0])
            den = int(b.split('/')[-1])
            fr = Fraction(nom,den)
            float_durs.append(fr)
        else:
            float_durs.append(float(b))
    
    return float_durs
    

def chords_mel_mid(f_chords,f_durs,f_bars,allMelody,timesig,prefix):
    
    #path for generations
    midi_out = './midi/'
    xml_out = './musicxml/'
    
    #create the m21 instance for MIDI
    rc = m21.stream.Stream()
    #set tonality and tempo (default 120 tempo or set it to tempo21)
    kf = m21.key.Key('C', 'major')
    tempo21 = m21.tempo.MetronomeMark(number=100)
    rc.append(kf)
    rc.append(tempo21)
    #create m21 instance for XML
    rx = m21.stream.Stream()
    rx.append(m21.text.TextBox(prefix+' generation'))
    #calculate all bars according to f_bars
    all_bars = [index for index, value in enumerate(f_bars) if value == 'bar']
    #add the last idx which is the len of the events
    all_bars.append(len(f_bars))
    melody = m21.stream.Part()
    fl = m21.instrument.Flute()
    melody.insert(0, fl)
    chords = m21.stream.Part()
    pp = m21.instrument.Piano()
    chords.insert(0, pp)
    melodyxml = m21.stream.Part()
    melodyxml.insert(0, fl)
    #get TimeSig nominator denominator
    timesig = json.loads(timesig)
    ts = m21.meter.TimeSignature(str(timesig[0])+'/'+str(timesig[1]))

    for m in range(0,len(all_bars)-1):
        #create measure
        cho_m = m21.stream.Measure()
        mel_m = m21.stream.Measure()
        melxml_m = m21.stream.Measure()
        if m == 0:
            clef_s = m21.clef.TrebleClef()
            clef_b = m21.clef.BassClef()
            cho_m.insert(0, clef_b)
            cho_m.insert(0, ts)
            mel_m.insert(0, clef_s)
            mel_m.insert(0, ts)
            melxml_m.insert(0, clef_s)
            melxml_m.insert(0, ts)
            
        #for lead sheet only melody track will be given with chord symbols
        bar_prev = all_bars[m]
        bar_new = all_bars[m+1]
        #get the sum of durations
        bar_durs = f_durs[bar_prev:bar_new]
        bar_durs = string_durs_to_float(bar_durs)
        #get the chord list for this bar
        bar_chords = f_chords[bar_prev:bar_new]
        bar_melody = allMelody[bar_prev:bar_new]
        offset = 0.0
        prevChord = ''
        for b in range(0,len(bar_chords)):
            cho = bar_chords[b]
            dur = bar_durs[b]
            mel = bar_melody[b]
            if cho == 'Rest':
               aChord_t = m21.note.Rest() 
               aChord_name = 'Rest'
            else:
               aChord_s = m21.harmony.ChordSymbol(cho)
               pitchNames = [p for p in aChord_s.pitches]
               aChord_t = m21.chord.Chord(pitchNames)
               aChord_name = aChord_t.pitchedCommonName
            if prevChord == aChord_name:
                apC = cho_m.pop(-1)
                apC.quarterLength += float(dur)
                cho_m.append(apC)
            else: 
                aChord_t.offset = offset
                aChord_t.quarterLength = float(dur)
                cho_m.append(aChord_t)
                #append Chord Symbol if it is not rest
                if aChord_name != 'Rest':
                    aChord_s.offset = offset
                    aChord_s.writeAsChord = False
                    melxml_m.append(aChord_s) # add the chord symbol to mel track
                prevChord = aChord_name
            if mel == 'Rest' or mel =='eos': #check if to create a Note or Rest and set offset
                aNote = m21.note.Rest()
            else: #set pitch also
                pitch = m21.pitch.Pitch()
                pitch.midi = int(mel)
                aNote = m21.note.Note()
                aNote.pitch = pitch               
            #set onset and duration and append it
            aNote.offset = offset
            aNote.quarterLength = float(dur)
            mel_m.append(aNote) 
            melxml_m.append(aNote)
            offset = dur
        ############################  
        #append the measures to the parts
        chords.append(cho_m)
        melody.append(mel_m)
        melodyxml.append(melxml_m)
    #append the parts to the MIDI and XML streams
    #create end bar lines
    #chords[-1].append(m21.bar.Barline(type='final'))
    #melody[-1].append(m21.bar.Barline(type='final'))
    # MIDI
    rc.append(melody)
    rc.append(chords)
    # XML
    rx.append(melodyxml)
    rx.append(chords)
    #get random string seed
    rstr = randomString(5)
    #first MIDI
    mf = m21.midi.translate.streamToMidiFile(rc)
    midiOut = midi_out+'music.mid'
    mf.open(midiOut, 'wb')
    mf.write()
    mf.close()   
    print(midiOut, ' has been generated!')
    #then musicXML
    mx = m21.musicxml.m21ToXml.GeneralObjectExporter(rx)
    xmlOut = xml_out+'sheet.xml'
    mxText = mx.parse().decode('utf-8')
    f = open(xmlOut, 'w')
    f.write(mxText.strip())
    f.close()   
    print(xmlOut, ' has been generated!')
    
    
def randomString(stringLength=10):
    """Generate a random string of fixed length """
    letters = string.ascii_lowercase
    return ''.join(choice(letters) for i in range(stringLength))
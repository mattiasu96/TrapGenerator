#%% Import completo
import tensorflow as tf
from tensorflow.keras.models import Sequential, load_model
from tensorflow.keras.layers import Dense, Activation, Dropout
from tensorflow.keras.layers import LSTM
from tensorflow.keras.utils import get_file
import numpy as np
import random
import sys
import os
import shutil
import pdb
from mydy import Events, FileIO, Containers, Constants

#Base dir
from beta.settings import BASE_DIR
thisPath = os.path.join(BASE_DIR, 'templates\pyScript')
#Bear in mind that the relative path is from your Django project's root folder.


#%% Variabili che devono essere uguali in training e prediction
n_epochs = 50 #per debug ho messo 15 ,  50 quello serio
quant = 32
maxlenUSER = 256*2
batchSizeSET = 128
stepUSER = 8 #o 256
NCP = 33*2 #17*32
pathDB = thisPath + '/datasetartificial 32note.txt' # Corpus file
pathOUT = thisPath + '/kaggle/working/'
pathGen = BASE_DIR + '/templates/midiGen/'
filename_gen_txt = ''
#32esimi: dovresti raddoppiare il maxlen e lo step_size,

#%% Diversity
idDiv = 3 #l'user deve scegliere questo
diversityArray = [0.9, 1.0, 1.2, 1.5, 2]
divUSER = diversityArray[idDiv]
filename_gen_txt = ('%sdrumloop_%4.2f.txt' % (pathGen, divUSER))
filename_gen_midi = ('%sdrumloop_%4.2f.mid' % (pathGen, divUSER))
static_midi = ('midiGen/drumloop_%4.2f.mid' % (divUSER))

def sample(preds, temperature=1.0):
    preds = np.asarray(preds).astype('float64')
    preds = np.log(preds) / temperature
    exp_preds = np.exp(preds)
    preds = exp_preds / np.sum(exp_preds)
    probas = np.random.multinomial(1, preds, 1)
    return np.argmax(probas)

#%% RUN
def runPrediction(is_character=False, maxlen=None, num_units=None, model_prefix=''):
    #carica modello e pesi
    model = load_model(thisPath + '/kaggle/working/model_alt.h5', compile = False)

    character_mode = is_character

    if character_mode:
        if maxlen == None:
            maxlen = 1024
        if num_units == None:
            num_units = 32
        step = 2*17 # step to create training data for truncated-BPTT
    else: # word mode
        if maxlen == None:
            maxlen = 256 # maxlength used in RNN input
        if num_units == None: 
            num_units = 512 #number of unit per layer LSTM 512 
        step = stepUSER

    if character_mode:
        num_char_pred = maxlen*3/2
    else: 
        num_char_pred = NCP #17*32 #17*30 this should be the number of elements predicted in the output. How "long" is my output sequence
    num_layers = 2
    # 
    if character_mode:
        prefix = 'char'
    else:
        prefix = 'word'

    path = pathDB # Corpus file
    text = open(path).read()
    print('corpus length:', len(text))

    if character_mode:
        chars = set(text)
    else:
        chord_seq = text.split(' ')
        chars = set(chord_seq) #contains the unique words in my dictionary. They are 119
        text = chord_seq #contains the full text in an array format. Each entry of my array is a word of type 0xb0110101010 

    char_indices = dict((c, i) for i, c in enumerate(chars))
    indices_char = dict((i, c) for i, c in enumerate(chars))
    num_chars = len(char_indices) #number of unique words in my training set
    print('total chars:', num_chars)

    # cut the text in semi-redundant sequences of maxlen characters

    sentences = []
    next_chars = []
    #Here im creating the inputs and targets for my RNN. Each single input has length maxlen.
    #Inputs are semi-redundant, in the sense that i take a length of maxlen=128 and the step is 8. So my first part of the input
    #will be the same and the last 8 elements are "new". I'm just "slitting" of 8 notes ahead
    for i in range(0, len(text) - maxlen, step): #iterates over the range with steps of 8.
        sentences.append(text[i: i + maxlen])
        next_chars.append(text[i + maxlen])
    print('nb sequences:', len(sentences))
    print('Vectorization...')
    
    #Here i'm creating the input dataset and target dataset for my network
    #X is a tri-dimensional vector: 1 dimension -> Sentences, 2 dimension -> Single sentence, 3 dimension -> one hot encoded vector of the single word
    #So basically i have a structure where i have N sentences of maxlen Words where each word is represented as a one hot vector of length num_chars
    X = np.zeros((len(sentences), maxlen, num_chars), dtype=np.bool) #Input matrix
    y = np.zeros((len(sentences), num_chars), dtype=np.bool) #Target Matrix
    #Here i'm actually "populating" the matrixes, which were initialized with all zeros
    print('Entering initialization cycle')

    for i, sentence in enumerate(sentences):
        for t, char in enumerate(sentence):
            X[i, t, char_indices[char]] = 1 #NB: char in this case means a whole word like oxb01011101. With char_indices[char] i'm retrieving the index of my word inside my dictionary of (words,index)
        #print('Finished input initialization')
        y[i, char_indices[next_chars[i]]] = 1
    print('Completed Vectorization')
    
    # build the model: 2 stacked LSTM
    # model = get_model(maxlen, num_chars, num_layers, num_units) 
    
    #Just some string declarations for folders management and names.
    #NB: CHANGE THE / with \ for windows! 

    # result_directory = 'r_%s_%s_%d_%d_units/' % (prefix, model_prefix, maxlen, num_units)
    result_directory = pathGen
    filepath_model = os.path.join(result_directory, '/kaggle/working/best_model.hdf')

    #filepath_model = '%sbest_model.hdf' % result_directory
    description_model = '%s, %d layers, %d units, %d maxlen, %d steps' % (prefix, num_layers, num_units, maxlen, step)
    
    #Usual Model checkpoints and Early Stopping
    checker = tf.keras.callbacks.ModelCheckpoint(filepath_model, monitor='loss', verbose=0, save_best_only=True, mode='auto')
    early_stop = tf.keras.callbacks.EarlyStopping(monitor='loss', patience=15, verbose=0, mode='auto')
    
    #create a result directory if it doesn't exist
    if not os.path.exists(result_directory):
        os.mkdir(result_directory)

    # write a description file.
    #creates an empty file with the drscription of my model as title
    #with open(result_directory+descri  ption_model, 'w') as f_description:
    #     pass

    # train the model, output generated text after each iteration
    batch_size = batchSizeSET #Size of a training batch. So basically i'll update my loss function every 128 input sentences (usual batch gradient descent)
    loss_history = []
    pt_x = [n_epochs]
    #An epoch is a complete iteration over the whole input training set. So 10 epochs means that i iterates 10 times over my input dataset
    nb_epochs = [np.sum(pt_x[:i+1]) for i in range(len(pt_x))] #array containing many epochs length. The model will be fitted many times, one for each nb_epochs.

    # not random seed, but the same seed for all.
    #A random seed (or seed state, or just seed) is a number (or vector) used to initialize a pseudorandom number generator.
    start_index = random.randint(0, len(text) - maxlen - 1)

    for iteration, nb_epoch in zip(pt_x,nb_epochs):
        if os.path.exists('/kaggle/working/stop_asap.keunwoo'):
            os.remove('/kaggle/working/stop_asap.keunwoo')
            break

        # print('-' * 50)
        # print('Iteration', iteration)
        
        #fitting model over nb_epochs
        #result = model.fit(X, y, batch_size=batch_size, nb_epoch=nb_epoch, callbacks=[checker, early_stop]) 
        #loss_history = loss_history + result.history['loss']

        # print ('Saving model after %d epochs...' % nb_epoch)
        #Saving model weights. Saving a model trained over nb_epochs
        #model.save_weights('%smodel_after_%d.hdf'%(result_directory, nb_epoch), overwrite=True) 
        #model.load_weights("model_weights.h5")
        #w2 = model.get_weights()
        #print(w2)

        
        diversity = divUSER
        filename_gen_txt = ('%sdrumloop_%4.2f.txt' % (result_directory, diversity))
        #creates a .txt file where i will save my predictions
        # with open(('%sresult_%s_iter_%02d_diversity_%4.2f.txt' % (result_directory, prefix, iteration, diversity)), 'w') as f_write:
        with open(filename_gen_txt, 'w') as f_write:
            print()
            print('----- diversity:', diversity)
            #f_write.write('diversity:%4.2f\n' % diversity)
            if character_mode:
                generated = ''
            else:
                generated = [] #simple initialization
            #selects a random sentence from my input dataset.
            sentence = text[start_index: start_index + maxlen]
            seed_sentence = text[start_index: start_index + maxlen]

            if character_mode:
                generated += sentence
            else:
                #at first iteration i just add my input sentence in my generated element
                generated = generated + sentence


            print('----- Generating with seed:')

            if character_mode:
                print(sentence)
                sys.stdout.write(generated)
            else:
                print(' '.join(sentence))

            for i in range(num_char_pred): 
                # if generated.endswith('_END_'):
                # 	break
                x = np.zeros((1, maxlen, num_chars)) #initialization of input. Matrix of maxlen words, each 

                for t, char in enumerate(sentence):
                    x[0, t, char_indices[char]] = 1. 

                preds = model.predict(x, verbose=0)[0] 
                #print('printo la prediction')
                #print(preds)
                next_index = sample(preds, diversity)
                next_char = indices_char[next_index]
                #print('printo il next char')
                #print(next_char)

                if character_mode:
                    generated += next_char
                    sentence = sentence[1:] + next_char
                else:
                    generated.append(next_char)
                    sentence = sentence[1:]
                    sentence.append(next_char)
                    #print('printo la sentence generata')
                    #print(generated)

                if character_mode:
                    sys.stdout.write(next_char)
                # else:
                # 	for ch in next_char:
                # 		sys.stdout.write(ch)	

                sys.stdout.flush()

            if character_mode:
                f_write.write(seed_sentence + '\n')
                f_write.write(generated)
            else:
                f_write.write(' '.join(seed_sentence))
                
                f_write.write(' ' .join(generated))

        # np.save('/kaggle/working/%sloss_%s.npy'%(result_directory, prefix), loss_history)

    print ('Done!')

#chiamo run() dopo

# ---------------------------------------------------------------------------------------------------
#%% Txt to MIDI conversion in the following cells
def roundup(numToRound, multiple):
    if multiple == 0:
        return numToRound
    remainder = numToRound % multiple
    if remainder==0:
        return numToRound
    return numToRound + multiple - remainder

#Function responsible for converting midi notes into text. Since i have to train my network over the structure i decided
#which is 0b0000000 for no note, 0b01000000 for kick ecc... i need to convert midi notes into this format.

#The original script used for midi-text translation has been lost, must be re-implemented again

PPQ = 480 # Pulse per quater note. Used in sequencers. Standard value
event_per_bar = 16 # to quantise.
min_ppq = PPQ / (event_per_bar/4)

# ignore: 39 hand clap, 54 tambourine, 56 Cowbell, 58 Vibraslap, 60-81

#the dictionary below maps values to other ones. Reduced the size of the used notes. For example
#if i have an eletric snare or a stick snare, i just map both of them into a standard snare

drum_conversion = {35:36, # acoustic bass drum -> bass drum (36)
                    37:38, 40:38, # 37:side stick, 38: acou snare, 40: electric snare
                    43:41, # 41 low floor tom, 43 ghigh floor tom
                    47:45, # 45 low tom, 47 low-mid tom
                    50:48, # 50 high tom, 48 hi mid tom
                    44:42, # 42 closed HH, 44 pedal HH
                    57:49, # 57 Crash 2, 49 Crash 1
                    59:51, 53:51, 55:51, # 59 Ride 2, 51 Ride 1, 53 Ride bell, 55 Splash
                    52:49 # 52: China cymbal
                    }

#Used in the code to map elements, everything that has not one of the following number is discarded.
#Basically i'm ignoring notes that are not in my dataset (for examle i'll ignore shakers ecc...)
                # k, sn,cHH,oHH,LFtom,ltm,htm,Rde,Crash
allowed_pitch = [36, 38, 42, 46, 41, 45, 48, 51, 49] # 46: open HH
cymbals_pitch = [49, 51] # crash, ride
cymbals_pitch = [] # crash, ride


#mapping midi values into notes
pitch_to_midipitch = {36:Constants.C_3,  # for logic 'SoCal' drum mapping
                        38:Constants.D_3, 
                        39:Constants.Eb_3,
                        41:Constants.F_3,
                        42:Constants.Gb_3,
                        45:Constants.A_3,
                        46:Constants.Bb_3,
                        48:Constants.C_4,
                        49:Constants.Db_4,
                        51:Constants.Eb_4
                        }
#la singola nota è un elemento composto da pitch (numerico, pitch midi) e tick (modo per tenere il tempo in midi)
class Note:
    def __init__(self, pitch, c_tick):
        self.pitch = pitch
        self.c_tick = c_tick # cumulated_tick of a midi note

    def add_index(self, idx):
        '''index --> 16-th note-based index starts from 0'''
        self.idx = idx

class Note_List():
    def __init__(self):
        ''''''
        self.notes = []
        self.quantised = False
        self.max_idx = None

    def add_note(self, note):
        '''note: instance of Note class'''
        self.notes.append(note)

    def quantise(self, minimum_ppq):
        '''
        e.g. if minimum_ppq=120, quantise by 16-th note.
        
        '''
        if not self.quantised:
            for note in self.notes:
                note.c_tick = ((note.c_tick+minimum_ppq/2)//minimum_ppq)* minimum_ppq # quantise
                #here the index is calculated. The index is an absolute index over the 16th notes.
                #for example an index of value 34, means that my current note appears after 34 chromes
                #it's simply calculated by dividing the cumulated tick of the note by the ticks contained in a 16th note
                note.add_index(note.c_tick/minimum_ppq)
            #NB: THE QUANTIZATION FUNCTION ITERATES OVER ALL THE NOTES. So first i add all the notes, then i iterate and quantize

            #Does this automatically reference to the last item added?
            #YES. The counter note will store the last element of the iteration. So basically here i'm assigning as max index the index of the last added note
            self.max_idx = note.idx

            #Here checks if if my ending is a full musical bar. For example, if my file ends with a single kick, i'll add that note.
            #but that kick will (probably) be at the beginning of the last musical bar. So i have to "pad" until the end.
            #It's like adding a pause on my piece, so i have all complete bars and no trucated ones at the end
            if (self.max_idx + 1) % event_per_bar != 0:
                self.max_idx += event_per_bar - ((self.max_idx + 1) % event_per_bar) # make sure it has a FULL bar at the end.
            self.quantised = True

        return

    def simplify_drums(self):
        ''' use only allowed pitch - and converted not allowed pitch to the similar in a sense of drums!
        '''
        #Here forces conversion into the pitches in drum_conversion
        for note in self.notes:
            if note.pitch in drum_conversion: # ignore those not included in the key
                note.pitch = drum_conversion[note.pitch]
        #https://stackoverflow.com/questions/30670310/what-do-brackets-in-a-for-loop-in-python-mean
        #The following one is a list comprehension. Basically generates a new list from an existing one using a given condition on the elements
        self.notes = [note for note in self.notes if note.pitch in allowed_pitch]	

        return

    def return_as_text(self):
        ''''''
        length = int(self.max_idx + 1) # of events in the track.
        #print(type(length))
        event_track = []
        #Thw following cycle create a 9 by N matrix. I append N times a vector of nine zeros.
        #This means that i create N notes, and then i initialize them with all zeros (9 zeros, since a note is represented by a 9 element binary number)

        for note_idx in range(length):  #sostituire xrange con range in Python3
            event_track.append(['0']*len(allowed_pitch))

        num_bars = length/event_per_bar# + ceil(len(event_texts_temp) % _event_per_bar)

        for note in self.notes:
            pitch_here = note.pitch
            #The following line returns the index of the passed pitch. Basically given an input generic pitch
            #it returns the associated pitch in my vocabolary (computes the actual mapping from the whole
            #vocabolary of notes into my reduced one)
            note_add_pitch_index = allowed_pitch.index(pitch_here) # 0-8
            #print(type(note.idx))  
            #print(type(note_add_pitch_index))
            event_track[int(note.idx)][note_add_pitch_index] = '1'
            # print note.idx, note.c_tick, note_add_pitch_index, ''.join(event_track[note.idx])
            # pdb.set_trace()

        event_text_temp = ['0b'+''.join(e) for e in event_track] # encoding to binary

        event_text = []
        # event_text.append('SONG_BEGIN')
        # event_text.append('BAR')
        print(num_bars)
        print(type(num_bars))        
        for bar_idx in range(int(num_bars)):
            event_from = bar_idx * event_per_bar
            event_to = event_from + event_per_bar
            event_text = event_text + event_text_temp[event_from:event_to]
            event_text.append('BAR')

        # event_text.append('SONG_END')

        return ' '.join(event_text)
    
    #Function that converts txt to notes. The note is represented as a number (in the MIDI scale)

#in encoded drums ho una riga intera dal file (quindi i vari 0xb00101110) 
def text_to_notes(encoded_drums, note_list=None):
    ''' 
    0b0000000000 0b10000000 ...  -> corresponding note. 
    '''
    if note_list == None:
        note_list = Note_List()
#https://www.programiz.com/python-programming/methods/built-in/enumerate enumerate mi ritorna coppie di (indice,valore) 
    for word_idx, word in enumerate(encoded_drums):
        c_tick_here = word_idx*min_ppq 

        for pitch_idx, pitch in enumerate(allowed_pitch):

            if word[pitch_idx+2] == '1':
                new_note = Note(pitch, c_tick_here)
                note_list.add_note(new_note)
    return note_list

def conv_text_to_midi(filename):
    if os.path.exists(filename[:-4]+'.mid'):
        print("Midi già esistente")
        return
    f = open(filename, 'r')
    #These multiple readlines are actually useless. Need to check the output of the NN, but right now they're useless.
    #One single readline is enough
    #f.readline() # title
    #f.readline() # seed sentence
    #legge una riga intera dal file
    sentence = f.readline()
    #splitta gli elementi letti a ogni spazio.
    encoded_drums = sentence.split(' ')
    # print('printing encoded drums')
    # print(encoded_drums)
    #find the first BAR

    first_bar_idx = encoded_drums.index('BAR') 

    #encoded_drums = encoded_drums[first_bar_idx:]
    try:
        encoded_drums = [ele for ele in encoded_drums if ele not in ['BAR', 'SONG_BEGIN', 'SONG_END', '']]
    except:
        pdb.set_trace()

    # prepare output
    note_list = Note_List()
    pattern = Containers.Pattern(fmt=0) #Don't know why there's an assertion in the code for fmt=0 if Pattern.len < 1
    track = Containers.Track()
    #??
    PPQ = 480
    min_ppq = PPQ / (event_per_bar/4)
    track.resolution = PPQ # ???? too slow. why??
    pattern.resolution = PPQ
    # track.resolution = 192
    pattern.append(track)

    velocity = 84
    duration = min_ppq*9/10  # it is easier to set new ticks if duration is shorter than _min_ppq

    note_list = text_to_notes(encoded_drums, note_list=note_list)

    max_c_tick = 0 
    not_yet_offed = [] # set of midi.pitch object
    # print('entering for note_idx cycle')
    #In this cycle im adding all the notes except the very last one
    for note_idx, note in enumerate(note_list.notes[:-1]):
        # add onset
        tick_here = note.c_tick - max_c_tick #extracting relative tick
        pitch_here = pitch_to_midipitch[note.pitch]

        on = Events.NoteOnEvent(tick=tick_here, velocity=velocity, pitch=pitch_here)
        track.append(on)
        max_c_tick = max(max_c_tick, note.c_tick)
        
        # crea un buffer di note da 'spegnere' se le successive sono allo stesso tick della corrente
        if note_list.notes[note_idx+1].c_tick == note.c_tick:
            not_yet_offed.append(pitch_here)
        else: #se le note successive sono a un tick successivo spengo le note ancora accese
        #questo non era indentrato correttamente
            not_yet_offed.append(pitch_here)
            # print("inizia ciclo off")
            # print(not_yet_offed) #ricorda di mettere nel buffer anche la nota corrente
            for off_idx, waiting_pitch in enumerate(not_yet_offed):
                # spegni la prima a tick+duration
                if off_idx == 0: 
                    off = Events.NoteOffEvent(tick=duration, pitch=waiting_pitch)
                    max_c_tick = max_c_tick + duration
                else: #spegni le altre sempre a tick + duration (ma relative tick is 0)
                    off = Events.NoteOffEvent(tick=0, pitch=waiting_pitch)
                track.append(off)
            not_yet_offed = [] # svuota il buffer 

    # finalise
    # print("finalise")
    if note_list.notes == []:
        print ('No notes in %s' % filename)
        return
        pdb.set_trace()
    #here i'm going to add the last note and close the track with the EndEvent
    # print("$$ here i'm going to add the last note and close the track with the EndEvent")
    note = note_list.notes[-1]
    tick_here = note.c_tick - max_c_tick
    pitch_here = pitch_to_midipitch[note.pitch]
    on = Events.NoteOnEvent(tick=tick_here, velocity=velocity, pitch=pitch_here)
    track.append(on)
    off = Events.NoteOffEvent(tick=duration, pitch=pitch_here)
    track.append(off)

    # print("off ciclo")
    for off_idx, waiting_pitch in enumerate(not_yet_offed):
        off = Events.NoteOffEvent(tick=0, pitch=waiting_pitch)
        track.append(off)
    # track.append(off)
    
    # end of track event
    # print("end of track event")
    eot = Events.EndOfTrackEvent(tick=1)
    track.append(eot)
    # Write midi
    FileIO.write_midifile(filename[:-4]+'.mid', pattern)    

# Crea file alla fine di tutto
checkFile = (thisPath + '/checkFile.666')
def createCheckFile():
    # checkFile = os.path.join(thisPath, '/checkFile.666')
    with open(checkFile, 'w') as file: 
        pass

# do some cleaning
def clean_folder(folderpath):
    folder = folderpath
    for filename in os.listdir(folder):
        file_path = os.path.join(folder, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print('Failed to delete %s. Reason: %s' % (file_path, e))


def pulizzzia(ctrlString):
    if ctrlString == 'old':
        #cancella evenutuali vecchi file - txt, midi, checkfile
        tempFolder = pathGen #midigen
        clean_folder(tempFolder)
        if os.path.exists(checkFile):
            os.remove(checkFile)
        else:
            print("checkfile does not exist")
    elif ctrlString == 'useless':
        #cancella file inutili (txt)
        if os.path.exists(filename_gen_txt):
            os.remove(filename_gen_txt)
        else:
            print("TXT file does not exist") 
        

#%% QUI CHIAMO LE FUNZIONI
def runAll():
    pulizzzia('old')

    # Questo genera il txt
    runPrediction(False, maxlenUSER, None , '')


    # Questo converte txt to midi
    # tempdir = './r_word__%d_%d_units/result_word_iter_%d_diversity_%4.2f.txt' % ( maxlenUSER, 512,n_epochs, divUSER)
    tempdir = filename_gen_txt
    print("tempdir", tempdir)
    conv_text_to_midi(tempdir)

    createCheckFile()
    pulizzzia('useless')
    print('success runAll')


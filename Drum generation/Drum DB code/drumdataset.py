import os, fnmatch
from random import randrange
from math import ceil
import random
import string
from mydy import Events, FileIO, Containers, Constants

def find(pattern, path):
    result = []
    for root, dirs, files in os.walk(path):
        for name in files:
            if fnmatch.fnmatch(name, pattern):
                result.append(os.path.join(root, name))
    return result

def randomString(stringLength=8):
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(stringLength))

# FIND FILES
kick_files = []
snare_files = []
hh_files = []
len4 = 2

kick_files = find( '*[Kick].mid', 'Drums')
snare_files = find( '*[?Snare].mid', 'Drums')
hh_files = find( '*[Hat].mid', 'Drums')

print(kick_files)
print(snare_files)
print(hh_files)

Nit = 1000

for x in range(Nit):
    # KICK
    maxLen = len(kick_files)
    i=randrange(0,maxLen)
    #print(kick_files[i])
    k_midi = FileIO.read_midifile(kick_files[i]) #returns a Pattern with the MIDI file information (resolution ecc...), based on documentation https://github.com/jameswenzel/mydy/blob/master/src/FileIO.py
    k_midi.resolution=480
    #print(k_midi)

    k_track = k_midi[1] #selecting the track (since it's only one, it will be always at index 0)k_track = k_track.make_ticks_abs()# Converting time from relative to an absolute measure

    k_flt=k_track.filter(lambda e: isinstance(e, (Events.NoteOnEvent, Events.NoteOffEvent)))# Selects only Note_On events, i'm discarding the note off

    c1 = 36
    for element in k_flt :
        current_note = element.data[0]
        if current_note != c1:
            element.data[0] = c1

    # SNARE
    maxLen = len(snare_files)
    i=randrange(0,maxLen)
    #print(snare_files[i])
    s_midi = FileIO.read_midifile(snare_files[i]) #returns a Pattern with the MIDI file information (resolution ecc...), based on documentation https://github.com/jameswenzel/mydy/blob/master/src/FileIO.py
    s_midi.resolution=480

    s_track = s_midi[1] #selecting the track (since it's only one, it will be always at index 0)

    s_flt=s_track.filter(lambda e: isinstance(e, (Events.NoteOnEvent, Events.NoteOffEvent)))# Selects only Note_On events, i'm discarding the note off

    d1 = 38
    for element in s_flt :
        current_note = element.data[0]
        if current_note != d1:
            element.data[0] = d1

    # HH
    maxLen = len(hh_files)
    i=randrange(0,maxLen)
    #print(hh_files[i])
    hh_midi = FileIO.read_midifile(hh_files[i]) #returns a Pattern with the MIDI file information (resolution ecc...), based on documentation https://github.com/jameswenzel/mydy/blob/master/src/FileIO.py
    hh_midi.resolution=480

    hh_track = hh_midi[1] #selecting the track

    hh_flt=hh_track.filter(lambda e: isinstance(e, (Events.NoteOnEvent, Events.NoteOffEvent)))# Selects only Note_On events, i'm discarding the note off

    fd1 = 42
    for element in hh_flt :
        current_note = element.data[0]
        if current_note != fd1:
            element.data[0] = fd1

    totLen = hh_flt.length/480
    totLen = ceil(totLen)
    if  totLen < 8: 
      hh_flt *=2
      
    # MERGE
    #ste = Events.SetTempoEvent(tick=0.0, data=[10, 197, 90])
    ste = Events.SetTempoEvent(tick=0.0, bpm=85)
    tse = Events.TimeSignatureEvent(tick=0.0, data=[4, 2, 24, 8])
    track0 = Containers.Track(events=[ste,tse], relative=True)

    track0.relative = False
    k_flt.relative = False
    s_flt.relative = False
    hh_flt.relative = False
    combined = track0 + (k_flt + s_flt + hh_flt)*len4
    combined = Containers.Track(events=sorted(combined, key=lambda x: x.tick),
                            relative=False)
    combined.relative = True

    # Add the end of track event, append it to the track
    eot = Events.EndOfTrackEvent(tick=1)
    combined.append(eot)
    new_track = Containers.Track(events= [x for x in combined], relative=True)


    new_pattern = Containers.Pattern( tracks=[new_track], resolution=480, fmt=1, relative=True)
    #print(new_pattern)

    totLen = combined.length/480
    totLen = ceil(totLen)
    if  totLen == 32:  
        #os.mkdir('DrumDB')
        midiname = "DrumDB\\" + randomString() + ".mid"

        # Save the pattern to disk
        FileIO.write_midifile(midiname, new_pattern)
        print(midiname + " scritto")
    else:
        x -= 1

#bf = FileIO.read_midifile("bellofigo.mid") 
#bf.resolution=480
#print("bellofigo")
#print(bf)
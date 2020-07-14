import os, fnmatch
from random import randrange
from math import ceil, floor
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

def allunga(xFlt, times):
    if times>1:
        copy = xFlt.copy()
        xRel = copy.relative
        copy.relative = True

        ii = 1
        while(ii < times):
            xFlt.extend(xFlt.make_ticks_rel())

            ii += 1

        copy.relative = xRel
        return xFlt
    else:
        return xFlt

def realLen(traccia):
    copy = traccia.copy()
    copyRel = copy.relative
    copy.relative = False

    realLength = copy[-1].tick
    copy.relative = copyRel
    return realLength

def sistLen(traccia):
    xRel = traccia.relative
    traccia.relative = False
    traccia[-1].tick = 7680-1
    traccia.relative = xRel
    return traccia


# FIND FILES
kick_files = []
snare_files = []
hh_files = []
len4 = 4

kick_files = find( '*[Kick].mid', 'Drums')
snare_files = find( '*[?Snare].mid', 'Drums')
hh_files = find( '*[Hat].mid', 'Drums')

print(kick_files)
print(snare_files)
print(hh_files)

#os.mkdir('DrumsDB')
Nit = 100
count = 0
while ( count < Nit):
    # KICK
    maxLen = len(kick_files)
    i=randrange(0,maxLen)
    
    k_midi = FileIO.read_midifile(kick_files[i]) #returns a Pattern with the MIDI file information (resolution ecc...), based on documentation https://github.com/jameswenzel/mydy/blob/master/src/FileIO.py
    k_midi.resolution=480
    #print(kick_files[i])
    #nnn = os.path.basename(kick_files[i])

    #print(k_midi)

    k_track = k_midi[-1] #selecting the track (since it's only one, it will be always at index 0)k_track = k_track.make_ticks_abs()# Converting time from relative to an absolute measure

    k_flt=k_track.filter(lambda e: isinstance(e, (Events.NoteOnEvent, Events.NoteOffEvent)))# Selects only Note_On events, i'm discarding the note off

    c1 = 36
    for element in k_flt :
        current_note = element.data[0]
        if current_note != c1:
            element.data[0] = c1
    
    k_totLen = realLen(k_flt)

    # SNARE
    maxLen = len(snare_files)
    i=randrange(0,maxLen)
    #print(snare_files[i]) 
    nnn = os.path.basename(snare_files[i])
            
    s_midi = FileIO.read_midifile(snare_files[i]) #returns a Pattern with the MIDI file information (resolution ecc...), based on documentation https://github.com/jameswenzel/mydy/blob/master/src/FileIO.py
    s_midi.resolution=480

    s_track = s_midi[-1] #selecting the track (since it's only one, it will be always at index 0)

    s_flt=s_track.filter(lambda e: isinstance(e, (Events.NoteOnEvent, Events.NoteOffEvent)))# Selects only Note_On events, i'm discarding the note off

    d1 = 38
    for element in s_flt :
        current_note = element.data[0]
        if current_note != d1:
            element.data[0] = d1

    s_flt = sistLen(s_flt)
    s_totLen = realLen(s_flt)
    #print(s_totLen)

    # HH
    maxLen = len(hh_files)
    i=randrange(0,maxLen)
    #print(hh_files[i])
    hh_midi = FileIO.read_midifile(hh_files[i]) #returns a Pattern with the MIDI file information (resolution ecc...), based on documentation https://github.com/jameswenzel/mydy/blob/master/src/FileIO.py
    hh_midi.resolution=480

    hh_track = hh_midi[-1] #selecting the track
    # nnn = os.path.basename(hh_files[i])
    hh_flt=hh_track.filter(lambda e: isinstance(e, (Events.NoteOnEvent, Events.NoteOffEvent)))# Selects only Note_On events, i'm discarding the note off

    fd1 = 42
    for element in hh_flt :
        current_note = element.data[0]
        if current_note != fd1:
            element.data[0] = fd1

    hh_totLen = realLen(hh_flt)

    #PREMERGE
    kLen = ceil(k_flt.length/480) #in quarti
    sLen = ceil(s_flt.length/480)
    hLen = ceil(hh_flt.length/480)
    
    kMeas = kLen // 4 #quante battute
    sMeas = sLen // 4
    hMeas = hLen // 4
    totMeas = 32

    meas = (kMeas, sMeas, hMeas)
    maxMeas = max(meas)
    #print(meas)
    #print(floor(maxMeas / sMeas))

    k_flt.relative = True
    k_flt = Containers.Track(k_flt, relative=True)
    k_flt = allunga(k_flt, floor(maxMeas / kMeas))

    s_flt.relative = True
    s_flt = Containers.Track(s_flt, relative=True)
    s_flt = allunga(s_flt, floor(maxMeas / sMeas))

    hh_flt.relative = True
    hh_flt = Containers.Track(hh_flt, relative=True)
    hh_flt = allunga(hh_flt, floor(maxMeas / hMeas))

    # MERGE
    #ste = Events.SetTempoEvent(tick=0.0, data=[10, 197, 90])
    ste = Events.SetTempoEvent(tick=0.0, bpm=85)
    tse = Events.TimeSignatureEvent(tick=0.0, data=[4, 2, 24, 8])
    track0 = Containers.Track(events=[ste,tse], relative=True)

    track0.relative = False
    k_flt.relative = False
    s_flt.relative = False
    hh_flt.relative = False

    combtemp = (k_flt + s_flt + hh_flt)
    
    combined = track0 + (k_flt + s_flt + hh_flt)
    
    combined = Containers.Track(events=sorted(combined, key=lambda x: x.tick),
                            relative=False)
    eotTick =  combined[-1].tick % 7680
    #print(eotTick)
    combined.relative = True

    combtemp = Containers.Track(events=sorted(combtemp, key=lambda x: x.tick),
                            relative=False)
    combtemp.relative = True

    for ii in range(len4):
        combined.extend(combtemp)

    # Add the end of track event, append it to the track
    eot = Events.EndOfTrackEvent(tick=eotTick)
    combined.append(eot)
    new_track = Containers.Track(events= [x for x in combined], relative=True)


    new_pattern = Containers.Pattern( tracks=[new_track], resolution=480, fmt=1, relative=True)
    #print(new_pattern)

    # totLen = realLen(new_track)
    # totLen = totLen/(480)
    #print(totLen)
    totLen = 16
    if  totLen ==16:  #SISTEMARE LENGTH
        count += 1
        midiname = "DrumsDB\\" + randomString() + ".mid"
        # midiname = "DrumsDB\\" + nnn + ".mid"

        # Save the pattern to disk
        FileIO.write_midifile(midiname, new_pattern)
        print(midiname + " scritto")

print("Ho finito!")

#bf = FileIO.read_midifile("bellofigo.mid") 
#bf.resolution=480
#print("bellofigo")
#print(bf)
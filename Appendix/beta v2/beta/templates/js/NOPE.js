// - Create AudioContext
var AudioContextFunc = window.AudioContext || window.webkitAudioContext;
var audioContext = new AudioContextFunc();

// create player from WebAudioFontPlayer
var player=new WebAudioFontPlayer();

player.loader.decodeAfterLoading(audioContext, 'mySamples');

var songStart = 0;
var input = null;
var currentSongTime = 0;
var nextStepTime = 0;
var nextPositionTime = 0;
var loadedsong = null;
var mySong = null;

var bpm = 120;
var scaler = 1;

function go() {
    document.getElementById('tmr').innerHTML = 'starting...';
    try {
        startPlay(loadedsong);
        document.getElementById('tmr').innerHTML = 'playing...';
    } catch (expt) {
        document.getElementById('tmr').innerHTML = 'error ' + expt;
    }
}

var stepDuration = 44/1000;

function startPlay(song) {
    currentSongTime = 0;
    songStart = audioContext.currentTime;
    nextStepTime = audioContext.currentTime;
    // var stepDuration = 44 / 1000;
    //console.log(stepDuration)
    tick(song);
}

function tick(song) {
    //console.log(stepDuration)
    if (audioContext.currentTime > nextStepTime - stepDuration) {
        sendNotes(song, songStart, currentSongTime, currentSongTime + stepDuration, audioContext, input, player);
        currentSongTime = currentSongTime + stepDuration;
        nextStepTime = nextStepTime + stepDuration;
        if (currentSongTime > song.duration) {
            currentSongTime = currentSongTime - song.duration;
            sendNotes(song, songStart, 0, currentSongTime, audioContext, input, player);
            songStart = songStart + song.duration;
        }
    }
    if (nextPositionTime < audioContext.currentTime) {
        var o = document.getElementById('position');
        o.value = 100 * currentSongTime / song.duration;
        document.getElementById('tmr').innerHTML = '' + Math.round(100 * currentSongTime / song.duration) + '%';
        nextPositionTime = audioContext.currentTime + 3;
    }
    window.requestAnimationFrame(function (t) {
        tick(song);
    });
}

function sendNotes(song, songStart, start, end, audioContext, input, player) {
    for (var t = 0; t < song.tracks.length; t++) {
        var track = song.tracks[t];
        for (var i = 0; i < track.notes.length; i++) {
            if (track.notes[i].when / scaler >= start && track.notes[i].when / scaler < end) {
                var when = songStart + track.notes[i].when / scaler;
                var duration = track.notes[i].duration;
                if (duration > 3) {
                    duration = 3;
                }
                var instr = track.info.variable;
                var v = track.volume / 7;
                //player.queueWaveTable(audioContext, input, window[instr], when, track.notes[i].pitch, duration, v, track.notes[i].slides);
                player.queueWaveTable(audioContext, input, _drumsTrap_sf2_file, when, track.notes[i].pitch, duration, v, track.notes[i].slides);
            }
        }
    }

    // for (var b = 0; b < song.beats.length; b++) {
    //     var beat = song.beats[b];
    //     for (var i = 0; i < beat.notes.length; i++) {
    //         if (beat.notes[i].when >= start && beat.notes[i].when < end) {
    //             var when = songStart + beat.notes[i].when;
    //             var duration = 1.5;
    //             var instr = beat.info.variable;
    //             var v = beat.volume / 2;
    //             //player.queueWaveTable(audioContext, input, window[instr], when, beat.n, duration, v);
    //             console.log(beat.n)
    //             player.queueWaveTable(audioContext, input, _drumsTrap_sf2_file, when, beat.n, duration, v);
    //         }
    //     }
    // }
}

function startLoad(song) {
    console.log("start load");
    console.log(song);
    var AudioContextFunc = window.AudioContext || window.webkitAudioContext;
    audioContext = new AudioContextFunc();
    player = new WebAudioFontPlayer();
    input = audioContext.destination;

        // PER TRACKS
        for (var i = 0; i < song.tracks.length; i++) {
            var nn = player.loader.findInstrument(song.tracks[i].program);
            var info = player.loader.instrumentInfo(nn);
            song.tracks[i].info = info;
            song.tracks[i].id = nn;
            player.loader.startLoad(audioContext, info.url, info.variable);
        }
    
    //song.beats = song.tracks
    //song.tracks = null
    for (var i = 0; i < song.beats.length; i++) {
        var nn = player.loader.findDrum(song.beats[i].n);
        var info = player.loader.drumInfo(nn);
        song.beats[i].info = info;
        song.beats[i].id = nn;
        player.loader.startLoad(audioContext, info.url, info.variable);
    }
    player.loader.waitLoad(function () {
        console.log('buildControls');
        buildControls(song);
    });
}

document.getElementById("bpmSel").addEventListener('change', function(e){
    let bpmSelector = this.value;
    //stepDuration = (44 / 1000)*(bpm/10)
    scaler = bpmSelector/bpmActual;
} );

function buildControls(song) {
    audioContext.resume();

    console.log('Loaded');
    var pos = document.getElementById('position');
    pos.oninput = function (e) {
        if (loadedsong) {
            player.cancelQueue(audioContext);
            var next = song.duration * pos.value / 100;
            songStart = songStart - (next - currentSongTime);
            currentSongTime = next;
        }
    };
    // console.log('Tracks');
    // for (var i = 0; i < song.tracks.length; i++) {
    //     setVolumeAction(i, song);
    // }
    // console.log('Drums');
    // for (var i = 0; i < song.beats.length; i++) {
    //     setDrVolAction(i, song);
    // }
    loadedsong = song;
}

// function setVolumeAction(i, song) {
//     var vlm = document.getElementById('channel' + i);
//     vlm.oninput = function (e) {
//         player.cancelQueue(audioContext);
//         var v = vlm.value / 100;
//         if (v < 0.000001) {
//             v = 0.000001;
//         }
//         song.tracks[i].volume = v;
//     };
//     var sl = document.getElementById('selins' + i);
//     sl.onchange = function (e) {
//         var nn = sl.value;
//         var info = player.loader.instrumentInfo(nn);
//         player.loader.startLoad(audioContext, info.url, info.variable);
//         player.loader.waitLoad(function () {
//             console.log('loaded');
//             song.tracks[i].info = info;
//             song.tracks[i].id = nn;
//         });
//     };
// }

// function setDrVolAction(i, song) {
//     var vlm = document.getElementById('drum' + i);
//     vlm.oninput = function (e) {
//         player.cancelQueue(audioContext);
//         var v = vlm.value / 100;
//         if (v < 0.000001) {
//             v = 0.000001;
//         }
//         song.beats[i].volume = v;
//     };
//     var sl = document.getElementById('seldrm' + i);
//     sl.onchange = function (e) {
//         var nn = sl.value;
//         var info = player.loader.drumInfo(nn);
//         player.loader.startLoad(audioContext, info.url, info.variable);
//         player.loader.waitLoad(function () {
//             console.log('loaded');
//             song.beats[i].info = info;
//             song.beats[i].id = nn;
//         });
//     };
// }

// function chooserIns(n, track) {
//     var html = '<select id="selins' + track + '">';
//     for (var i = 0; i < player.loader.instrumentKeys().length; i++) {
//         var sel = '';
//         if (i == n) {
//             sel = ' selected';
//         }
//         html = html + '<option value="' + i + '"' + sel + '>' + i + ': ' + player.loader.instrumentInfo(i).title + '</option>';
//     }
//     html = html + '</select>';
//     return html;
// }

// function chooserDrum(n, beat) {
//     var html = '<select id="seldrm' + beat + '">';
//     for (var i = 0; i < player.loader.drumKeys().length; i++) {
//         var sel = '';
//         if (i == n) {
//             sel = ' selected';
//         }
//         html = html + '<option value="' + i + '"' + sel + '>' + i + ': ' + player.loader.drumInfo(i).title + '</option>';
//     }
//     html = html + '</select>';
//     return html;
// }

function handleFileSelect(event) {
    console.log(event);
    var file = event.target.files[0];
    console.log(file);
    var fileReader = new FileReader();
    fileReader.onload = function (progressEvent) {
        console.log(progressEvent);
        var arrayBuffer = progressEvent.target.result;
        console.log(arrayBuffer);
        var midiFile = new MIDIFile(arrayBuffer);
        var song = midiFile.parseSong();
        mf = midiFile
        mySong = song
        startLoad(song);
        console.log("song.tracks")
        console.log(song.tracks)
        console.log("song.beats")
        console.log(song.beats)
        document.getElementById("bpmSel").value = Math.trunc(bpmActual)
    };
    fileReader.readAsArrayBuffer(file);
}

function handleExample(path) {
    console.log("Handle midi file");
    console.log(path);
    var xmlHttpRequest = new XMLHttpRequest();
    xmlHttpRequest.open("GET", path, true);
    xmlHttpRequest.responseType = "arraybuffer";
    xmlHttpRequest.onload = function (e) {
        var arrayBuffer = xmlHttpRequest.response;
        var midiFile = new MIDIFile(arrayBuffer);
        var song = midiFile.parseSong();
        mf = midiFile
        mySong = song
        startLoad(song);
        document.getElementById("bpmSel").value = Math.trunc(bpmActual)
    };
    xmlHttpRequest.send(null);
}

var midi_path

function genMidi() {
    midi_path = midiurl
    console.log(midi_path);
    //document.getElementById("cntls").innerHTML = "genMidi"
    handleExample(midi_path)
}

// var bpm = document.getElementById("bpm")
// var ti = 60/bpm.value

// bpm.onchange = function(){
//     ti = 60/bpm.value
//     myWave.params.plugins[0].params.timeInterval = timeInterval()
//     myWave.timeline.render()
// }

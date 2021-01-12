'use strict';
var myWave;
var input = document.getElementById("input")
// Create an instance

var bla = 123;
var bpm = document.getElementById("bpm")
var ti = 60/bpm.value

bpm.onchange = function(){
    ti = 60/bpm.value
    myWave.params.plugins[0].params.timeInterval = timeInterval()
    myWave.timeline.render()
}

document.addEventListener('DOMContentLoaded', function() {
    myWave = WaveSurfer.create({
        container: '#waveform',
        waveColor: 'violet',
        progressColor: 'purple',
        loaderColor: 'purple',
        cursorColor: 'navy',
        plugins: [
            WaveSurfer.timeline.create({
                container: '#wave-timeline',
                formatTimeCallback: formatTimeCallback,
                timeInterval: timeInterval,
                primaryLabelInterval: primaryLabelInterval,
                secondaryLabelInterval: secondaryLabelInterval,
                primaryColor: 'blue',
                secondaryColor: 'red',
                primaryFontColor: 'blue',
                secondaryFontColor: 'red'
            })
        ]
    })
});


input.onchange = function(e){
  console.log("...")
  let src = URL.createObjectURL(this.files[0]);
  myWave.load(src);
  console.log("Carricato")
}

var pp = document.getElementById("playpause")

pp.onclick = function(e){
    myWave.playPause();
}

// TIMELINE OVERRIDE
/**
 * Use formatTimeCallback to style the notch labels as you wish, such
 * as with more detail as the number of pixels per second increases.
 *
 * Here we format as M:SS.frac, with M suppressed for times < 1 minute,
 * and frac having 0, 1, or 2 digits as the zoom increases.
 *
 * Note that if you override the default function, you'll almost
 * certainly want to override timeInterval, primaryLabelInterval and/or
 * secondaryLabelInterval so they all work together.
 *
 * @param: seconds
 * @param: pxPerSec
 */
function formatTimeCallback(seconds, pxPerSec) {
  seconds = Number(seconds);
  var minutes = Math.floor(seconds / 60);
  seconds = seconds % 60;

  // fill up seconds with zeroes
  var secondsStr = Math.round(seconds).toString();
  if (pxPerSec >= 25 * 10) {
      secondsStr = seconds.toFixed(2);
  } else if (pxPerSec >= 25 * 1) {
      secondsStr = seconds.toFixed(1);
  }

  if (minutes > 0) {
      if (seconds < 10) {
          secondsStr = '0' + secondsStr;
      }
      return `${minutes}:${secondsStr}`;
  }
  return secondsStr;
}

/**
* Use timeInterval to set the period between notches, in seconds,
* adding notches as the number of pixels per second increases.
*
* Note that if you override the default function, you'll almost
* certainly want to override formatTimeCallback, primaryLabelInterval
* and/or secondaryLabelInterval so they all work together.
*
* @param: pxPerSec
*/
function timeInterval(pxPerSec) {
  var retval = 1;
  if (pxPerSec >= 25 * 100) {
      retval = 0.01;
  } else if (pxPerSec >= 25 * 40) {
      retval = 0.025;
  } else if (pxPerSec >= 25 * 10) {
      retval = 0.1;
  } else if (pxPerSec >= 25 * 4) {
      retval = 0.25;
  } else if (pxPerSec >= 25) {
      retval = 1;
  } else if (pxPerSec * 5 >= 25) {
      retval = 5;
  } else if (pxPerSec * 15 >= 25) {
      retval = 15;
  } else {
      retval = Math.ceil(ti * 0.5 / pxPerSec) * 60;
  }
  return retval;
}

/**
* Return the cadence of notches that get labels in the primary color.
* EG, return 2 if every 2nd notch should be labeled,
* return 10 if every 10th notch should be labeled, etc.
*
* Note that if you override the default function, you'll almost
* certainly want to override formatTimeCallback, primaryLabelInterval
* and/or secondaryLabelInterval so they all work together.
*
* @param pxPerSec
*/
function primaryLabelInterval(pxPerSec) {
  var retval = 1;
  if (pxPerSec >= 25 * 100) {
      retval = 10;
  } else if (pxPerSec >= 25 * 40) {
      retval = 4;
  } else if (pxPerSec >= 25 * 10) {
      retval = 10;
  } else if (pxPerSec >= 25 * 4) {
      retval = 4;
  } else if (pxPerSec >= 25) {
      retval = 1;
  } else if (pxPerSec * 5 >= 25) {
      retval = 5;
  } else if (pxPerSec * 15 >= 25) {
      retval = 15;
  } else {
      retval = Math.ceil(0.5 / pxPerSec) * 60;
  }
  return retval;
}

/**
* Return the cadence of notches to get labels in the secondary color.
* EG, return 2 if every 2nd notch should be labeled,
* return 10 if every 10th notch should be labeled, etc.
*
* Secondary labels are drawn after primary labels, so if
* you want to have labels every 10 seconds and another color labels
* every 60 seconds, the 60 second labels should be the secondaries.
*
* Note that if you override the default function, you'll almost
* certainly want to override formatTimeCallback, primaryLabelInterval
* and/or secondaryLabelInterval so they all work together.
*
* @param pxPerSec
*/
function secondaryLabelInterval(pxPerSec) {
  // draw one every 10s as an example
  return Math.floor(10 / timeInterval(pxPerSec));
}


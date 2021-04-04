// Instruments
//

//const { ToneEvent } = require("tone");

// Instrument 1
//  let drumPlayers = new Tone.Players({
//   kick : 'https://teropa.info/ext-assets/drumkit/kick.mp3',
//   hatClosed : 'https://teropa.info/ext-assets/drumkit/hatClosed.mp3',
//   hatOpen : 'https://teropa.info/ext-assets/drumkit/hatOpen2.mp3',
//   snare : 'https://teropa.info/ext-assets/drumkit/snare3.mp3',
//   tomLow : 'https://teropa.info/ext-assets/drumkit/tomLow.mp3',
//   tomMid : 'https://teropa.info/ext-assets/drumkit/tomMid.mp3',
//   tomHigh : 'https://teropa.info/ext-assets/drumkit/tomHigh.mp3',
//   ride : 'https://teropa.info/ext-assets/drumkit/ride.mp3',
//   crash : 'https://teropa.info/ext-assets/drumkit/hatOpen.mp3'
// }).toDestination()

//
// Instrument 2

// let bass = new Tone.Synth({
//   oscillator:{type:'sawtooth'},
//   volume: -4
// })

// let bassFilter = new Tone.Filter({type:'lowpass', frequency:2000})

// bass.connect(bassFilter);
// bassFilter.toDestination();

//
// Instrument 3

// let audio = new Audio('Assets/127155__daphne-in-wonderland__celtic-harp-c2.wav');

// let leadSampler = new Tone.Sampler({
//   urls: {
//     'C2': 'Assets/127155__daphne-in-wonderland__celtic-harp-c2.wav'
//   },
//   volume: -4
// })

// let leadDelay = new Tone.PingPongDelay('8n',0.3)
// leadSampler.connect(leadDelay);
// leadDelay.toDestination();

// let leadReverb = new Tone.Reverb({decay: 3, wet: 0.5}).toDestination()
// leadSampler.connect(leadReverb);

//
// ________Patterns__________

//  1.Drum Part
//  let drumPattern = [
//   ['0:0:0','kick'],
//   ['0:1:0','hatClosed'],
//   ['0:1:2','kick'],
//   ['0:2:0','kick'],
//   ['0:3:0','hatClosed'],
//   ['1:0:0','kick'],
//   ['1:1:0','hatClosed'],
//   ['1:2:0','kick'],
//   ['1:2:3','kick'],
//   ['1:3:0','hatClosed'],
//   ['1:3:2','kick'],
//   ['1:3:2','hatOpen'],
// ];

// let drumPart = new Tone.Part((time, drum)=>{
//     drumPlayers.player(drum).start(time);
//   }, drumPattern ).start();

//   drumPart.loop = true;
//   drumPart.loopStart = 0;
//   drumPart.loopEnd = '2m';



// 2. Bass Part

// let bassPattern = [
//   ['0:0:0', 'C#2'],
//   ['0:0:3', 'C#2'],
//   ['0:1:2', 'E1']

// ];

// let bassPart = new Tone.Part((time,note) =>{
//   bass.triggerAttackRelease(note,0.1,time);
//  },bassPattern).start();

//   bassPart.loop = true;
//   bassPart.loopStart = 0;
//   bassPart.loopEnd ='2n';



// 3. Lead Part


//  let leadPattern = [
// ];

//  let leadPart = new Tone.Part((time,note) => {
//   leadSampler.triggerAttackRelease(note,'2n',time);
//  },leadPattern).start();

//   leadPart.loop = true;
//   leadPart.loopStart = 0;
//   leadPart.loopEnd ='2m';


//
// Interaction
//let playing = false
/*document.getElementById("start").onclick = async () => {
  if (playing) {
    document.getElementById("start").innerHTML = "Start"
    await Tone.start();
    Tone.Transport.stop();
  } else {
    document.getElementById("start").innerHTML = "Stop"
    await Tone.start();
    Tone.Transport.start();
  }
  playing = !playing;
}

document.getElementById("bpm").onclick = (evt) =>{
  let newBpm = +evt.target.value;
  Tone.Transport.bpm.value = newBpm;
}

let sequencer = new Nexus.Sequencer('#sequencer',{
  columns: 32,
  rows: 12,
  size: [550,200]
})

new Tone.Loop((time) => {
  Tone.Draw.schedule( () => sequencer.next(),time);
 },'16n').start();

let sequencerRows = ['B3', 'G#3', 'E3', 'C#2', 'B2', 'G#2', 'E2', 'C#2', 'B1', 'G#1', 'E1', 'C#1'];

sequencer.on('change', ({column, row, state})=> {
  let time = {'16n': column};
  let note = sequencerRows[row];
  console.log((time,note));
  if (state){
    leadPart.add(time, note)
  } else{
    leadPart.remove(time, note)
  }
})
*/
// document.getElementById('bass').onclick  = () => {
//   bass.triggerAttackRelease('C#2',0.1)
// }

//---------------------------------------------------------------------------------------------------------------
// Generate Button
//
// Sends post request to server: model parameters
//---------------------------------------------------------------------------------------------------------------

var isClicked = false;
function highlight() {
    var lstm = document.getElementById('lstm');
    var transformer = document.getElementById('transformer');
    if (isClicked == true) {
        lstm.className = "model-unselect"
        transformer.className = "model-select"
    }
    else {
        lstm.className = "model-select"
        transformer.className = "model-unselect"
    }

    isClicked = !isClicked

}

document.getElementById("custom-slider").addEventListener("input", function(event){
    let value = event.target.value;
    document.getElementById("current-value").innerText= value;
    document.getElementById("current-value").classList.add("active") 
    document.getElementById("current-value").style.left = `${((value-0.7)/0.6 * 80) - 17*(value-0.7)}%`;
  })
  
  document.getElementById("custom-slider").addEventListener("blur", function(event){
    document.getElementById("current-value").classList.remove("active") 
  })

async function save_param() {

    //Add a span class for the spinner object
    // document.getElementById('generate').innerHTML += "<span id='generateSpinner' class='spinner-border spinner-border-sm model-select'   role='status' aria-hidden='true'  ></span>"
    document.getElementById('generate').className = "gen-btn-press"
    document.getElementById('generate').innerHTML = " <div class='pulse-bubble pulse-bubble-1' ></div> " +
        "<div class='pulse-bubble pulse-bubble-2'></div>" +
        "<div class='pulse-bubble pulse-bubble-3'></div>"

    var temp = document.getElementById('custom-slider').value;
    var timsig_n = document.getElementById('time-sig-num').value;
    var timsig_d = document.getElementById('time-sig-den').value;
    var numOfBars = document.getElementById('numOfBars').value;
    var valence = document.getElementById('valence').value;
    var density = document.getElementById('density').value;
    var model = (isClicked == true) ? 'lstm' : 'transformer';

    var par = {
        temp: temp,
        timsig_n: timsig_n,
        timsig_d: timsig_d,
        numOfBars: numOfBars,
        valence: valence,
        density: density,
        model: model,
    }

    var options = {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(par)
    };

    var response = await fetch('/api', options);
    var data = await response.json();
    console.log(data.message)
    var osmd = document.getElementById('osmdContainer');
    osmd.innerHTML = " "
    document.getElementById('generate').className = "gen-btn"
    document.getElementById('generate').innerHTML = "Generate"
    if (data.code) {
        var osmd = document.getElementById('osmdContainer');
        osmd.innerHTML = '<h3>  Something has gone horribly wrong somewhere </h3>'  +
                            '<h3><span> \\(o ~ 0)/ </span></h3>' 
    }
    else {
        display_sheet_music()
    }

}

function display_sheet_music() {

    // Fetch musicXML Container
    var osmd = new opensheetmusicdisplay.OpenSheetMusicDisplay("osmdContainer");

    osmd.setOptions({
        backend: "svg",
        drawTitle: false,
        drawComposer: false,
        drawPartNames: true,
        renderSingleHorizontalStaffline: false
    });

    osmd
        .load("http://localhost:3000/sheet")
        .then(
            function () {
                window.osmd = osmd; //give access to osmd object in Browser console, e.g. for osmd.setOptions()
                osmd.render();
            });

}


//---------------------------------------------------------------------------------------------------------------
// Play Button 
//
// Sends get request to server to play the generated file.
// File is received as a ToneJS readable-JSON object.
// and upload
//---------------------------------------------------------------------------------------------------------------

async function play_file() {

    document.getElementById('play').className = "play-btn-press"
    document.getElementById('pause-left').style.display = "inline-block"
    document.getElementById('pause-right').style.display = "inline-block"
    //Add a span class for the spinner object
    //document.getElementById('play').innerHTML += "<span id ='playSpinner' class='spinner-border spinner-border-sm'   role='status' aria-hidden='true'  ></span>"

    //Fetch musicJSON
    var response = await fetch('/api');
    var data = await response.json();

    //  Change the instruments from bass-electric/bassoon/cello/clarinet/contrabass/flute/french-horn/guitar-acoustic
    //guitar-electric/guitar-nylon/harmonium/harp/organ/piano/saxophone/trombone/trumpet/tuba/violin/xylophone/
    // data.tracks[0].name = "bass-electric"
    // data.tracks[1].name = "harp"

    // Play musicJSON with tone
    var instruments = [];
    if (data) {
        const now = Tone.now() + 0.5;
        data.tracks.forEach((track) => {
            //get instrument from sample library -- courtsey of  nbrosowsky/tonejs-instruments 
            var instrument = SampleLibrary.load({
                instruments: track.name.toLowerCase(),
                baseUrl: "http://localhost:8080/",
                ext: ".[wav|mp3|ogg]"
            });
            instrument.toDestination()
            instruments.push(instrument)
            //schedule all of the events
            track.notes.forEach((note) => {
                // play instrument sound
                Tone.loaded().then(() => instrument.triggerAttackRelease(
                    note.name,
                    note.duration,
                    note.time + now,
                    note.velocity)
                )
            });

        });
    } else {
        //dispose the instrument and make a new one
        while (instruments.length) {
            const instrument = instruments.shift();
            instrument.disconnect();

        }
    }


    document.getElementById('play').className = "play-btn"
    document.getElementById('pause-left').style.display = "none"
    document.getElementById('pause-right').style.display = "none"

}

// Get the modal
var modal = document.getElementById("info");

// Get the button that opens the modal
var btn = document.getElementById("info-btn");

// Get the <span> element that closes the modal
var span = document.getElementsByClassName("close")[0];

// When the user clicks the button, open the modal 
btn.onclick = function () {
    modal.style.display = "block";
}

// When the user clicks on <span> (x), close the modal
span.onclick = function () {
    modal.style.display = "none";
}

// When the user clicks anywhere outside of the modal, close it
window.onclick = function (event) {
    if (event.target == modal) {
        modal.style.display = "none";
    }
}

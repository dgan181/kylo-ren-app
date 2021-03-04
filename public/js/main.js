 // Instruments
 //
 // Instrument 1
 let drumPlayers = new Tone.Players({
  kick : 'https://teropa.info/ext-assets/drumkit/kick.mp3',
  hatClosed : 'https://teropa.info/ext-assets/drumkit/hatClosed.mp3',
  hatOpen : 'https://teropa.info/ext-assets/drumkit/hatOpen2.mp3',
  snare : 'https://teropa.info/ext-assets/drumkit/snare3.mp3',
  tomLow : 'https://teropa.info/ext-assets/drumkit/tomLow.mp3',
  tomMid : 'https://teropa.info/ext-assets/drumkit/tomMid.mp3',
  tomHigh : 'https://teropa.info/ext-assets/drumkit/tomHigh.mp3',
  ride : 'https://teropa.info/ext-assets/drumkit/ride.mp3',
  crash : 'https://teropa.info/ext-assets/drumkit/hatOpen.mp3'
}).toDestination()

 //
 // Instrument 2

let bass = new Tone.Synth({
  oscillator:{type:'sawtooth'},
  volume: -4
})

let bassFilter = new Tone.Filter({type:'lowpass', frequency:2000})

bass.connect(bassFilter);
bassFilter.toDestination();

//
// Instrument 3

let audio = new Audio('Assets/127155__daphne-in-wonderland__celtic-harp-c2.wav');

let leadSampler = new Tone.Sampler({
  urls: {
    'C2': 'Assets/127155__daphne-in-wonderland__celtic-harp-c2.wav'
  },
  volume: -4
})

let leadDelay = new Tone.PingPongDelay('8n',0.3)
leadSampler.connect(leadDelay);
leadDelay.toDestination();

let leadReverb = new Tone.Reverb({decay: 3, wet: 0.5}).toDestination()
leadSampler.connect(leadReverb);

//
// ________Patterns__________

//  1.Drum Part
 let drumPattern = [
  ['0:0:0','kick'],
  ['0:1:0','hatClosed'],
  ['0:1:2','kick'],
  ['0:2:0','kick'],
  ['0:3:0','hatClosed'],
  ['1:0:0','kick'],
  ['1:1:0','hatClosed'],
  ['1:2:0','kick'],
  ['1:2:3','kick'],
  ['1:3:0','hatClosed'],
  ['1:3:2','kick'],
  ['1:3:2','hatOpen'],
];

let drumPart = new Tone.Part((time, drum)=>{
    drumPlayers.player(drum).start(time);
  }, drumPattern ).start();

  drumPart.loop = true;
  drumPart.loopStart = 0;
  drumPart.loopEnd = '2m';



// 2. Bass Part

let bassPattern = [
  ['0:0:0', 'C#2'],
  ['0:0:3', 'C#2'],
  ['0:1:2', 'E1']

];

let bassPart = new Tone.Part((time,note) =>{
  bass.triggerAttackRelease(note,0.1,time);
 },bassPattern).start();

  bassPart.loop = true;
  bassPart.loopStart = 0;
  bassPart.loopEnd ='2n';



// 3. Lead Part


 let leadPattern = [
];

 let leadPart = new Tone.Part((time,note) => {
  leadSampler.triggerAttackRelease(note,'2n',time);
 },leadPattern).start();

  leadPart.loop = true;
  leadPart.loopStart = 0;
  leadPart.loopEnd ='2m';


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

async function save_param(){
  var temp = document.getElementById('temp').value;
  var timsig_n = document.getElementById('time-sig-num').value;
  var timsig_d = document.getElementById('time-sig-den').value;
  var numOfBars = document.getElementById('numOfBars').value;
  var valence = document.getElementById('valence').value;

  var par = {
    temp: temp,
    timsig_n: timsig_n,
    timsig_d: timsig_d,
    numOfBars: numOfBars,
    valence: valence,

  }

  var options = {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json'
    },
    body: JSON.stringify(par)
  };

  var param_p = document.getElementById('param_p');
  param_p.innerHTML = '<p> <h3> File generating... </h3h></p>'
  var response = await fetch('/api', options);
  var data = await response.text();
  param_p.innerHTML = '<p> <h3>' + data + '</h3h></p>' +
                     '<p> The following parameters were sent: </p>'

  window.localStorage.setItem('param',JSON.stringify(par));
  fetch_param();
}

function fetch_param(){
  var param = JSON.parse(window.localStorage.getItem('param'));
  var param_p = document.getElementById('param_p');

  param_p.innerHTML += '<p> Temp: ' + param.temp + '</p>' +
                      '<p> Time Signature: ' + param.timsig_n + '<span> &#47;</span> ' + param.timsig_d + '</p>' +
                      '<p> Number of Bars: ' + param.numOfBars + '</p>' +
                      '<p> Valence: ' + param.valence + '</p>'
  }


//---------------------------------------------------------------------------------------------------------------
// Play Button 
//
// Sends get request to server to play the generated file.
// File is received as a ToneJS readable-JSON object.
//---------------------------------------------------------------------------------------------------------------

async function play_file(){

  var response = await fetch('/api');
  var data = await response.json();

  var param_p = document.getElementById('param_p');

  param_p.innerHTML += '<p>' + 'playing file...' + '</p>'
  //console.log(JSON.stringify(data))

  const instruments = [];
    if (data) {
        const now = Tone.now() + 0.5;
        data.tracks.forEach((track) => {
            //create a synth for each track
            const synth = new Tone.PolySynth(Tone.Synth, {
               envelope: {
                  attack: 0.02,
                   decay: 0.1,
                   sustain: 0.3,
                   release: 1,
               },
            }).toDestination();

            //const synth = new Tone.Synth();
            //synth.oscillator.type = "sine";
            //synth.toDestination();
            instruments.push(synth)
            //schedule all of the events
            track.notes.forEach((note) => {
                synth.triggerAttackRelease(
                    note.name,
                    note.duration,
                    note.time + now,
                    note.velocity
                );
            });
        });
    } else {
        //dispose the synth and make a new one
        while (instruments.length) {
            const synth = instruments.shift();
            synth.disconnect();
        }
    }

  }

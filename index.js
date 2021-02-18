const express = require('express');
const app = express();
const fs = require('fs');
const {spawn} = require('child_process');
const port = 3000;
const { Midi } = require('@tonejs/midi')

app.listen(port, (err) =>{
    if(!err)
    console.log('server started running on:' + port);
    else
    console.log('unable to start server');
})

app.use(express.static('public'));
app.use(express.json());


//---------------------------------------------------------------------------------------------------------------
// Post Request:
//
// Receives file parameters and runs python script to excute model
//---------------------------------------------------------------------------------------------------------------

app.post('/api', (request,response) => {

  var filestuff;
  console.log("I got the generate request!")
  //  Deal with the request
  const param = request.body;
  const python = spawn('python',['script1.py', param.temp, param.timsig_n, param.timsig_d , param.numOfBars , param.valence ]);
  // Testing
   python.stdout.on('data', (data) => {
     console.log('from file...');
     filestuff = data.toString();
     console.log(filestuff);
     console.log(data.toString());
   });

  python.on('close', (code) => {
    console.log(`child process close all stdio with code ${code}`);
    // send data to browser
    response.send("File generated!");
  });
});

//---------------------------------------------------------------------------------------------------------------
// Get Request:
//
// Converts midi data file to Tonejs readable-JSON and sends it to the client
//---------------------------------------------------------------------------------------------------------------

app.get('/api', (request,response) => {

  console.log("I got the play request!")
  const midiData = fs.readFileSync("./Backend/seq2seq_test/generations/music.mid")
  const midi = new Midi(midiData)
  response.json(midi)
});

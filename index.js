const express = require('express');
const app = express();
const fs = require('fs');
const {spawn} = require('child_process');
const port = 3000;
const { Midi } = require('@tonejs/midi')
const __model_dirname = "./Backend/forDeploy"

// Function to convert an Uint8Array to a string
var uint8arrayToString = function(data){
  return String.fromCharCode.apply(null, data);
};

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
  
  const options = {
    cwd: __model_dirname
  }
  const param = request.body
  const python = spawn('python',['./gen_full.py', param.temp, param.timsig_n, param.timsig_d , param.numOfBars , param.valence, param.density, param.model ], options);
  // Testing
  python.stdout.on('data', (data) => {
    console.log('from file...');
    filestuff = data.toString();
    console.log(filestuff);
    console.log(data.toString());
  });

    // Handle error output
  python.stderr.on('data', (data) => {
    // As said before, convert the Uint8Array to a readable string.
    console.log(uint8arrayToString(data));
  });

    // Handle error output
  python.stderr.on('data', (data) => {
    // As said before, convert the Uint8Array to a readable string.
    console.log(uint8arrayToString(data));
  });
  
  python.on('close', (code) => {
    console.log(`child process close all stdio with code ${code}`);
    // send data to browser
    var message
    if(code == 0){ 
    message = "File generated!" }
    else{ 
      message = "Error in generating file"}
    const response_message = {
      message: message,
      code: code
    }
    response.json(response_message)
  });
});

//---------------------------------------------------------------------------------------------------------------
// Get Request:
//
// Converts midi data file to Tonejs readable-JSON and sends it to the client
//---------------------------------------------------------------------------------------------------------------

app.get('/api', (request,response) => {

  console.log("I got the play request!")
  
  const midiData = fs.readFileSync(__model_dirname+"/midi/music.mid")
  const midi = new Midi(midiData)
  response.json(midi)
});

//---------------------------------------------------------------------------------------------------------------
// Get Request:
//
// Sends musicXML to client for sheet music
//---------------------------------------------------------------------------------------------------------------


app.get('/sheet', (request,response) => {
  console.log("Sending sheet music")
  response.set('Content-Type', 'text/xml');
  const xmlData = fs.readFileSync(__model_dirname+"/musicxml/sheet.xml")
  response.send(xmlData)
});

//---------------------------------------------------------------------------------------------------------------
// Get Request:
//
// Sends musicXML to client for sheet music
//---------------------------------------------------------------------------------------------------------------


app.get('/sheet', (request,response) => {
  console.log("Sending sheet music")
  response.set('Content-Type', 'text/xml');
  const xmlData = fs.readFileSync(__model_dirname+"/musicxml/sheet.xml")
  response.send(xmlData)
});

const express = require('express');
const app = express();
const fs = require('fs');
const {spawn} = require('child_process');
const port = 3000;

app.listen(port, (err) =>{
    if(!err)
    console.log('server started running on:' + port);
    else
    console.log('unable to start server');
})

app.use(express.static('public'));
app.use(express.json());

app.post('/api', (request,response) => {
  var filestuff;
  console.log("I got a request!")
  console.log(request.body);
  const param = request.body;
  const python = spawn('python',['script1.py', param.temp, param.timsig_n, param.timsig_d, param.numOfBars, param.valence]);
  python.stdout.on('data', function (data) {
    console.log('from file...');
    filestuff = data.toString();
    console.log(filestuff);
  });

  python.on('close', (code) => {
    console.log(`child process close all stdio with code ${code}`);
    // send data to browser
  });
  response.send("File generated!");

});


app.get('/api', (request,response) => {
  fs.readFile('gen.txt', 'utf8', (err, data) => {
    if (err){
      console.log(err)
      } else {
      console.log("file reading or playing");
      response.send(data.toString());
      }

  });
  //response.writeHead(200, {'Content-Type': 'video/mp4'});
  //let opStream = fs.createReadStream('/home/Downloads/me_at_the_zoo.mp4');

  //res.writeHead(200, {'Content-Type': 'audio/mp3'});
  //let opStream = fs.createReadStream('/home/Downloads/attention_instrument.mp3');

  //opStream.pipe(response);
});

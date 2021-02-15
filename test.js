const express = require('express');
const app = express();
const fs = require('fs');
const process = require('process');
const {spawn} = require('child_process');
var path = require('path');

//console.log(process.cwd())
project_path = process.cwd()
//{cwd:'E:\\GitHub\\KyloRen27\\kylo\\Backend\\seq2seq_test\\'}
//'{process.cwd()}\\generate_v0.1.py'

const defaults = {
  cwd: 'C:\\Users\\Anirudh\\Anaconda3\\envs\\Music21',
  env: process.env,
  shell: true
};

const ls = spawn('python', ['script1.py','0.9', '[4,4]', '16', '2']);

ls.stdout.on('data', (data) => {
  console.log(`stdout: ${data}`);
});

ls.stderr.on('data', (data) => {
  console.error(`stderr: ${data}`);
});

ls.on('close', (code) => {
  console.log(`child process exited with code ${code}`);
});
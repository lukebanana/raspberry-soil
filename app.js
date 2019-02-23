var msg = 'Starting...';
console.log(msg);

fs = require('fs');
var async = require('async');
var sht10 = require('./js/SHT1x')

datapath = '/home/pi/sensor-data';
filename = 'data.csv';
HEADERLINE = 'Time Temperature Humidity Dewpoint\n';
dataline = '';
/*
//read sensor data
async.series([
    sht10.init,
    sht10.reset,
    function (callback) {
        sht10.getSensorValues(function (error, values) {
            dataline = dataline + Math.floor(Date.now() / 1000); //Timestamp from milliseconds to seconds.
            dataline = dataline + '\t' + values.temperature + '\t' + values.humidity + '\t' + values.dewpoint + '\n';
            writesensordata();
            callback(error);
        });
    }
], function (error) {
    sht10.shutdown();
    if (error) {
        console.error(error);
    }
});
*/

var SHT1x = require('pi-sht1x');

async.series([
  SHT1x.init,
  SHT1x.reset,
  function(callback) {
    SHT1x.getSensorValues(function(error, values) {
      console.log(values);
      callback(error);
    });
  }
], function(error) {
  SHT1x.shutdown();
  if (error) {
    console.error(error);
  }
});

function writesensordata(callback) {
    //Write sensor data to given file
    fs.access(datapath + '/' + filename, fs.F_OK, function (err) {
        if (err) {
            var datafile = fs.appendFile(datapath + '/' + filename, HEADERLINE, (err) => {
                if (err) throw err;
                else console.log('A new data file was created with headers.');
            });
        }

        var datafile = fs.appendFile(datapath + '/' + filename, dataline, (err) => {
            if (err) throw err;
            console.log('New sensor data was appended to ' + filename + ' file.');
        });
    });
}
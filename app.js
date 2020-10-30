var msg = 'Starting...';
console.log(msg);

fs = require('fs');

datapath = '/home/pi/sensor-data';
filename = 'data.csv';
HEADERLINE = 'Time Temperature Humidity Dewpoint\n';
dataline = '';

var async = require('async');

var SHT1x = require('./js/SHT1x');


async.series([
  SHT1x.init,
  SHT1x.reset,
  function(callback) {
    SHT1x.getSensorValues(function(error, values) {
        console.log("ok");
      console.log(values);
      callback(error);
    });
  }
], function(error) {
  SHT1x.shutdown();
       console.log("nok");
  if (error) {
    console.error(error);
  }
});
/*
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
*/

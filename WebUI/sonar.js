// Palermo server startup
var http = require('http');
var router = require('./router');
var connect = require('connect');
var experimental = require('./experimental');

var PORT = 8080;

var thrift = require('thrift');
var managementService = require('./ManagementService');
var types = require("./collector_types");

function plain(req, resp) {
    resp.end("hello world");
}

function tsdbHandler(req, resp) {
    var connection = thrift.createConnection('localhost', 7932);
    client = thrift.createClient(managementService, connection);

    connection.on("error", function (err) {
        console.log("Could not connect with the Collector: " + err);
    });

    var time = Math.round(new Date().getTime() / 1000);
    console.log("time: " + time);

    var query = new types.TimeSeriesQuery({
        startTime:0,
        stopTime:time,
        hostname:"jack",
        sensor:"TEST"
    });

    client.query(query, function (err, result) {

            console.log("result received");
            console.log("length: " + result.length);

            var jsonObj = []; //declare array

            for (i in result) {
                console.log("value " + result[i].value);

                var time = result[i].timestamp;
                var value = result[i].value;

                jsonObj.push([time,value]);
            }


            var ss = JSON.stringify(jsonObj);
            console.log(ss);
            resp.end(ss);
        }
    )
    ;

    /*
     client.getLabels("srv2", function (err, result) {
     console.log("received a result");
     for (i in result) {
     console.log(result[i]);
     }
     }); */

// console.log("done");

// Send the data in a json formatted string
}

// configure urls
var urls = new router.UrlNode('ROOT', {handler:experimental.mongoTestHandler}, [
    new router.UrlNode('INDEX', {url:'test', handler:plain}, []),
    new router.UrlNode('REGISTER', {url:'register', handler:experimental.register}, []),
    new router.UrlNode('TSDB', {url:'tsdb', handler:tsdbHandler}, [])
]);

// dump url configuration
console.log(urls.generateUrlHandler());

// using connect framework to start the server
var app = connect();
app.use(connect.logger('dev'));
app.use(router(urls));
app.use(connect.static('static'));
app.listen(PORT);

console.log('server running at localhost:' + PORT);

console.log("connecting with a thrift controller")


// var ttransport = thrift.transport;

/*
 var connection = thrift.createConnection('localhost', 7932);
 client = thrift.createClient(managementService, connection);

 connection.on("error", function (err) {
 console.log("an error with the connection occured: " + err);
 });

 client.getLabels("srv2", function (err, result) {
 console.log("received a result");
 for (i in result) {
 console.log(result[i]);
 }
 });

 console.log("done");
 */

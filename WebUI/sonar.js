// Palermo server startup
var http = require('http');
var router = require('./router');
var connect = require('connect');
var experimental = require('./experimental');
var qs = require('querystring');

var PORT = 8080;

var thrift = require('thrift');
var managementService = require('./ManagementService');
var types = require("./collector_types");

function plain(req, resp) {
    resp.end("hello world");
}

function delSensorHandler(req, resp) {

}

function addSensorHandler(req, resp) {
    console.log("adding new sensor " + req.method);

    var body = "";

    req.on('data', function (data) {
        console.log("data: " + data);
        body += data;
    });

    req.on('end', function () {
        console.log("end: " + body);
        body = qs.parse(body);

        var connection = thrift.createConnection('localhost', 7932);
        client = thrift.createClient(managementService, connection);

        if (body.sensorName != null && body.sensorName.length > 3) {

            client.deploySensor(body.sensorName, "null", function (err, ret) {
                    console.log("sensor registered");

                    // Decompose the labels
                    var labels = body.sensorLabels.split(",");
                    console.log("labels " + labels);
                    client.setSensorLabels(body.sensorName, labels, function (err, ret) {
                        resp.end("ok");
                    });
                }
            )
            ;
        }

    })
}

function sensorsHandler(req, resp) {
    var connection = thrift.createConnection('localhost', 7932);
    client = thrift.createClient(managementService, connection);

    connection.on("error", function (err) {
        console.log("Could not connect with the Collector: " + err);
    });

    client.getAllSensors(function (err, result) {

        var sensorData = []

        var counter = 0;
        for (var sensor in result) {

            console.log("sensor " + result[sensor]);
            var value = result[sensor]
            console.log("VALUE " + value);

            var test = (function (value) {
                return function test(err, rr) {
                    counter++;
                    console.log("callback " + counter + " of " + result.length);

                    var sensorInfo = {
                        name:value,
                        labels:rr
                    }
                    console.log("PUSH: " + value);
                    sensorData.push(sensorInfo)

                    if (counter == result.length) {

                        console.log("running return ...");
                        console.log("test done");

                        console.log("sensor data: " + sensorData);
                        var ss = JSON.stringify(sensorData);
                        resp.end(ss);
                    }
                }
            })(value);


            client.getSensorLabels(result[sensor], test)
        }
    })
}

function tsdbHandler(req, resp) {
    var connection = thrift.createConnection('localhost', 7932);
    client = thrift.createClient(managementService, connection);

    connection.on("error", function (err) {
        console.log("Could not connect with the Collector: " + err);
    });

    var time = Math.round(new Date().getTime() / 100);
    console.log("time: " + time);

    var query = new types.TimeSeriesQuery({
        startTime:0,
        stopTime:time,
        hostname:"jack",
        sensor:"sensorhub"
    });

    client.query(query, function (err, result) {

            console.log("result received");
            console.log("length: " + result.length);

            var jsonObj = []; //declare array

            for (i in result) {
                console.log("value " + result[i].value);

                var time = result[i].timestamp;
                var value = result[i].value;

                jsonObj.push([time, value]);
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
    new router.UrlNode('TSDB', {url:'tsdb', handler:tsdbHandler}, []),
    new router.UrlNode('SENSORS', {url:'sensors', handler:sensorsHandler}, []),
    new router.UrlNode('SENSORADD', {url:'addsensor', handler:addSensorHandler}, [])
    new router.UrlNode('SENSORDEL', {url:'delsensor', handler:delSensorHandler}, [])
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

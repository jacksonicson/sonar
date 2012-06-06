// Palermo server startup
var http = require('http');
var router = require('./router');
var connect = require('connect');
var experimental = require('./experimental');
var qs = require('querystring');
var url = require('url');

var PORT = 8080;

var thrift = require('thrift');
var managementService = require('./ManagementService');
var types = require("./collector_types");

function plain(req, resp) {
    resp.end("hello world");
}

function delHostHandler(req, resp) {
    var connection = thrift.createConnection('localhost', 7932);
    var client = thrift.createClient(managementService, connection);

    var query = url.parse(req.url).query;
    var body = qs.parse(query);
    var hostname = body.hostname;

    client.delHost(hostname, function (err, ret) {
        console.log("host removed: " + hostname);
        resp.end("ok");
    })
}

function delSensorHandler(req, resp) {
    var connection = thrift.createConnection('localhost', 7932);
    var client = thrift.createClient(managementService, connection);

    var query = url.parse(req.url).query;
    var body = qs.parse(query);
    var sensorName = body.sensorName;

    console.log("deleting sensor name: " + sensorName);

    client.delSensor(sensorName, function (err, ret) {
        console.log("ok");
        resp.end("ok");
    });
}

function addHostHandler(req, resp) {
    console.log("add host handler");

    var body = "";
    req.on('data', function (data) {
        body += data;
    });

    req.on('end', function () {
        console.log("end host add body: " + body);
        body = qs.parse(body);

        var connection = thrift.createConnection('localhost', 7932);
        var client = thrift.createClient(managementService, connection);

        console.log("host name: " + body.hostname);

        if (body.hostname != null && body.hostname.length >= 3) {

            client.addHost(body.hostname, function (err, ret) {

                console.log("a");

                var labels = body.hostLabels.split(",");

                console.log("SAVING LABELS: " + labels);

                client.setHostLabels(body.hostname, labels, function (err, ret) {

                    console.log("b");
                    var sensorList = [];
                    for (var i in body) {
                        if (i.indexOf("sensor_") == 0) {
                            console.log("sensor active " + i);
                            sensorList[i.replace("sensor_", '')] = body[i]
                        }
                    }

                    var counter = 0;
                    for (var i in sensorList) {
                        var active = false;
                        if (sensorList[i] == "on") {
                            console.log("sensor " + i + " is active!!!!");
                            active = true;
                        }

                        client.setSensor(body.hostname, i, active, function (err, ret) {
                            counter++;
                            if (counter == sensorList.length) {
                                console.log("everything worked out...");
                                resp.end("ok");
                            }
                        })
                    }

                    if (sensorList.length == 0)
                        resp.end("ok");
                })
            })

        }

    })
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
        var client = thrift.createClient(managementService, connection);

        console.log("sensor name: " + body.sensorName);

        if (body.sensorName != null && body.sensorName.length >= 3) {


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

var connection = thrift.createConnection('localhost', 7932);
connection.on("error", function (err) {
    console.log("Could not connect with the Collector: " + err);
});

function hostsHandler(req, resp) {

    var connection = thrift.createConnection('localhost', 7932);
    var client = thrift.createClient(managementService, connection);

    var dataTable = []
    var counter = 0;

    console.log("hosts handler");

    // Get all registered sensors
    client.getAllSensors(function (err, sensors) {

        // Fetch all hosts
        client.getAllHosts(function (err, hosts) {

            if (hosts.length == 0) {
                resp.end(JSON.stringify(dataTable));
                return;
            }

            // Iterate over all hosts
            for (var i in hosts) {

                dataTable[i] = {
                    hostname:hosts[i],
                    labels:[],
                    sensor:[]
                }

                // Getting labels for the current host
                client.getLabels(hosts[i], (function (i) {
                    return function (err, labels) {

                        console.log("labels received");
                        dataTable[i].labels = labels;

                        counter++;
                        if (sensors.length == 0) {
                            if (counter == hosts.length) {
                                resp.end(JSON.stringify(dataTable));
                                return;
                            }
                        }

                        // Get sensor configuration for all (sensors + hosts)
                        for (var j in sensors) {
                            // Get bundled sensor configuration for the host
                            client.getBundledSensorConfiguration(sensors[j], hosts[i], (function (i, j) {
                                return function (err, sensorConfig) {
                                    dataTable[i].sensor[j] = {
                                        name:sensorConfig.sensor,
                                        labels:sensorConfig.labels,
                                        active:sensorConfig.active
                                    }

                                    // For each host all sensors have to be evaluated
                                    counter++;
                                    if (counter >= sensors.length * hosts.length) {
                                        resp.end(JSON.stringify(dataTable));
                                        return;
                                    }
                                }
                            })(i, j));
                        }
                    }
                })(i))


            }
        })
    });
}

function sensorsHandler(req, resp) {
    var connection = thrift.createConnection('localhost', 7932);
    var client = thrift.createClient(managementService, connection);

    connection.on("error", function (err) {
        console.log("Could not connect with the Collector: " + err);
    });

    client.getAllSensors(function (err, result) {

        console.log("returned from all sensors");

        var sensorData = []

        if (result.length == 0) {
            var ss = JSON.stringify(sensorData);
            resp.end(ss);
        }

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
        sensor:"TEST"
    });

    client.query(query, function (err, result) {

            console.log("result received: " + result);
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
    new router.UrlNode('SENSORADD', {url:'addsensor', handler:addSensorHandler}, []),
    new router.UrlNode('SENSORDEL', {url:'delsensor', handler:delSensorHandler}, []),
    new router.UrlNode('HOSTS', {url:'hosts', handler:hostsHandler}, []),
    new router.UrlNode('ADDHOST', {url:'addhost', handler:addHostHandler}, []),
    new router.UrlNode('DELHOST', {url:'delhost', handler:delHostHandler}, [])
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

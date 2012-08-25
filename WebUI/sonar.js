// http://jdewit.github.com/bootstrap-timepicker/
// http://www.rapidtables.com/web/color/Web_Color.htm
// Palermo server startup
    var http = require('http');
var template = require('swig');
var router = require('./router');
// var XDate = require('./xdate2');
var moment = require('moment')
var connect = require('connect');
var experimental = require('./experimental');
var qs = require('querystring');
var url = require('url');

var PORT = 8090;
// var SERVER_HOST = 'localhost';
var SERVER_HOST = 'monitor0.dfg';

var thrift = require('thrift');
var managementService = require('./ManagementService');
var types = require("./collector_types");

var connection = thrift.createConnection(SERVER_HOST, 7932);
connection.on("error", function (err) {
    console.log("Could not connect with the Collector: " + err);
});

function plain(req, resp) {
    resp.end("hello world");
}

function delHostHandler(req, resp) {
    var connection = thrift.createConnection(SERVER_HOST, 7932);
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
    var connection = thrift.createConnection(SERVER_HOST, 7932);
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

function bulkHostExtendsHandler(req, resp){
    console.log("bulk host extender handler");

    var body = "";
    req.on('data', function (data) {
        body += data;
    });

    req.on('end', function () {
        console.log("end host extend body: " + body);
        body = qs.parse(body);
        
        var connection = thrift.createConnection(SERVER_HOST, 7932);
        var client = thrift.createClient(managementService, connection);
        var counter = 0;
        var childHosts = body.childHost;
        
        if(childHosts instanceof Array){
            for(var index = 0; index < childHosts.length ; index++){
                client.addHostExtension(childHosts[index], body.parentHost, function (err, ret) {
                    counter++;
                    if (counter == childHosts.length) {
                        console.log("everything worked out...");
                        resp.end("ok");
                    }
                });
            }
        } else {
            client.addHostExtension(childHosts, body.parentHost, function (err, ret) {
                console.log("everything worked out...");
                resp.end("ok");
            });
        }
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

        var connection = thrift.createConnection(SERVER_HOST, 7932);
        var client = thrift.createClient(managementService, connection);

        console.log("host name: " + body.hostname);

        if (body.hostname != null && body.hostname.length >= 3) {

            client.getAllSensors(function (err, sensors) {

                client.addHost(body.hostname, function (err, ret) {

                    console.log("a");

                    var labels = body.hostLabels.split(",");

                    console.log("saving host extensions :" + body.hostExtends);
                    
                    client.addHostExtension(body.hostname, body.hostExtends, function (err, ret) {
                        
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

                            var disableList = [];
                            for (var s in sensors) {
                                if (sensorList.hasOwnProperty(sensors[s]) == false) {
                                    disableList[sensors[s]] = 'off';
                                }
                            }

                            for (var item in disableList) {
                                sensorList[item] = disableList[item];
                            }

                            var counter = 0;
                            for (var i in sensorList) {
                                var active = false;
                                if (sensorList[i] == "on") {
                                    console.log("sensor " + i + " is active!!!!");
                                    active = true;
                                }

                                console.log("SETTING SENSOR: " + i);

                                client.setSensor(body.hostname, i, active, function (err, ret) {
                                    console.log("sensor set " + i);
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

        var connection = thrift.createConnection(SERVER_HOST, 7932);
        var client = thrift.createClient(managementService, connection);

        console.log("sensor name: " + body.sensorName);

        if (body.sensorName != null && body.sensorName.length >= 3) {

            client.deploySensor(body.sensorName, "null", function (err, ret) {
                    console.log("sensor registered");

                    // Decompose the labels
                    var labels = body.sensorLabels.split(",");
                    console.log("labels " + labels);
                    client.setSensorLabels(body.sensorName, labels, function (err, ret) {
                        // decompose the sensor configuration parameters and set it
                        var sensorInterval = body.sensorInterval;
                        var sensorType = body.sensorType;
                        var paramKeys = body.sensorParamKey;
                        var paramValues = body.sensorParamValue;
                        var sensorExtends = body.sensorExtends;
                        var parameters = new Array();
                        var config = false;

                        // check if sensor configuration is specified
                        // if not change it to default 0
                        if(null != sensorInterval){
                            config = true;
                        } else {
                            sensorInterval = 0;
                        }
                        
                        var enumSensorType = null;
                        if(null == sensorType){
                            enumSensorType =  0;
                        } else if(sensorType == '0'){
                            enumSensorType = 0;
                        } else if(sensorType == '1'){
                            enumSensorType = 1;
                        }

                        console.log("Sensor type value: " + enumSensorType);
                        
                        console.log("Sensor Extends: " + sensorExtends);
                        if(null == sensorExtends || sensorExtends == "-1"){
                            sensorExtends = null;
                        }

                        // prepare the parameter array
                        if(null != paramKeys){
                            config = true;
                            if(paramKeys instanceof Array){
                                for(var index = 0; index < paramKeys.length ; index++){
                                    var parameter = new types.Parameter({
                                        key: paramKeys[index],
                                        value: paramValues[index]
                                    });
                                    parameters.push(parameter);
                                }
                            } else {
                                var parameter = new types.Parameter({
                                    key: paramKeys,
                                    value: paramValues
                                });
                                parameters.push(parameter);
                            }
                        }

                        if(config == true){
                            // prepare the sensor configuration object
                            var sensorConfiguration = new types.SensorConfiguration({
                                interval : sensorInterval,
                                parameters : parameters,
                                sensorType: enumSensorType,
                                sensorExtends: sensorExtends
                            });

                            client.setSensorConfiguration(body.sensorName, sensorConfiguration, function (err, ret) {
                                resp.end("ok");
                            });
                        }

                    });
                }
            )
            ;
        }

    })
}

function hostsHandler(req, resp) {

    var connection = thrift.createConnection(SERVER_HOST, 7932);
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
                    extendsHost:null,
                    labels:[],
                    sensor:[]
                }
                
                client.getHostExtension(hosts[i], (function (i) {
                    return function(err, extendsHost){
                        if(null != extendsHost){
                            console.log(i + "extends :" + extendsHost);
                            dataTable[i].extendsHost = extendsHost;
                        }
                        
                        // Getting labels for the current host
                        client.getLabels(hosts[i], (function (i) {
                            return function (err, labels) {

                                console.log("labels received");
                                dataTable[i].labels = labels;
                                if (sensors.length == 0) {
                                    counter++;
                                    if (counter == hosts.length) {
                                        resp.end(JSON.stringify(dataTable));
                                        console.log("Returning from here");
                                        return;
                                    }
                                }
                                console.log("sensors: " + sensors);
                            
                                // Get sensor configuration for all (sensors + hosts)
                                for (var j in sensors) {
                                    console.log("checking sensor: " + sensors[j]);
                                    // Get bundled sensor configuration for the host
                                    client.getBundledSensorConfiguration(sensors[j], hosts[i], (function (i, j) {
                                        return function (err, sensorConfig) {
                                            dataTable[i].sensor[j] = {
                                                name:sensorConfig.sensor,
                                                labels:sensorConfig.labels,
                                                active:sensorConfig.active
                                            }
                                            
                                            console.log(i + ":" + hosts[i] + ":" + dataTable[i].sensor[j].name+ ":" + dataTable[i].sensor[j].active);

                                            // For each host all sensors have to be evaluated
                                            counter++;
                                            if (counter >= sensors.length * hosts.length) {
                                                resp.end(JSON.stringify(dataTable));
                                                console.log("Processing done");
                                                return;
                                            }
                                        }
                                    })(i, j));
                                }
                            }
                        })(i))
                    }  
                })(i))
            }
        })
    });
}

function sensorsHandler(req, resp) {
    var connection = thrift.createConnection(SERVER_HOST, 7932);
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

                    console.log("labels: " + rr);

                    client.hasBinary(value, function (err, hasBinary) {

                        console.log("Has binary: " + hasBinary);

                        counter++;
                        console.log("callback " + counter + " of " + result.length);

                        var sensorInfo = {
                            name:value,
                            labels:rr,
                            binary:hasBinary
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

                    });


                }
            })(value);

            client.getSensorLabels(result[sensor], test)
        }
    })
}

function logdbHandler(req, resp){

	var body="";
	if (req.method == 'GET') {
        var jsonObj = [];
        var ss = JSON.stringify(jsonObj);
        console.log(ss);
        resp.end(ss);

        return;
    }


    req.on('data', function (data) {
        body += data;
    });

    req.on('end', function () {
        body = qs.parse(body);

        var connection = thrift.createConnection(SERVER_HOST, 7932);
        var client = thrift.createClient(managementService, connection);

        connection.on("error", function (err) {
            console.log("Could not connect with the Collector: " + err);
        });


		var startDate = body.startdate + body.starttime;
		var stopDate = body.stopdate + body.stoptime;;
		
        var startUnix = moment(startDate, "MM/DD/YYYY hh:mm a")/1000;
        var endUnix = moment(stopDate, "MM/DD/YYYY hh:mm a")/1000;
        var hostname = body.hostname;
        var sensor = body.sensor;

        console.log("hostname: " + hostname);
        console.log("sensor: " + sensor);
        console.log("startTime: " + startUnix);
        console.log("endTime: " + endUnix);

		var query = new types.LogsQuery({
			startTime : startUnix,
			stopTime : endUnix,
			sensor : sensor,
			hostname : hostname
		});
		
        // Execute the query
        client.queryLogs(query, function (err, logMessages) {
			var ss = JSON.stringify(logMessages);
            console.log(ss);
            resp.end(ss);
        });
    });
	
}

function tsdbHandler(req, resp) {

    var body = "";

    if (req.method == 'GET') {
        var jsonObj = [];
        var ss = JSON.stringify(jsonObj);
        console.log(ss);
        resp.end(ss);

        return;
    }


    req.on('data', function (data) {
        body += data;
    });

    req.on('end', function () {
        body = qs.parse(body);

        console.log("startTime: " + body.startdate);

        var connection = thrift.createConnection(SERVER_HOST, 7932);
        var client = thrift.createClient(managementService, connection);

        connection.on("error", function (err) {
            console.log("Could not connect with the Collector: " + err);
        });


        var startDate = body.startdate + body.starttime;
		var stopDate = body.stopdate + body.stoptime;;
		
        var startUnix = moment(startDate, "MM/DD/YYYY hh:mm a")/1000;
        var endUnix = moment(stopDate, "MM/DD/YYYY hh:mm a")/1000;

        var labels = body.labels;
        var hostname = body.hostname;
        var sensor = body.sensor;

        console.log("hostname: " + hostname);
        console.log("sensor: " + sensor);
        console.log("startTime: " + startUnix);
        console.log("endTime: " + endUnix);

        var query = new types.TimeSeriesQuery({
            startTime:startUnix,
            stopTime:endUnix,

            hostname:hostname,
            sensor:sensor
        });

        // Execute the query
        client.query(query, function (err, timeSeries) {

            var jsonObj = [];

            for (i in timeSeries) {
                // console.log("received feedback " + timeSeries[i].value);
                var item = [timeSeries[i].timestamp * 1000, timeSeries[i].value];
                jsonObj.push(item)
            }

            console.log(timeSeries.length + "data received");
            jsonObj.sort( function(a, b) {
                return a[0] - b[0]
            });

            var ss = JSON.stringify(jsonObj);
            
            resp.end(ss);
        });
    });
}

function sensorConfigHandler(req, resp){
    var body = "";

    req.on('data', function (data) {
        body += data;
    });

    req.on('end', function () {
        body = qs.parse(body);
        var sensor = body.sensor;
        console.log("Requesting configuration for sensor: " + body.sensor);

        var connection = thrift.createConnection(SERVER_HOST, 7932);
        var client = thrift.createClient(managementService, connection);

        connection.on("error", function (err) {
            console.log("Could not connect with the Collector: " + err);
        });

        // Execute the query
        client.getSensorConfiguration(sensor, function (err, configurationData) {
            var ss = JSON.stringify(configurationData);
            console.log(ss);
            resp.end(ss);
        });
    });
}

function sensorNamesHandler(req, resp){

    req.on('end', function () {
        console.log("Requesting all sensors");

        var connection = thrift.createConnection(SERVER_HOST, 7932);
        var client = thrift.createClient(managementService, connection);
        var sensorData = []
        connection.on("error", function (err) {
            console.log("Could not connect with the Collector: " + err);
        });

        // Execute the query
        client.getSensorNames(function (err, sensorNames) {

            for(var count = 0; count < sensorNames.length; count++){
                var sensorInfo = {
                    name:sensorNames[count]
                }
                sensorData.push(sensorInfo);
            }
            var ss = JSON.stringify(sensorData);
            console.log(ss);
            resp.end(ss);
        });
    });
}

// Getting started with monogdb
// http://howtonode.org/node-js-and-mongodb-getting-started-with-mongojs

// From validation
// https://github.com/chriso/node-validator

// Swig templating engine
// https://github.com/paularmstrong/swig
// http://paularmstrong.github.com/node-templates/

template.init({
    allowErrors:false,
    autoescape:false,
    cache:false,
    encoding:'utf8',
    filters:{},
    root:'static',
    tags:{},
    extensions:{},
    tzOffset:0
})

function browse(req, resp) {
    var compiled = template.compileFile('browse.html');
    var rendered = compiled.render({
    });
    resp.end(rendered);
}

function logs(req, resp) {
    var compiled = template.compileFile('logs.html');
    var rendered = compiled.render({
    });
    resp.end(rendered);
}

function config(req, resp) {
    var compiled = template.compileFile('config.html');
    var rendered = compiled.render({
    });
    resp.end(rendered);
}


function configjs(req, resp) {
    var compiled = template.compileFile('config.js');

    var urlMap = urls.generateUrlMap();
    console.log("RUNNING CONFIG")
    console.log("URLS " + urlMap);

    var rendered = compiled.render(urlMap);
    resp.writeHead(200, {
        'Content-Type':'text/javascript',
        'Content-Length':rendered.length
    })
    resp.end(rendered);
}

// configure urls
var urls = new router.UrlNode('ROOT', {handler:experimental.mongoTestHandler}, [
    new router.UrlNode('BROWSE', {url:'browse', handler:browse}, []),
    new router.UrlNode('CONFIG', {url:'config', handler:config}, []),
	new router.UrlNode('LOGS', {url:'logs', handler:logs}, []),
	
    new router.UrlNode('CONFIGJS', {url:'config.js', handler:configjs}, []),

    new router.UrlNode('INDEX', {url:'test', handler:plain}, []),
    new router.UrlNode('REGISTER', {url:'register', handler:experimental.register}, []),
    new router.UrlNode('TSDB', {url:'tsdb', handler:tsdbHandler}, []),
    new router.UrlNode('SENSORS', {url:'sensors', handler:sensorsHandler}, []),
    new router.UrlNode('SENSORADD', {url:'addsensor', handler:addSensorHandler}, []),
    new router.UrlNode('SENSORDEL', {url:'delsensor', handler:delSensorHandler}, []),
    new router.UrlNode('SENSORCONF', {url:'sensorConfig', handler:sensorConfigHandler}, []),
    new router.UrlNode('HOSTS', {url:'hosts', handler:hostsHandler}, []),
    new router.UrlNode('ADDHOST', {url:'addhost', handler:addHostHandler}, []),
    new router.UrlNode('DELHOST', {url:'delhost', handler:delHostHandler}, []),
    new router.UrlNode('HOSTEXTEND', {url:'hostExtend', handler:bulkHostExtendsHandler}, []),
	new router.UrlNode('LOGDB', {url:'logdb', handler:logdbHandler}, []),
    new router.UrlNode('SENSORNAMES', {url:'sensornames', handler:sensorNamesHandler}, [])
]);

// dump url configuration
console.log(urls.generateUrlHandler());

// using connect framework to start the server
var app = connect();
app.use(connect.logger('dev'));
app.use(router(urls));
app.use(connect.static('static'));
app.listen(PORT);

console.log('server running at ' + SERVER_HOST + '.dfg:' + PORT);

console.log("connecting with a thrift controller")


// var ttransport = thrift.transport;

/*
 var connection = thrift.createConnection(SERVER_HOST, 7932);
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

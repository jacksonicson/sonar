// Palermo server startup
var http = require('http');
var router = require('./router');
var connect = require('connect');
var experimental = require('./experimental');

var PORT = 8080;

function plain(req, resp) {
    resp.end("hello world");
}

// configure urls
var urls = new router.UrlNode('ROOT', {handler:experimental.mongoTestHandler}, [
    new router.UrlNode('INDEX', {url:'test', handler:plain}, []),
    new router.UrlNode('REGISTER', {url:'register', handler:experimental.register}, [])
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


var thrift = require('thrift');
var managementService = require('./ManagementService');

var ttransport = thrift.transport;

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


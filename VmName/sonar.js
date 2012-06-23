var http = require('http');
var connect = require('connect')
var fs = require('fs')
var url = require('url')

PORT = 7754

fs.readFile('vm.index', 'ascii', function(err, data){

    if(err) {
        console.error("Could not open file: %s", err);
        process.exit(1);
    }

    value = parseInt(data)

    function handler(req, resp)
    {
        requestedUri = url.parse(req.url).pathname;
        if(requestedUri != '/new')
        {
            resp.writeHead(404)
            resp.end()
            return
        }

        value++
        fs.writeFile('vm.index', '' + value, function(err) {
            if(err) {
                console.log(err);
            } else {
                resp.writeHead(400, {"Content-Type": "text/plain"})
                resp.end("vm" + value)
            }
        })
    }

    // using connect framework to start the server
    var app = connect();
    app.use(connect.logger('dev'));
    app.use(handler);
    app.listen(PORT);

    console.log('server running at localhost:' + PORT);

});






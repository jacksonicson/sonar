var database = require('./database');
var template = require('swig');
var check = require('validator').check, sanitize = require('validator').sanitize;
var url = require('url');

// Getting started with monogdb
// http://howtonode.org/node-js-and-mongodb-getting-started-with-mongojs

// From validation
// https://github.com/chriso/node-validator

// Swig templating engine
// https://github.com/paularmstrong/swig
// http://paularmstrong.github.com/node-templates/

function validate(handler, messageList) {
    try {
        handler();
    } catch(err) {
        messageList.push(err.message)
    }
}

function register(req, resp) {

    var errors = new Array();

    parsedUrl = url.parse(req.url, true)

    validate(function() { check(parsedUrl.query.mail, 'Invalid Username').len(6, 64) }, errors)

    if(errors.length > 0)
    {
        console.log(errors);
        resp.end(errors.toString());
    } else {
        resp.end("ok");
    }
}

function mongoTestHandler(req, resp) {

    database.db.users.save({email:"srirangan@gmail.com", password:"iLoveMongo", sex:"male"},
        function (err, saved) {
            if (err || !saved) console.log("User not saved");
            else console.log("User saved");

            var tmpl = template.compileFile(process.cwd() + "/static/index.html");
            var page = tmpl.render({
                test:'test value'
            });

            resp.end(page);
        });
}

exports.mongoTestHandler = mongoTestHandler;
exports.register = register;
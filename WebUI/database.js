var databaseUrl = "localhost/users"; // "username:password@example.com/mydb"
var collections = ["users", "reports"]
var db = require("mongojs");

exports.db = db.connect(databaseUrl, collections);
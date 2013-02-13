/**
 * Created with JetBrains WebStorm.
 * User: jack
 * Date: 08.06.12
 * Time: 21:36
 * To change this template use File | Settings | File Templates.
 */

var fs = require("fs");

filedat = fs.readFileSync("xdate.js", "utf8");
eval(filedat);

exports.XDate = XDate;
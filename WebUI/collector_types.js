//
// Autogenerated by Thrift Compiler (0.8.0)
//
// DO NOT EDIT UNLESS YOU ARE SURE THAT YOU KNOW WHAT YOU ARE DOING
//
var Thrift = require('thrift').Thrift;
var ttypes = module.exports = {};
var Identifier = module.exports.Identifier = function(args) {
  this.timestamp = null;
  this.sensor = null;
  this.hostname = null;
  if (args) {
    if (args.timestamp !== undefined) {
      this.timestamp = args.timestamp;
    }
    if (args.sensor !== undefined) {
      this.sensor = args.sensor;
    }
    if (args.hostname !== undefined) {
      this.hostname = args.hostname;
    }
  }
};
Identifier.prototype = {};
Identifier.prototype.read = function(input) {
  input.readStructBegin();
  while (true)
  {
    var ret = input.readFieldBegin();
    var fname = ret.fname;
    var ftype = ret.ftype;
    var fid = ret.fid;
    if (ftype == Thrift.Type.STOP) {
      break;
    }
    switch (fid)
    {
      case 1:
      if (ftype == Thrift.Type.I64) {
        this.timestamp = input.readI64();
      } else {
        input.skip(ftype);
      }
      break;
      case 3:
      if (ftype == Thrift.Type.STRING) {
        this.sensor = input.readString();
      } else {
        input.skip(ftype);
      }
      break;
      case 2:
      if (ftype == Thrift.Type.STRING) {
        this.hostname = input.readString();
      } else {
        input.skip(ftype);
      }
      break;
      default:
        input.skip(ftype);
    }
    input.readFieldEnd();
  }
  input.readStructEnd();
  return;
};

Identifier.prototype.write = function(output) {
  output.writeStructBegin('Identifier');
  if (this.timestamp) {
    output.writeFieldBegin('timestamp', Thrift.Type.I64, 1);
    output.writeI64(this.timestamp);
    output.writeFieldEnd();
  }
  if (this.sensor) {
    output.writeFieldBegin('sensor', Thrift.Type.STRING, 3);
    output.writeString(this.sensor);
    output.writeFieldEnd();
  }
  if (this.hostname) {
    output.writeFieldBegin('hostname', Thrift.Type.STRING, 2);
    output.writeString(this.hostname);
    output.writeFieldEnd();
  }
  output.writeFieldStop();
  output.writeStructEnd();
  return;
};

var MetricReading = module.exports.MetricReading = function(args) {
  this.value = null;
  this.labels = null;
  if (args) {
    if (args.value !== undefined) {
      this.value = args.value;
    }
    if (args.labels !== undefined) {
      this.labels = args.labels;
    }
  }
};
MetricReading.prototype = {};
MetricReading.prototype.read = function(input) {
  input.readStructBegin();
  while (true)
  {
    var ret = input.readFieldBegin();
    var fname = ret.fname;
    var ftype = ret.ftype;
    var fid = ret.fid;
    if (ftype == Thrift.Type.STOP) {
      break;
    }
    switch (fid)
    {
      case 1:
      if (ftype == Thrift.Type.DOUBLE) {
        this.value = input.readDouble();
      } else {
        input.skip(ftype);
      }
      break;
      case 3:
      if (ftype == Thrift.Type.SET) {
        var _size0 = 0;
        var _rtmp34;
        this.labels = [];
        var _etype3 = 0;
        _rtmp34 = input.readSetBegin();
        _etype3 = _rtmp34.etype;
        _size0 = _rtmp34.size;
        for (var _i5 = 0; _i5 < _size0; ++_i5)
        {
          var elem6 = null;
          elem6 = input.readString();
          this.labels.push(elem6);
        }
        input.readSetEnd();
      } else {
        input.skip(ftype);
      }
      break;
      default:
        input.skip(ftype);
    }
    input.readFieldEnd();
  }
  input.readStructEnd();
  return;
};

MetricReading.prototype.write = function(output) {
  output.writeStructBegin('MetricReading');
  if (this.value) {
    output.writeFieldBegin('value', Thrift.Type.DOUBLE, 1);
    output.writeDouble(this.value);
    output.writeFieldEnd();
  }
  if (this.labels) {
    output.writeFieldBegin('labels', Thrift.Type.SET, 3);
    output.writeSetBegin(Thrift.Type.STRING, this.labels.length);
    for (var iter7 in this.labels)
    {
      if (this.labels.hasOwnProperty(iter7))
      {
        iter7 = this.labels[iter7];
        output.writeString(iter7);
      }
    }
    output.writeSetEnd();
    output.writeFieldEnd();
  }
  output.writeFieldStop();
  output.writeStructEnd();
  return;
};

var LogMessage = module.exports.LogMessage = function(args) {
  this.logLevel = null;
  this.logMessage = null;
  this.programName = null;
  if (args) {
    if (args.logLevel !== undefined) {
      this.logLevel = args.logLevel;
    }
    if (args.logMessage !== undefined) {
      this.logMessage = args.logMessage;
    }
    if (args.programName !== undefined) {
      this.programName = args.programName;
    }
  }
};
LogMessage.prototype = {};
LogMessage.prototype.read = function(input) {
  input.readStructBegin();
  while (true)
  {
    var ret = input.readFieldBegin();
    var fname = ret.fname;
    var ftype = ret.ftype;
    var fid = ret.fid;
    if (ftype == Thrift.Type.STOP) {
      break;
    }
    switch (fid)
    {
      case 1:
      if (ftype == Thrift.Type.I32) {
        this.logLevel = input.readI32();
      } else {
        input.skip(ftype);
      }
      break;
      case 2:
      if (ftype == Thrift.Type.STRING) {
        this.logMessage = input.readString();
      } else {
        input.skip(ftype);
      }
      break;
      case 3:
      if (ftype == Thrift.Type.STRING) {
        this.programName = input.readString();
      } else {
        input.skip(ftype);
      }
      break;
      default:
        input.skip(ftype);
    }
    input.readFieldEnd();
  }
  input.readStructEnd();
  return;
};

LogMessage.prototype.write = function(output) {
  output.writeStructBegin('LogMessage');
  if (this.logLevel) {
    output.writeFieldBegin('logLevel', Thrift.Type.I32, 1);
    output.writeI32(this.logLevel);
    output.writeFieldEnd();
  }
  if (this.logMessage) {
    output.writeFieldBegin('logMessage', Thrift.Type.STRING, 2);
    output.writeString(this.logMessage);
    output.writeFieldEnd();
  }
  if (this.programName) {
    output.writeFieldBegin('programName', Thrift.Type.STRING, 3);
    output.writeString(this.programName);
    output.writeFieldEnd();
  }
  output.writeFieldStop();
  output.writeStructEnd();
  return;
};

var File = module.exports.File = function(args) {
  this.filename = null;
  this.description = null;
  this.file = null;
  this.labels = null;
  if (args) {
    if (args.filename !== undefined) {
      this.filename = args.filename;
    }
    if (args.description !== undefined) {
      this.description = args.description;
    }
    if (args.file !== undefined) {
      this.file = args.file;
    }
    if (args.labels !== undefined) {
      this.labels = args.labels;
    }
  }
};
File.prototype = {};
File.prototype.read = function(input) {
  input.readStructBegin();
  while (true)
  {
    var ret = input.readFieldBegin();
    var fname = ret.fname;
    var ftype = ret.ftype;
    var fid = ret.fid;
    if (ftype == Thrift.Type.STOP) {
      break;
    }
    switch (fid)
    {
      case 1:
      if (ftype == Thrift.Type.STRING) {
        this.filename = input.readString();
      } else {
        input.skip(ftype);
      }
      break;
      case 2:
      if (ftype == Thrift.Type.STRING) {
        this.description = input.readString();
      } else {
        input.skip(ftype);
      }
      break;
      case 3:
      if (ftype == Thrift.Type.STRING) {
        this.file = input.readString();
      } else {
        input.skip(ftype);
      }
      break;
      case 4:
      if (ftype == Thrift.Type.SET) {
        var _size8 = 0;
        var _rtmp312;
        this.labels = [];
        var _etype11 = 0;
        _rtmp312 = input.readSetBegin();
        _etype11 = _rtmp312.etype;
        _size8 = _rtmp312.size;
        for (var _i13 = 0; _i13 < _size8; ++_i13)
        {
          var elem14 = null;
          elem14 = input.readString();
          this.labels.push(elem14);
        }
        input.readSetEnd();
      } else {
        input.skip(ftype);
      }
      break;
      default:
        input.skip(ftype);
    }
    input.readFieldEnd();
  }
  input.readStructEnd();
  return;
};

File.prototype.write = function(output) {
  output.writeStructBegin('File');
  if (this.filename) {
    output.writeFieldBegin('filename', Thrift.Type.STRING, 1);
    output.writeString(this.filename);
    output.writeFieldEnd();
  }
  if (this.description) {
    output.writeFieldBegin('description', Thrift.Type.STRING, 2);
    output.writeString(this.description);
    output.writeFieldEnd();
  }
  if (this.file) {
    output.writeFieldBegin('file', Thrift.Type.STRING, 3);
    output.writeString(this.file);
    output.writeFieldEnd();
  }
  if (this.labels) {
    output.writeFieldBegin('labels', Thrift.Type.SET, 4);
    output.writeSetBegin(Thrift.Type.STRING, this.labels.length);
    for (var iter15 in this.labels)
    {
      if (this.labels.hasOwnProperty(iter15))
      {
        iter15 = this.labels[iter15];
        output.writeString(iter15);
      }
    }
    output.writeSetEnd();
    output.writeFieldEnd();
  }
  output.writeFieldStop();
  output.writeStructEnd();
  return;
};

var TransferableTimeSeriesPoint = module.exports.TransferableTimeSeriesPoint = function(args) {
  this.timestamp = null;
  this.value = null;
  this.labels = null;
  if (args) {
    if (args.timestamp !== undefined) {
      this.timestamp = args.timestamp;
    }
    if (args.value !== undefined) {
      this.value = args.value;
    }
    if (args.labels !== undefined) {
      this.labels = args.labels;
    }
  }
};
TransferableTimeSeriesPoint.prototype = {};
TransferableTimeSeriesPoint.prototype.read = function(input) {
  input.readStructBegin();
  while (true)
  {
    var ret = input.readFieldBegin();
    var fname = ret.fname;
    var ftype = ret.ftype;



    var fid = ret.fid;

      console.log("name " + fname + " type " + fid)

    if (ftype == Thrift.Type.STOP) {
      break;
    }
    switch (fid)
    {
      case 1:
      if (ftype == Thrift.Type.I64) {
        this.timestamp = input.readI64();
      } else {
        input.skip(ftype);
      }
      break;
      case 2:
      if (ftype == Thrift.Type.DOUBLE) {
        this.value = input.readDouble();
      } else {
        input.skip(ftype);
      }
      break;
      case 3:
      if (ftype == Thrift.Type.SET) {
        var _size16 = 0;
        var _rtmp320;
        this.labels = [];
        var _etype19 = 0;
        _rtmp320 = input.readSetBegin();
        _etype19 = _rtmp320.etype;
        _size16 = _rtmp320.size;
        for (var _i21 = 0; _i21 < _size16; ++_i21)
        {
          var elem22 = null;
          elem22 = input.readString();
          this.labels.push(elem22);
        }
        input.readSetEnd();
      } else {
        input.skip(ftype);
      }
      break;
      default:
        input.skip(ftype);
    }
    input.readFieldEnd();
  }
  input.readStructEnd();
  return;
};

TransferableTimeSeriesPoint.prototype.write = function(output) {
  output.writeStructBegin('TransferableTimeSeriesPoint');
  if (this.timestamp) {
    output.writeFieldBegin('timestamp', Thrift.Type.I64, 1);
    output.writeI64(this.timestamp);
    output.writeFieldEnd();
  }
  if (this.value) {
    output.writeFieldBegin('value', Thrift.Type.DOUBLE, 2);
    output.writeDouble(this.value);
    output.writeFieldEnd();
  }
  if (this.labels) {
    output.writeFieldBegin('labels', Thrift.Type.SET, 3);
    output.writeSetBegin(Thrift.Type.STRING, this.labels.length);
    for (var iter23 in this.labels)
    {
      if (this.labels.hasOwnProperty(iter23))
      {
        iter23 = this.labels[iter23];
        output.writeString(iter23);
      }
    }
    output.writeSetEnd();
    output.writeFieldEnd();
  }
  output.writeFieldStop();
  output.writeStructEnd();
  return;
};

var TimeSeriesQuery = module.exports.TimeSeriesQuery = function(args) {
  this.startTime = null;
  this.stopTime = null;
  this.sensor = null;
  this.labels = null;
  this.hostname = null;
  if (args) {
    if (args.startTime !== undefined) {
      this.startTime = args.startTime;
    }
    if (args.stopTime !== undefined) {
      this.stopTime = args.stopTime;
    }
    if (args.sensor !== undefined) {
      this.sensor = args.sensor;
    }
    if (args.labels !== undefined) {
      this.labels = args.labels;
    }
    if (args.hostname !== undefined) {
      this.hostname = args.hostname;
    }
  }
};
TimeSeriesQuery.prototype = {};
TimeSeriesQuery.prototype.read = function(input) {
  input.readStructBegin();
  while (true)
  {
    var ret = input.readFieldBegin();
    var fname = ret.fname;
    var ftype = ret.ftype;
    var fid = ret.fid;
    if (ftype == Thrift.Type.STOP) {
      break;
    }
    switch (fid)
    {
      case 1:
      if (ftype == Thrift.Type.I64) {
        this.startTime = input.readI64();
      } else {
        input.skip(ftype);
      }
      break;
      case 2:
      if (ftype == Thrift.Type.I64) {
        this.stopTime = input.readI64();
      } else {
        input.skip(ftype);
      }
      break;
      case 3:
      if (ftype == Thrift.Type.STRING) {
        this.sensor = input.readString();
      } else {
        input.skip(ftype);
      }
      break;
      case 5:
      if (ftype == Thrift.Type.SET) {
        var _size24 = 0;
        var _rtmp328;
        this.labels = [];
        var _etype27 = 0;
        _rtmp328 = input.readSetBegin();
        _etype27 = _rtmp328.etype;
        _size24 = _rtmp328.size;
        for (var _i29 = 0; _i29 < _size24; ++_i29)
        {
          var elem30 = null;
          elem30 = input.readString();
          this.labels.push(elem30);
        }
        input.readSetEnd();
      } else {
        input.skip(ftype);
      }
      break;
      case 4:
      if (ftype == Thrift.Type.STRING) {
        this.hostname = input.readString();
      } else {
        input.skip(ftype);
      }
      break;
      default:
        input.skip(ftype);
    }
    input.readFieldEnd();
  }
  input.readStructEnd();
  return;
};

TimeSeriesQuery.prototype.write = function(output) {
  output.writeStructBegin('TimeSeriesQuery');
  if (this.startTime) {
    output.writeFieldBegin('startTime', Thrift.Type.I64, 1);
    output.writeI64(this.startTime);
    output.writeFieldEnd();
  }
  if (this.stopTime) {
    output.writeFieldBegin('stopTime', Thrift.Type.I64, 2);
    output.writeI64(this.stopTime);
    output.writeFieldEnd();
  }
  if (this.sensor) {
    output.writeFieldBegin('sensor', Thrift.Type.STRING, 3);
    output.writeString(this.sensor);
    output.writeFieldEnd();
  }
  if (this.labels) {
    output.writeFieldBegin('labels', Thrift.Type.SET, 5);
    output.writeSetBegin(Thrift.Type.STRING, this.labels.length);
    for (var iter31 in this.labels)
    {
      if (this.labels.hasOwnProperty(iter31))
      {
        iter31 = this.labels[iter31];
        output.writeString(iter31);
      }
    }
    output.writeSetEnd();
    output.writeFieldEnd();
  }
  if (this.hostname) {
    output.writeFieldBegin('hostname', Thrift.Type.STRING, 4);
    output.writeString(this.hostname);
    output.writeFieldEnd();
  }
  output.writeFieldStop();
  output.writeStructEnd();
  return;
};

var SensorConfiguration = module.exports.SensorConfiguration = function(args) {
  this.interval = null;
  if (args) {
    if (args.interval !== undefined) {
      this.interval = args.interval;
    }
  }
};
SensorConfiguration.prototype = {};
SensorConfiguration.prototype.read = function(input) {
  input.readStructBegin();
  while (true)
  {
    var ret = input.readFieldBegin();
    var fname = ret.fname;
    var ftype = ret.ftype;
    var fid = ret.fid;
    if (ftype == Thrift.Type.STOP) {
      break;
    }
    switch (fid)
    {
      case 1:
      if (ftype == Thrift.Type.I64) {
        this.interval = input.readI64();
      } else {
        input.skip(ftype);
      }
      break;
      case 0:
        input.skip(ftype);
        break;
      default:
        input.skip(ftype);
    }
    input.readFieldEnd();
  }
  input.readStructEnd();
  return;
};

SensorConfiguration.prototype.write = function(output) {
  output.writeStructBegin('SensorConfiguration');
  if (this.interval) {
    output.writeFieldBegin('interval', Thrift.Type.I64, 1);
    output.writeI64(this.interval);
    output.writeFieldEnd();
  }
  output.writeFieldStop();
  output.writeStructEnd();
  return;
};

var BundledSensorConfiguration = module.exports.BundledSensorConfiguration = function(args) {
  this.sensor = null;
  this.hostname = null;
  this.labels = null;
  this.configuration = null;
  this.active = null;
  if (args) {
    if (args.sensor !== undefined) {
      this.sensor = args.sensor;
    }
    if (args.hostname !== undefined) {
      this.hostname = args.hostname;
    }
    if (args.labels !== undefined) {
      this.labels = args.labels;
    }
    if (args.configuration !== undefined) {
      this.configuration = args.configuration;
    }
    if (args.active !== undefined) {
      this.active = args.active;
    }
  }
};
BundledSensorConfiguration.prototype = {};
BundledSensorConfiguration.prototype.read = function(input) {
  input.readStructBegin();
  while (true)
  {
    var ret = input.readFieldBegin();
    var fname = ret.fname;
    var ftype = ret.ftype;
    var fid = ret.fid;
    if (ftype == Thrift.Type.STOP) {
      break;
    }
    switch (fid)
    {
      case 1:
      if (ftype == Thrift.Type.STRING) {
        this.sensor = input.readString();
      } else {
        input.skip(ftype);
      }
      break;
      case 2:
      if (ftype == Thrift.Type.STRING) {
        this.hostname = input.readString();
      } else {
        input.skip(ftype);
      }
      break;
      case 3:
      if (ftype == Thrift.Type.SET) {
        var _size32 = 0;
        var _rtmp336;
        this.labels = [];
        var _etype35 = 0;
        _rtmp336 = input.readSetBegin();
        _etype35 = _rtmp336.etype;
        _size32 = _rtmp336.size;
        for (var _i37 = 0; _i37 < _size32; ++_i37)
        {
          var elem38 = null;
          elem38 = input.readString();
          this.labels.push(elem38);
        }
        input.readSetEnd();
      } else {
        input.skip(ftype);
      }
      break;
      case 4:
      if (ftype == Thrift.Type.STRUCT) {
        this.configuration = new ttypes.SensorConfiguration();
        this.configuration.read(input);
      } else {
        input.skip(ftype);
      }
      break;
      case 5:
      if (ftype == Thrift.Type.BOOL) {
        this.active = input.readBool();
      } else {
        input.skip(ftype);
      }
      break;
      default:
        input.skip(ftype);
    }
    input.readFieldEnd();
  }
  input.readStructEnd();
  return;
};

BundledSensorConfiguration.prototype.write = function(output) {
  output.writeStructBegin('BundledSensorConfiguration');
  if (this.sensor) {
    output.writeFieldBegin('sensor', Thrift.Type.STRING, 1);
    output.writeString(this.sensor);
    output.writeFieldEnd();
  }
  if (this.hostname) {
    output.writeFieldBegin('hostname', Thrift.Type.STRING, 2);
    output.writeString(this.hostname);
    output.writeFieldEnd();
  }
  if (this.labels) {
    output.writeFieldBegin('labels', Thrift.Type.SET, 3);
    output.writeSetBegin(Thrift.Type.STRING, this.labels.length);
    for (var iter39 in this.labels)
    {
      if (this.labels.hasOwnProperty(iter39))
      {
        iter39 = this.labels[iter39];
        output.writeString(iter39);
      }
    }
    output.writeSetEnd();
    output.writeFieldEnd();
  }
  if (this.configuration) {
    output.writeFieldBegin('configuration', Thrift.Type.STRUCT, 4);
    this.configuration.write(output);
    output.writeFieldEnd();
  }
  if (this.active) {
    output.writeFieldBegin('active', Thrift.Type.BOOL, 5);
    output.writeBool(this.active);
    output.writeFieldEnd();
  }
  output.writeFieldStop();
  output.writeStructEnd();
  return;
};


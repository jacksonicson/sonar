//
// Autogenerated by Thrift Compiler (0.8.0)
//
// DO NOT EDIT UNLESS YOU ARE SURE THAT YOU KNOW WHAT YOU ARE DOING
//
var Thrift = require('thrift').Thrift;

var ttypes = require('./collector_types');
//HELPER FUNCTIONS AND STRUCTURES

var CollectService_logMessage_args = function(args) {
  this.id = null;
  this.message = null;
  if (args) {
    if (args.id !== undefined) {
      this.id = args.id;
    }
    if (args.message !== undefined) {
      this.message = args.message;
    }
  }
};
CollectService_logMessage_args.prototype = {};
CollectService_logMessage_args.prototype.read = function(input) {
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
      if (ftype == Thrift.Type.STRUCT) {
        this.id = new ttypes.Identifier();
        this.id.read(input);
      } else {
        input.skip(ftype);
      }
      break;
      case 2:
      if (ftype == Thrift.Type.STRING) {
        this.message = input.readString();
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

CollectService_logMessage_args.prototype.write = function(output) {
  output.writeStructBegin('CollectService_logMessage_args');
  if (this.id) {
    output.writeFieldBegin('id', Thrift.Type.STRUCT, 1);
    this.id.write(output);
    output.writeFieldEnd();
  }
  if (this.message) {
    output.writeFieldBegin('message', Thrift.Type.STRING, 2);
    output.writeString(this.message);
    output.writeFieldEnd();
  }
  output.writeFieldStop();
  output.writeStructEnd();
  return;
};

var CollectService_logMessage_result = function(args) {
};
CollectService_logMessage_result.prototype = {};
CollectService_logMessage_result.prototype.read = function(input) {
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
    input.skip(ftype);
    input.readFieldEnd();
  }
  input.readStructEnd();
  return;
};

CollectService_logMessage_result.prototype.write = function(output) {
  output.writeStructBegin('CollectService_logMessage_result');
  output.writeFieldStop();
  output.writeStructEnd();
  return;
};

var CollectService_logMetric_args = function(args) {
  this.id = null;
  this.value = null;
  if (args) {
    if (args.id !== undefined) {
      this.id = args.id;
    }
    if (args.value !== undefined) {
      this.value = args.value;
    }
  }
};
CollectService_logMetric_args.prototype = {};
CollectService_logMetric_args.prototype.read = function(input) {
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
      if (ftype == Thrift.Type.STRUCT) {
        this.id = new ttypes.Identifier();
        this.id.read(input);
      } else {
        input.skip(ftype);
      }
      break;
      case 2:
      if (ftype == Thrift.Type.STRUCT) {
        this.value = new ttypes.MetricReading();
        this.value.read(input);
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

CollectService_logMetric_args.prototype.write = function(output) {
  output.writeStructBegin('CollectService_logMetric_args');
  if (this.id) {
    output.writeFieldBegin('id', Thrift.Type.STRUCT, 1);
    this.id.write(output);
    output.writeFieldEnd();
  }
  if (this.value) {
    output.writeFieldBegin('value', Thrift.Type.STRUCT, 2);
    this.value.write(output);
    output.writeFieldEnd();
  }
  output.writeFieldStop();
  output.writeStructEnd();
  return;
};

var CollectService_logMetric_result = function(args) {
};
CollectService_logMetric_result.prototype = {};
CollectService_logMetric_result.prototype.read = function(input) {
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
    input.skip(ftype);
    input.readFieldEnd();
  }
  input.readStructEnd();
  return;
};

CollectService_logMetric_result.prototype.write = function(output) {
  output.writeStructBegin('CollectService_logMetric_result');
  output.writeFieldStop();
  output.writeStructEnd();
  return;
};

var CollectService_logResults_args = function(args) {
  this.id = null;
  this.file = null;
  if (args) {
    if (args.id !== undefined) {
      this.id = args.id;
    }
    if (args.file !== undefined) {
      this.file = args.file;
    }
  }
};
CollectService_logResults_args.prototype = {};
CollectService_logResults_args.prototype.read = function(input) {
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
      if (ftype == Thrift.Type.STRUCT) {
        this.id = new ttypes.Identifier();
        this.id.read(input);
      } else {
        input.skip(ftype);
      }
      break;
      case 2:
      if (ftype == Thrift.Type.STRUCT) {
        this.file = new ttypes.File();
        this.file.read(input);
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

CollectService_logResults_args.prototype.write = function(output) {
  output.writeStructBegin('CollectService_logResults_args');
  if (this.id) {
    output.writeFieldBegin('id', Thrift.Type.STRUCT, 1);
    this.id.write(output);
    output.writeFieldEnd();
  }
  if (this.file) {
    output.writeFieldBegin('file', Thrift.Type.STRUCT, 2);
    this.file.write(output);
    output.writeFieldEnd();
  }
  output.writeFieldStop();
  output.writeStructEnd();
  return;
};

var CollectService_logResults_result = function(args) {
};
CollectService_logResults_result.prototype = {};
CollectService_logResults_result.prototype.read = function(input) {
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
    input.skip(ftype);
    input.readFieldEnd();
  }
  input.readStructEnd();
  return;
};

CollectService_logResults_result.prototype.write = function(output) {
  output.writeStructBegin('CollectService_logResults_result');
  output.writeFieldStop();
  output.writeStructEnd();
  return;
};

var CollectServiceClient = exports.Client = function(output, pClass) {
    this.output = output;
    this.pClass = pClass;
    this.seqid = 0;
    this._reqs = {};
};
CollectServiceClient.prototype = {};
CollectServiceClient.prototype.logMessage = function(id, message, callback) {
  this.seqid += 1;
  this._reqs[this.seqid] = callback;
  this.send_logMessage(id, message);
};

CollectServiceClient.prototype.send_logMessage = function(id, message) {
  var output = new this.pClass(this.output);
  output.writeMessageBegin('logMessage', Thrift.MessageType.CALL, this.seqid);
  var args = new CollectService_logMessage_args();
  args.id = id;
  args.message = message;
  args.write(output);
  output.writeMessageEnd();
  return this.output.flush();
};

CollectServiceClient.prototype.recv_logMessage = function(input,mtype,rseqid) {
  var callback = this._reqs[rseqid] || function() {};
  delete this._reqs[rseqid];
  if (mtype == Thrift.MessageType.EXCEPTION) {
    var x = new Thrift.TApplicationException();
    x.read(input);
    input.readMessageEnd();
    return callback(x);
  }
  var result = new CollectService_logMessage_result();
  result.read(input);
  input.readMessageEnd();

  callback(null)
};
CollectServiceClient.prototype.logMetric = function(id, value, callback) {
  this.seqid += 1;
  this._reqs[this.seqid] = callback;
  this.send_logMetric(id, value);
};

CollectServiceClient.prototype.send_logMetric = function(id, value) {
  var output = new this.pClass(this.output);
  output.writeMessageBegin('logMetric', Thrift.MessageType.CALL, this.seqid);
  var args = new CollectService_logMetric_args();
  args.id = id;
  args.value = value;
  args.write(output);
  output.writeMessageEnd();
  return this.output.flush();
};

CollectServiceClient.prototype.recv_logMetric = function(input,mtype,rseqid) {
  var callback = this._reqs[rseqid] || function() {};
  delete this._reqs[rseqid];
  if (mtype == Thrift.MessageType.EXCEPTION) {
    var x = new Thrift.TApplicationException();
    x.read(input);
    input.readMessageEnd();
    return callback(x);
  }
  var result = new CollectService_logMetric_result();
  result.read(input);
  input.readMessageEnd();

  callback(null)
};
CollectServiceClient.prototype.logResults = function(id, file, callback) {
  this.seqid += 1;
  this._reqs[this.seqid] = callback;
  this.send_logResults(id, file);
};

CollectServiceClient.prototype.send_logResults = function(id, file) {
  var output = new this.pClass(this.output);
  output.writeMessageBegin('logResults', Thrift.MessageType.CALL, this.seqid);
  var args = new CollectService_logResults_args();
  args.id = id;
  args.file = file;
  args.write(output);
  output.writeMessageEnd();
  return this.output.flush();
};

CollectServiceClient.prototype.recv_logResults = function(input,mtype,rseqid) {
  var callback = this._reqs[rseqid] || function() {};
  delete this._reqs[rseqid];
  if (mtype == Thrift.MessageType.EXCEPTION) {
    var x = new Thrift.TApplicationException();
    x.read(input);
    input.readMessageEnd();
    return callback(x);
  }
  var result = new CollectService_logResults_result();
  result.read(input);
  input.readMessageEnd();

  callback(null)
};
var CollectServiceProcessor = exports.Processor = function(handler) {
  this._handler = handler
}
CollectServiceProcessor.prototype.process = function(input, output) {
  var r = input.readMessageBegin();
  if (this['process_' + r.fname]) {
    return this['process_' + r.fname].call(this, r.rseqid, input, output);
  } else {
    input.skip(Thrift.Type.STRUCT);
    input.readMessageEnd();
    var x = new Thrift.TApplicationException(Thrift.TApplicationExceptionType.UNKNOWN_METHOD, 'Unknown function ' + r.fname);
    output.writeMessageBegin(r.fname, Thrift.MessageType.Exception, r.rseqid);
    x.write(output);
    output.writeMessageEnd();
    output.flush();
  }
}

CollectServiceProcessor.prototype.process_logMessage = function(seqid, input, output) {
  var args = new CollectService_logMessage_args();
  args.read(input);
  input.readMessageEnd();
  var result = new CollectService_logMessage_result();
  this._handler.logMessage(args.id, args.message, function (success) {
    result.success = success;
    output.writeMessageBegin("logMessage", Thrift.MessageType.REPLY, seqid);
    result.write(output);
    output.writeMessageEnd();
    output.flush();
  })
}

CollectServiceProcessor.prototype.process_logMetric = function(seqid, input, output) {
  var args = new CollectService_logMetric_args();
  args.read(input);
  input.readMessageEnd();
  var result = new CollectService_logMetric_result();
  this._handler.logMetric(args.id, args.value, function (success) {
    result.success = success;
    output.writeMessageBegin("logMetric", Thrift.MessageType.REPLY, seqid);
    result.write(output);
    output.writeMessageEnd();
    output.flush();
  })
}

CollectServiceProcessor.prototype.process_logResults = function(seqid, input, output) {
  var args = new CollectService_logResults_args();
  args.read(input);
  input.readMessageEnd();
  var result = new CollectService_logResults_result();
  this._handler.logResults(args.id, args.file, function (success) {
    result.success = success;
    output.writeMessageBegin("logResults", Thrift.MessageType.REPLY, seqid);
    result.write(output);
    output.writeMessageEnd();
    output.flush();
  })
}


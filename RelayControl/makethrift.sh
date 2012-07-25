#!/bin/bash
thrift -out . --gen py:twisted ../Thrift/relay.thrift
thrift -out . --gen py:twisted ../Thrift/rain.thrift
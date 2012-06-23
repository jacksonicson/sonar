#!/bin/bash
thrift -out ../generated --gen java ../../Thrift/collector.thrift
thrift -out ../generated --gen java timeseries.thrift
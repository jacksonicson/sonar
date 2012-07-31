# YUM dependencies
yum install python python-devel
yum install ntp
yum group install "Development Tools"
yum install unzip
yum install twisted
yum install python-setuptools 

# Copy relay to opt dir
mkdir /opt/relay
cp -f relay.zip /opt/relay

# Install Thrift
cd ../thrift-0.8.0/lib/py
python setup.py install

cd ../zope.interface-4.0.1
python setup.py install

# TARGET DIR
cd /opt/relay
rm -rf *
unzip relay.zip

# Install Systemd service
cp /opt/relay/relay.service /etc/systemd/system
systemctl enable relay.service
systemctl start relay.service
systemctl status relay.service


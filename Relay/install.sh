# Relay installation script
# Downloads all dependencies, installs Relay in the /opt directory and activates the Relay service (sytemd) 

# YUM dependencies
yum install python python-devel
yum install ntp
# Was required for building zop interface, which is now used from yum
# yum group install "Development Tools"
yum install unzip
yum install twisted
yum install python-setuptools
yum install python-zope-interface 
yum install thrift

# Copy relay to opt dir
rm -rf /opt/relay
mkdir /opt/relay
cp -f relay.zip /opt/relay

# Install Thrift
cd ../thrift-0.8.0/lib/py
python setup.py install

# Is now installed by yum
#cd ../zope.interface-4.0.1
# python setup.py install

# TARGET DIR
cd /opt/relay
unzip relay.zip

# Install Systemd service
cp /opt/relay/relay.service /etc/systemd/system
systemctl enable relay.service
systemctl start relay.service
systemctl status relay.service


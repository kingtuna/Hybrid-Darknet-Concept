####################################################
####                                            ####
#### Ubuntu 14.04LTS Honeypot Install Script    ####
#### Updated for 14.04 by Zane Witherspoon      ####
#### tuna@people.ops-trust.net                  ####
####                                            ####
####################################################

apt-get update
apt-get -y install gcc build-essential bind9 dnsutils cmake make gcc g++ flex bison
apt-get -y install libpcap-dev libgeoip-dev libssl-dev python-dev zlib1g-dev libmagic-dev 
apt-get -y install hping3 vim ntp xinetd curl default-jre git rubygems swig2.0 
mkdir build
cd build

###### setup hostname ######

OLDHOSTNAME=`cat /etc/hostname`
echo honey-pasv-`/sbin/ifconfig eth0 | grep 'inet addr:' | cut -d: -f2 | awk '{ print $1}'`> /etc/hostname
NEWHOSTNAME=`cat /etc/hostname`
hostname $NEWHOSTNAME

cat /etc/hosts | sed  s/$OLDHOSTNAME/$NEWHOSTNAME/g > /tmp/hosts
mv -f /tmp/hosts /etc/hosts
echo -e "127.0.0.1\t$NEWHOSTNAME" >> /etc/hosts


###### Install Bro ######
#
# apt-get install cmake make gcc g++ flex bison libpcap-dev 
# libgeoip-dev libssl-dev python-dev zlib1g-dev libmagic-dev swig2.0 -y

echo "Installing Bro"

wget http://geolite.maxmind.com/download/geoip/database/GeoLiteCity.dat.gz
wget http://geolite.maxmind.com/download/geoip/database/GeoLiteCityv6-beta/GeoLiteCityv6.dat.gz
gunzip GeoLiteCity.dat.gz
gunzip GeoLiteCityv6.dat.gz
mv GeoLiteCity.dat  /usr/share/GeoIP/GeoLiteCity.dat
mv GeoLiteCityv6.dat /usr/share/GeoIP/GeoLiteCityv6.dat
ln -s /usr/share/GeoIP/GeoLiteCity.dat /usr/share/GeoIP/GeoIPCity.dat
ln -s /usr/share/GeoIP/GeoLiteCityv6.dat /usr/share/GeoIP/GeoIPCityv6.dat
wget http://www.bro.org/downloads/release/bro-2.2.tar.gz
tar -xvzf bro-2.2.tar.gz
cd bro-2.2
./configure --prefix=/nsm/bro
make
make install

# this is an NTP script for bro to understand the protocol
curl https://raw.githubusercontent.com/kingtuna/logstash-ubuntu-misc/master/ntp.bro > /nsm/bro/share/bro/site/ntp.bro

echo '#add NTP suport
@load ntp' >> /nsm/bro/share/bro/site/local.bro

export PATH=/nsm/bro/bin:$PATH
/nsm/bro/bin/broctl install
/nsm/bro/bin/broctl start

cd /root/build/

###### logstash ######

gem install fpm

git clone https://github.com/Yuav/logstash-packaging.git --depth=1
cd logstash-packaging
./package.sh

cd ..
dpkg -i logstash_1.*.deb
/etc/init.d/logstash start

## clear out previous logstash configs
rm -f /etc/logstash/*

#http://www.appliednsm.com/parsing-bro-logs-with-logstash/
curl https://raw.githubusercontent.com/kingtuna/logstash-ubuntu-misc/master/logstash-bro-passive.conf > /etc/logstash/bro.conf

printf 'output {
  rabbitmq {
     user => "USERNAME"
     exchange_type => "direct"
     password => "PASSWORD"
     exchange => "amq"
     vhost => "/amp"
     durable => false
     ssl => true
     port => 5671
     persistent => false
     host => "RABBITMQ-IP"
  }
}' >> /etc/logstash/bro.conf

curl https://raw.githubusercontent.com/kingtuna/logstash-ubuntu-misc/master/upstart.logstash.conf > /etc/init/logstash.conf

cd /root/build/


###### Clean Ups and Cron ######

echo '
export PATH=/nsm/bro/bin:$PATH
/nsm/bro/bin/broctl install
/nsm/bro/bin/broctl start
sleep 2
service logstash restart

exit 0
' > /etc/rc.local 



##### crontab to install
##start logstash and bro

printf '0-59/5 * * * * /nsm/bro/bin/broctl cron
' > crontab.txt
crontab crontab.txt

echo "net.ipv4.tcp_keepalive_intvl=570" >> /etc/sysctl.conf

reboot

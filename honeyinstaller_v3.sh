####################################################
####                                            ####
#### Ubuntu 14.04LTS Honeypot Install Script    ####
#### Updated for 14.04 by Zane Witherspoon &    ####
#### tuna@people.ops-trust.net                  ####
####                                            ####
####################################################

apt-get update
apt-get -y install gcc build-essential bind9 dnsutils cmake make gcc g++ flex bison gcc
apt-get -y install libpcap-dev libgeoip-dev libssl-dev python-dev zlib1g-dev libmagic-dev 
apt-get -y install hping3 vim ntp xinetd curl default-jre git ruby swig2.0 ruby-dev
mkdir build
cd build

###### setup hostname ######

OLDHOSTNAME=`cat /etc/hostname`
echo honey-`/sbin/ifconfig eth0 | grep 'inet addr:' | cut -d: -f2 | awk '{ print $1}'`> /etc/hostname
NEWHOSTNAME=`cat /etc/hostname`
hostname $NEWHOSTNAME

cat /etc/hosts | sed  s/$OLDHOSTNAME/$NEWHOSTNAME/g > /tmp/hosts
mv -f /tmp/hosts /etc/hosts
echo -e "127.0.0.1\t$NEWHOSTNAME" >> /etc/hosts

###### Install NTP ######
mkdir build && cd build
wget http://www.eecis.udel.edu/~ntp/ntp_spool/ntp4/ntp-4.2/ntp-4.2.6p4.tar.gz
tar zxvf ntp-4.2.6p4.tar.gz
cd ntp-4.2.6p4/
./configure --enable-clockctl
make
make install
cd ..
echo "driftfile /var/lib/ntp/ntp.drift" > /etc/ntp.conf

echo "e30003fa000100000001000000000000000000000000000000000000000000000000000000000000d6a42558d961df90" > /root/ntp.bin
/usr/local/bin/ntpd -u ntp:ntp -p /var/run/ntpd.pid -g

echo '#!/bin/bash
killall ntpd
/usr/local/bin/ntpd -u ntp:ntp -p /var/run/ntpd.pid -g
killall sshpot
service sshpot restart
killall SSDP_Emulator
killall sentinel_emulator
/root/build/ssdp/SSDP_Emulator
/root/build/sentinel/sentinel_emulator
/usr/sbin/hping3 --rand-source -c 600 --udp -p 123 --fast -n 127.0.0.1 -d 48 -E /root/ntp.bin' > /root/killntp.sh 
chmod +x /root/killntp.sh 

hping3 --rand-source -c 600 --udp -p 123 --fast -n 127.0.0.1 -d 48 -E /root/ntp.bin


###### Install CHARGEN ######

echo 'service chargen
{
    disable = yes
    type = INTERNAL
    id = chargen-stream
    socket_type = stream
    protocol = tcp
    user = root
    wait = no
}                                                                               

# This is the udp version.
service chargen
{
    disable = no
    type = INTERNAL
    id = chargen-dgram
    socket_type = dgram
    protocol = udp
    user = root
    wait = yes
}' > /etc/xinetd.d/chargen 

service xinetd restart

###### Install SSDP Service Emulator ######
cd /root/build/
mkdir ssdp
cd /root/build/ssdp/
curl https://raw.githubusercontent.com/kingtuna/honeynet/master/emulators/SSDP_Emulator.c > SSDP_Emulator.c
gcc SSDP_Emulator.c -o SSDP_Emulator
/root/build/ssdp/SSDP_Emulator

###### Install sentinel Service Emulator ######
cd /root/build/
mkdir sentinel
cd /root/build/sentinel/
curl https://raw.githubusercontent.com/kingtuna/honeynet/master/emulators/sentinel_emulator.c > sentinel_emulator.c
gcc sentinel_emulator.c -o sentinel_emulator
/root/build/sentinel/sentinel_emulator

###### Install Recursive DNS ######

apt-get install bind9 dnsutils -y


echo 'include "/etc/bind/named.conf.options";
include "/etc/bind/named.conf.local";
include "/etc/bind/rndc.key";
# make it comment
# include "/etc/bind/named.conf.default-zones";
# add
include "/etc/bind/named.conf.internal-zones";
include "/etc/bind/named.conf.external-zones";' > /etc/bind/named.conf

echo '# define for internal section
view "internal" {
        match-clients {
                localhost;
                10.0.0.0/24;
        };
        zone "." {
                type hint;
                file "db.root";
        };
# set zone for internal
        zone "server.world" {
                type master;
                file "server.world.lan";
                allow-update { none; };
        };
# set zone for internal *note
        zone "0.0.10.in-addr.arpa" {
                type master;
                file "0.0.10.db";
                allow-update { none; };
        };
        zone "localhost" {
                type master;
                file "db.local";
        };
        zone "127.in-addr.arpa" {
                type master;
                file "db.127";
        };
        zone "0.in-addr.arpa" {
                type master;
                file "db.0";
        };
        zone "255.in-addr.arpa" {
                type master;
                file "db.255";
        };
};' > /etc/bind/named.conf.internal-zones

echo '# define for external section
view "external" {
        match-clients { any; };
# allo any query
        allow-query { any; };
# prohibit recursion
        recursion yes;
# set zone for external
        zone "server.world" {
                type master;
                file "server.world.wan";
                allow-update { none; };
        };
# set zone for external *note
        zone "80.0.16.172.in-addr.arpa" {
                type master;
                file "80.0.16.172.db";
                allow-update { none; };
        };
};' > /etc/bind/named.conf.external-zones

rndc-confgen | head -n5 > /etc/bind/rndc.key

echo 'options {
# change
directory "/etc/bind";
# query range you allow
version "eatdix";
allow-query {any;};
# the range to transfer zone files
allow-transfer {any;};
# recursion range you allow
allow-recursion {any;};
dnssec-validation auto;
auth-nxdomain no;
};' > /etc/bind/named.conf.options

service bind9 restart

###### Install Bro ######
#
# apt-get install cmake make gcc g++ flex bison libpcap-dev 
# libgeoip-dev libssl-dev python-dev zlib1g-dev libmagic-dev swig2.0 -y
#
# Javier this breaks a lot if bro doesn't get installed this is probabbly why

wget http://geolite.maxmind.com/download/geoip/database/GeoLiteCity.dat.gz
wget http://geolite.maxmind.com/download/geoip/database/GeoLiteCityv6-beta/GeoLiteCityv6.dat.gz
gunzip GeoLiteCity.dat.gz
gunzip GeoLiteCityv6.dat.gz
mv GeoLiteCity.dat  /usr/share/GeoIP/GeoLiteCity.dat
mv GeoLiteCityv6.dat /usr/share/GeoIP/GeoLiteCityv6.dat
ln -s /usr/share/GeoIP/GeoLiteCity.dat /usr/share/GeoIP/GeoIPCity.dat
ln -s /usr/share/GeoIP/GeoLiteCityv6.dat /usr/share/GeoIP/GeoIPCityv6.dat
wget `curl https://www.bro.org/download/index.html | grep "gz" | grep "bro-" | grep -v aux | grep -v asc | cut -d'"' -f2`
tar -xvzf bro-2.*.tar.gz
cd bro-2.*
./configure --prefix=/nsm/bro
make
make install

# this is an NTP script for bro to understand the protocol
printf 'bW9kdWxlIE5UUDsKCmV4cG9ydCB7CglyZWRlZiBlbnVtIExvZzo6SUQgKz0geyBMT0cgfTsKCgly
ZWRlZiBlbnVtIE5vdGljZTo6VHlwZSArPSB7CgkJTlRQX0FsYXJtLAoJCU5UUF9Nb25saXN0X1F1
ZXJpZXMsCgkJfTsKCgl0eXBlIG50cF9yZWNvcmQ6IHJlY29yZCB7CgkJdHM6IHRpbWUgJmxvZzsK
CQl1aWQ6IHN0cmluZyAmbG9nOwoJCW9yaWc6IGFkZHIgJmxvZzsKCQlyZXNwOiBhZGRyICZsb2c7
CgkJcmVmaWQ6IGNvdW50ICZkZWZhdWx0PTAgJmxvZzsKCQljb2RlOiBjb3VudCAmZGVmYXVsdD0w
ICZsb2c7CgkJc3RyYXR1bTogY291bnQgJmRlZmF1bHQ9MCAmbG9nOwoJCXBvbGw6IGNvdW50ICZk
ZWZhdWx0PTAgJmxvZzsKCQlwcmVjaXNpb246IGludCAmZGVmYXVsdD10b19pbnQoIjAiKSAmbG9n
OwoJCSNkaXN0YW5jZTogaW50ZXJ2YWw7CgkJI2Rpc3BlcnNpb246IGludGVydmFsOwoJCXJlZnRp
bWU6IHRpbWUgJmxvZzsKCQkjb3JpZzogdGltZTsKCQkjcmVjOiB0aW1lOwoJCSN4bXQ6IHRpbWU7
CgkJZXhjZXNzOiBzdHJpbmcgJmRlZmF1bHQ9Ik5VTEwiICZsb2c7CgkJfTsKCgkjIFRoZSBjb2Rl
IHZhbHVlIG1hcHMgdG8gdGhlIE5UUCBtb2RlIHR5cGUgLSBmb3Igbm93IEkgYW0gbW9zdGx5Cgkj
ICBpbnRlcmVzdGVkIGluIGNvbnRyb2wgbWVzc2FnZXMuCgkjCgkjIE1vZGUJRGVzY3JpcHRpb24K
CSMgMAlyZXNlcnZlZC4KCSMgMQlTeW1tZXRyaWMgYWN0aXZlLgoJIyAyCVN5bW1ldHJpYyBwYXNz
aXZlLgoJIyAzCUNsaWVudC4KCSMgNAlTZXJ2ZXIuCgkjIDUJQnJvYWRjYXN0LgoJIyA2CU5UUCBj
b250cm9sIG1lc3NhZ2UuCgkjIDcJcHJpdmF0ZSB1c2UuCgljb25zdCBOVFBfUkVTRVJWRUQgPSAw
OwoJY29uc3QgTlRQX1NZTV9BQ1RJVkUgPSAxOwoJY29uc3QgTlRQX1NZTV9QQVNTSVZFID0gMjsK
CWNvbnN0IE5UUF9DTElFTlQgPSAzOwoJY29uc3QgTlRQX1NFUlZFUiA9IDQ7Cgljb25zdCBOVFBf
QlJPQURDQVNUID0gNTsKCWNvbnN0IE5UUF9DT05UUk9MID0gNjsKCWNvbnN0IE5UUF9QUklWQVRF
ID0gNzsKCgljb25zdCBwb3J0cyA9IHsgMTIzL3VkcCx9OwoJcmVkZWYgbGlrZWx5X3NlcnZlcl9w
b3J0cyArPSB7IHBvcnRzIH07CgoJY29uc3QgbG9nX29ubHlfY29udHJvbDogYm9vbCA9IEYgJnJl
ZGVmOwoKCSMgU28gd2UgZG9uJ3Qgd2FybiBtb3JlIHRoYW4gb25lIHRpbWUKCWdsb2JhbCBudHBf
aG9zdDogdGFibGVbYWRkcl0gb2YgY291bnQ7CgoJfSAjIGVuZCBleHBvcnQKCgpldmVudCBudHBf
bWVzc2FnZShjOiBjb25uZWN0aW9uLCBtc2c6IG50cF9tc2csIGV4Y2Vzczogc3RyaW5nKQoJewoJ
IyB3ZSBhcmUgaGFuZGVkIGEgbnRwX21zZyB0eXBlIHdoaWNoIGlzIHNsaWdodGx5IGRpZmZlcmVu
dCB0aGFuIHRoZQoJIyAgbnRwX3JlY29yZCB1c2VkIGZvciBkZWFsaW5nIHdpdGggdGhlIHBvbGlj
eSBzaWRlIG9mIHRoaW5ncy4KCglpZiAoIGxvZ19vbmx5X2NvbnRyb2wgJiYgKChtc2ckY29kZSAh
PSBOVFBfQ09OVFJPTCkgfHwgKG1zZyRjb2RlICE9IE5UUF9QUklWQVRFKSkgKQoJCXJldHVybjsK
Cglsb2NhbCB0X3JlYzogbnRwX3JlY29yZDsKCgl0X3JlYyRvcmlnID0gYyRpZCRvcmlnX2g7Cgl0
X3JlYyRyZXNwID0gYyRpZCRyZXNwX2g7Cgl0X3JlYyR1aWQgPSBjJHVpZDsKCXRfcmVjJHRzID0g
YyRzdGFydF90aW1lOwoKCWlmICggbXNnPyRpZCApCgkJdF9yZWMkcmVmaWQgPSBtc2ckaWQ7CgoJ
aWYgKCBtc2c/JGNvZGUgKQoJCXRfcmVjJGNvZGUgPSBtc2ckY29kZTsKCglpZiAoIG1zZz8kc3Ry
YXR1bSApCgkJdF9yZWMkc3RyYXR1bSA9IG1zZyRzdHJhdHVtOwoKCWlmICggbXNnPyRwb2xsICkK
CQl0X3JlYyRwb2xsID0gbXNnJHBvbGw7CgoJaWYgKCBtc2c/JHByZWNpc2lvbiApCgkJdF9yZWMk
cHJlY2lzaW9uID0gbXNnJHByZWNpc2lvbjsKCgkjaWYgKCBtc2c/JHJlZl90ICkKCQkjdF9yZWMk
cmVmdGltZSA9IG1zZyRyZWZfdDsKCgkjdF9yZWMkZXhjZXNzID0gZXhjZXNzOwoKCWlmICgobXNn
JGNvZGUgPT0gTlRQX1BSSVZBVEUpIHx8IChtc2ckY29kZSA9PSBOVFBfQ09OVFJPTCkpIHsKCgkJ
aWYgKCBjJGlkJG9yaWdfaCAhaW4gbnRwX2hvc3QgKSB7CgoJCQlOT1RJQ0UoWyRub3RlPU5UUDo6
TlRQX01vbmxpc3RfUXVlcmllcywKCQkJCSRjb25uPWMsCgkJCQkkc3VwcHJlc3NfZm9yPTZocnMs
CgkJCQkkbXNnPWZtdCgiTlRQIG1vbmxpc3QgcXVlcmllcyIpLAoJCQkJJGlkZW50aWZpZXI9Y2F0
KGMkaWQkb3JpZ19oKV0pOwoJCQl9CgkJZWxzZQoJCQkrK250cF9ob3N0W2MkaWQkb3JpZ19oXTsK
CgkJfQoKCUxvZzo6d3JpdGUoTE9HLCB0X3JlYyk7Cgl9CgpldmVudCBicm9faW5pdCgpICZwcmlv
cml0eT01CiAgICAgICAgewogICAgICAgIExvZzo6Y3JlYXRlX3N0cmVhbShOVFA6OkxPRywgWyRj
b2x1bW5zPW50cF9yZWNvcmRdKTsKICAgICAgICBBbmFseXplcjo6cmVnaXN0ZXJfZm9yX3BvcnRz
KEFuYWx5emVyOjpBTkFMWVpFUl9OVFAsIHBvcnRzKTsKICAgICAgICB9Cg==' | base64 -d > /nsm/bro/share/bro/site/ntp.bro

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
printf 'IyBDcmVhdGVkIGJ5IFRlcnJlbmNlIEdhcmVhdSAidHVuYSIgZm9yIGhvbmV5cG90IHByb2plY3QK
IyB0dW5hQHBlb3BsZS5vcHMtdHJ1c3QubmV0CgojIFVzZWQgSmFzb24gU21pdGgncyBzZXR1cCBh
cyBhIGJhc2UKIyBHcmVhdCBCbG9nIHBvc3QgaHR0cDovL3d3dy5hcHBsaWVkbnNtLmNvbS9wYXJz
aW5nLWJyby1sb2dzLXdpdGgtbG9nc3Rhc2gvCiMgaHR0cDovL2Jsb2cubHVzaXMub3JnL2Jsb2cv
MjAxMi8wMS8zMS9sb2FkLWJhbGFuY2luZy1sb2dzdGFzaC13aXRoLWFtcXAvCiMgdHVuYUBwZW9w
bGUub3BzLXRydXN0Lm5ldAojIGh0dHBzOi8vaG9tZS5yZWdpdC5vcmcvMjAxNC8wMS9hLWJpdC1v
Zi1sb2dzdGFzaC1jb29raW5nLyBnZW9pcAojIGh0dHBzOi8vaG9tZS5yZWdpdC5vcmcvdGFnL2xv
Z3N0YXNoLwojTG9ncyBiZWluZyBwYXJzZWQ6CiNjb25uLmxvZwojZG5zLmxvZwojbnRwLmxvZwoK
aW5wdXQgewoKI1Byb2R1Y3Rpb24gTG9ncyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjCiAg
ZmlsZSB7CiAgICB0eXBlID0+ICJCUk9fY29ubmxvZyIKICAgIHBhdGggPT4gIi9uc20vYnJvL2xv
Z3MvY3VycmVudC9jb25uLmxvZyIKICB9CiAgZmlsZSB7CiAgICB0eXBlID0+ICJCUk9fZG5zbG9n
IgogICAgcGF0aCA9PiAiL25zbS9icm8vbG9ncy9jdXJyZW50L2Rucy5sb2ciCiAgfQoKICBmaWxl
IHsKICAgIHR5cGUgPT4gIkJST19udHBsb2ciCiAgICBwYXRoID0+ICIvbnNtL2Jyby9sb2dzL2N1
cnJlbnQvbnRwLmxvZyIKICB9CgogIGZpbGUgewogICAgdHlwZSA9PiAiU1NIUE9UX3NzaGxvZyIK
ICAgIHBhdGggPT4gIi92YXIvbG9nL3NzaHBvdF9hdXRoLmxvZyIKICB9CgojIyMjIyMjIyMjIyMj
IyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMKfQoKZmlsdGVyIHsKICBpZiBb
bWVzc2FnZV0gPX4gL14jLyB7CiAgICBkcm9wIHsgIH0KICB9IGVsc2UgewoKIyBTU0hQT1Rfc3No
bG9nICMjIyMjIyMjIyMjIyMjIyMjIyMjIyMKICBpZiBbdHlwZV0gPT0gIlNTSFBPVF9zc2hsb2ci
IHsKICAgICAgZ3JvayB7CiAgICAgICAgbWF0Y2ggPT4gWyAibWVzc2FnZSIsICIoPzx0cz4oLio/
KSlcdCg/PGlkLm9yaWdfaD4oLio/KSlcdCg/PHVzZXI+KC4qPykpXHQoPzxwYXNzPiguKj8pKVx0
IiBdCiAgICAgIH0KICB9CgojIEJST19udHBsb2cgIyMjIyMjIyMjIyMjIyMjIyMjIyMjIwogIGlm
IFt0eXBlXSA9PSAiQlJPX250cGxvZyIgewogICAgICBncm9rIHsKICAgICAgICBtYXRjaCA9PiBb
ICJtZXNzYWdlIiwgIig/PHRzPiguKj8pKVx0KD88dWlkPiguKj8pKVx0KD88aWQub3JpZ19oPigu
Kj8pKVx0KD88aWQucmVzcF9oPiguKj8pKVx0KD88cmVmaWQ+KC4qPykpXHQoPzxjb2RlPiguKj8p
KVx0KD88c3RyYXR1bT4oLio/KSlcdCg/PHBvbGw+KC4qPykpXHQoPzxwcmVjZWlzc2lvbj4oLio/
KSlcdCg/PHJlZnRpbWU+KC4qPykpXHQoPzxleGNlc3M+KC4qPykpIiBdCiAgICAgIH0KICAgICAg
aWYgW2NvZGVdID1+IC9eNC8gewogICAgICAgIGRyb3AgeyAgfQogICAgICAgfQogIH0KCiMgQlJP
X2Ruc2xvZyAjIyMjIyMjIyMjIyMjIyMjIyMjIyMjCiAgaWYgW3R5cGVdID09ICJCUk9fZG5zbG9n
IiB7CiAgICBncm9rIHsKbWF0Y2ggPT4gWyAibWVzc2FnZSIsICIoPzx0cz4oLio/KSlcdCg/PHVp
ZD4oLio/KSlcdCg/PGlkLm9yaWdfaD4oLio/KSlcdCg/PGlkLm9yaWdfcD4oLio/KSlcdCg/PGlk
LnJlc3BfaD4oLio/KSlcdCg/PGlkLnJlc3BfcD4oLio/KSlcdCg/PHByb3RvPiguKj8pKVx0KD88
dHJhbnNfaWQ+KC4qPykpXHQoPzxxdWVyeT4oLio/KSlcdCg/PHFjbGFzcz4oLio/KSlcdCg/PHFj
bGFzc19uYW1lPiguKj8pKVx0KD88cXR5cGU+KC4qPykpXHQoPzxxdHlwZV9uYW1lPiguKj8pKVx0
KD88cmNvZGU+KC4qPykpXHQoPzxyY29kZV9uYW1lPiguKj8pKVx0KD88QUE+KC4qPykpXHQoPzxU
Qz4oLio/KSlcdCg/PFJEPiguKj8pKVx0KD88UkE+KC4qPykpXHQoPzxaPiguKj8pKVx0KD88YW5z
d2Vycz4oLio/KSlcdCg/PFRUTHM+KC4qPykpXHQoPzxyZWplY3RlZD4oLiopKSIgXQpyZW1vdmVf
ZmllbGQgPT4gWyAiYW5zd2VycyIgXQogIH0KfQoKIyBCUk9fY29ubmxvZyAjIyMjIyMjIyMjIyMj
IyMjIyMjIyMjCiAgaWYgW3R5cGVdID09ICJCUk9fY29ubmxvZyIgewogICAgZ3JvayB7Cm1hdGNo
ID0+IFsgIm1lc3NhZ2UiLCAiKD88dHM+KC4qPykpXHQoPzx1aWQ+KC4qPykpXHQoPzxpZC5vcmln
X2g+KC4qPykpXHQoPzxpZC5vcmlnX3A+KC4qPykpXHQoPzxpZC5yZXNwX2g+KC4qPykpXHQoPzxp
ZC5yZXNwX3A+KC4qPykpXHQoPzxwcm90bz4oLio/KSlcdCg/PHNlcnZpY2U+KC4qPykpXHQoPzxk
dXJhdGlvbj4oLio/KSlcdCg/PG9yaWdfYnl0ZXM+KC4qPykpXHQoPzxyZXNwX2J5dGVzPiguKj8p
KVx0KD88Y29ubl9zdGF0ZT4oLio/KSlcdCg/PGxvY2FsX29yaWc+KC4qPykpXHQoPzxtaXNzZWRf
Ynl0ZXM+KC4qPykpXHQoPzxoaXN0b3J5PiguKj8pKVx0KD88b3JpZ19wa3RzPiguKj8pKVx0KD88
b3JpZ19pcF9ieXRlcz4oLio/KSlcdCg/PHJlc3BfcGt0cz4oLio/KSlcdCg/PHJlc3BfaXBfYnl0
ZXM+KC4qPykpXHQoPzx0dW5uZWxfcGFyZW50cz4oLio/KSkiIF0KICAgIH0KICB9CiB9CiAgaWYg
W2lkLm9yaWdfaF0gIHsKICAgIGdlb2lwIHsKICAgICAgc291cmNlID0+ICJpZC5vcmlnX2giCiAg
ICAgIHRhcmdldCA9PiAiZ2VvaXAiCiAgICAgIGFkZF9maWVsZCA9PiBbICJbZ2VvaXBdW2Nvb3Jk
aW5hdGVzXSIsICIle1tnZW9pcF1bbG9uZ2l0dWRlXX0iIF0KICAgICAgYWRkX2ZpZWxkID0+IFsg
IltnZW9pcF1bY29vcmRpbmF0ZXNdIiwgIiV7W2dlb2lwXVtsYXRpdHVkZV19IiAgXQogICAgfQog
ICAgbXV0YXRlIHsKICAgICAgY29udmVydCA9PiBbICJbZ2VvaXBdW2Nvb3JkaW5hdGVzXSIsICJm
bG9hdCIgXQogICAgfQogICAgbXV0YXRlIHsKICAgICAgdXBwZXJjYXNlID0+IFsgImdlb2lwLmNv
dW50cnlfY29kZTIiIF0KICAgIH0KICB9Cn0K' | base64 -d  > /etc/logstash/bro.conf

printf 'output {
  rabbitmq {
     user => "USER"
     exchange_type => "direct"
     password => "PASSWORD"
     exchange => "amq.direct"
     vhost => "/amp"
     durable => true
     ssl => true
     port => 5671
     persistent => true
     host => "hose_ip"
  }
}' >> /etc/logstash/bro.conf

curl https://raw.githubusercontent.com/kingtuna/logstash-ubuntu-misc/master/upstart.logstash.conf > /etc/init/logstash.conf

cd /root/build/

###### Setup SSH Honeypot ######

apt-get install libssh-dev -y
git clone https://github.com/kingtuna/sshpot.git
cd sshpot
make
mv /etc/ssh/sshd_config /etc/ssh/sshd_config.old
cat /etc/ssh/sshd_config.old | sed 's/Port 22$/Port 2222/g' > /etc/ssh/sshd_config
cp upstart.sshpot.conf /etc/init/sshpot.conf
cp sshpot /usr/local/bin/
touch cat /var/log/sshpot_auth.log
service ssh restart
service sshpot start
cd /root/build/

##
# Added in killntp.sh script
# killall sshpot
# service sshpot restart 
##

###### Clean Ups and Cron ######

echo '
/usr/local/bin/ntpd -u ntp:ntp -p /var/run/ntpd.pid -g
export PATH=/nsm/bro/bin:$PATH
/nsm/bro/bin/broctl install
/nsm/bro/bin/broctl start
sleep 2
hping3 --rand-source -c 600 --udp -p 123 --fast -n 127.0.0.1 -d 48 -E /root/ntp.bin
service logstash restart
killall sentinel_emulator
killall SSDP_Emulator
/root/build/ssdp/SSDP_Emulator
/root/build/sentinel/sentinel_emulator

exit 0
' > /etc/rc.local 



##### crontab to install
##start logstash and bro

printf '*/30 * * * * service bind9 restart
*/30 * * * * /etc/init.d/xinetd restart
* */2 * * * /root/killntp.sh
0-59/5 * * * * /nsm/bro/bin/broctl cron
' > crontab.txt
crontab crontab.txt

echo "net.ipv4.tcp_keepalive_intvl=570" >> /etc/sysctl.conf
reboot

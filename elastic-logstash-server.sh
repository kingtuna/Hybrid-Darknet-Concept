###### Install Elastic and logstash ######

apt-get install default-jre -y
wget https://download.elasticsearch.org/elasticsearch/elasticsearch/elasticsearch-1.1.0.deb
dpkg -i elasticsearch-1.1.0.deb
update-rc.d elasticsearch defaults
apt-get install -f

apt-get install git rubygems -y
gem install fpm

git clone https://github.com/Yuav/logstash-packaging.git --depth=1
cd logstash-packaging
./package.sh

cd ..
dpkg -i logstash_1.*.deb
/etc/init.d/elasticsearch start
update-rc.d logstash defaults
/etc/init.d/logstash start

###### Install LAMP ######

apt-get install tasksel
tasksel install lamp-server

cd /var/wwww/
git clone https://github.com/elasticsearch/kibana.git

/usr/share/elasticsearch/bin/plugin -install royrusso/elasticsearch-HQ

echo "
input {
rabbitmq {
   user => "USERNAME"
   password => "PASSWORD"
   exchange => "amq.direct"
   vhost => "/amp"
   host => "RABBITMQ-IP"
   durable => false
   exclusive => false
   type => "logstash-indexer-input"
        }
}

output {
  elasticsearch_http {
        host => "localhost"
  }
}
" > '/Users/zane/Desktop/testing.txt'

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
                user => "user"
                threads => "4"
                password => "password"
                exchange => "amq.direct"
                queue => "logstash-queue"
                exclusive => false
                vhost => "/amp"
                host => "ipaddress"
                type => "logstash-indexer-input"
        }
}
filter{
        mutate{
                rename => {"[geoip][coordinates]" => "[geoip][location]"}
        }
}
output {
        elasticsearch {
                host => ["10.240.0.4","10.240.0.6","10.240.0.5","10.240.0.3"]
                sniffing => true
                cluster => "elastichoney-cluster"
                node_name => "the-qtip"
                workers => "4"
        }
}
" > '/etc/logstash/brotastic.conf'

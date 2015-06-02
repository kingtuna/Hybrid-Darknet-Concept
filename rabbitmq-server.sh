#############################

Rabbit


apt-get install -y vim git
echo "deb http://www.rabbitmq.com/debian/ testing main" >> /etc/apt/sources.list
wget http://www.rabbitmq.com/rabbitmq-signing-key-public.asc
apt-key add rabbitmq-signing-key-public.asc
apt-get update
apt-get install rabbitmq-server -y


git clone git://github.com/joemiller/joemiller.me-intro-to-sensu.git
cd joemiller.me-intro-to-sensu/
./ssl_certs.sh clean
./ssl_certs.sh generate

mkdir -p /etc/rabbitmq/ssl
cp server_key.pem /etc/rabbitmq/ssl/
cp server_cert.pem /etc/rabbitmq/ssl/
cp testca/cacert.pem /etc/rabbitmq/ssl/

########## /etc/rabbitmq/rabbitmq.config
[
    {rabbit, [
    {ssl_listeners, [5671]},
    {ssl_options, [{cacertfile,"/etc/rabbitmq/ssl/cacert.pem"},
                   {certfile,"/etc/rabbitmq/ssl/server_cert.pem"},
                   {keyfile,"/etc/rabbitmq/ssl/server_key.pem"},
                   {verify,verify_peer},
                   {fail_if_no_peer_cert,false}]}
  ]},
{rabbitmq_management,
  [{listener, [{port,     15672},
               {ssl,      true},
               {ssl_opts, [{cacertfile, "/etc/rabbitmq/ssl/cacert.pem"},
                           {certfile,   "/etc/rabbitmq/ssl/server_cert.pem"},
                           {keyfile,    "/etc/rabbitmq/ssl/server_key.pem"}]}
              ]}
  ]}
].


## http://sensuapp.org/docs/0.11/installing_rabbitmq_debian

/usr/lib/rabbitmq/bin/rabbitmq-plugins enable rabbitmq_management
update-rc.d rabbitmq-server defaults
/etc/init.d/rabbitmq-server restart

rabbitmqctl add_vhost /amp
rabbitmqctl add_user USERNAME PASSWORD

rabbitmqctl set_permissions -p /amp PASSWORD ".*" ".*" ".*"

rabbitmqctl add_user USERNAME-CTL PASSWORD-CTL
rabbitmqctl set_user_tags admin administrator
rabbitmqctl set_permissions -p / admin ".*" ".*" ".*"
rabbitmqctl delete_user guest
service rabbitmq-server restart


# Hybrid-Darknet-Concept

Founder
Terrence Gareau

Collaborators

Zane Witherspoon 
Achilleas Moustakis
Krassimir T. Tzvetanov
Javier Prats

Project Sponsors
A10
Nexusguard
Cari.net

Requirements
Ubuntu 14.04 LTS

According to the diagram, it takes at least 3 machines to build the honeynet: 
the rabbitMQ data broker, 
the logstash/elasticsearch servers,
and finally the honeypot itself

Given that they all need the IP for the rabbitMQ to set up elasticsearch configurations, let's start with the rabbitMQ server.


#### rabbitMQ ####
On a ubuntu 14.04 machine, run rabbitmq-server.sh 
It's recommended that you change USERNAME and PASSWORD to your appropriate credentials
You should also change USERNAME-CTL and PASSWORD_CTL to your web client login credentials
The web client is at RABBIT-IP:15672
For the rest of the configurations, life will be much easier if the IP for rabbitMQ is static.

#### elasticsearch/logstash ####
Change the USERNAME and PASSWORD to match the ones in the rabbitMQ server.
Change RABBITMQ-IP to the internal IP for the rabbitMQ server.

#### honeypot ####
The honeyinstaller_v3.sh is the recommended script to set up the honeypot.
Change the USERNAME and PASSWORD to the same credentials as before
Change RABBIT-IP to the rabbitMQ internal IP

#### index template ####
You can define custom mappings for the indexes created by logstash.
Run index-template.sh on the elasticsearch/logstash server to set a custom mapping for the data parsed by logstash in all future auto-created indexes that start with logstash-*


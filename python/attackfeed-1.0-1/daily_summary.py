# DNS reports from es
# Zane Witherspoon
# 7 July 2015

# Attack object holds key information
class Attack:
    def __init__(self, ip, count, resp_p):
        self.ip = ip
        self.count = count
        self.resp_p = resp_p
        self.log = ''
        self.type = ''
        self.method = ''
        self.start_time = ''
        self.end_time = ''
        self.epoch_start = 0
        self.epoch_end = 0
        self.duration = 0
        self.qtype = {}
        self.query = {}
        self.ports = {}
        self.trans_id = ''
        self.country = ''
        self.region = ''
        self.asn = ''

###method used for general term searches##
def termSearch(field, order, searchSize, term):
    terms = es.search(
        index=indexName,
        body={
            'query': {
                'filtered': {
                    'filter': {
                        'bool': {
                            "must": [
                                {
                                    "fquery": {
                                        "query": {
                                            "query_string": {
                                                "query": term
                                            }
                                        }
                                    }
                                }
                            ]
                        }
                    }
                }
            },
            'facets': {
                'terms': {
                    'terms': {
                        'field': field,
                        'order': order,
                        'size': searchSize
                    }
                }
            }
        }
    )
    return terms

###method used for counting##
def portCount(term, ip, port):
    port = 'id.resp_p:' + str(port)
    terms = es.count(
        index=indexName,
        body={
            'query': {
                'filtered': {
                    'filter': {
                        'bool': {
                            "must": [
                                {
                                    "fquery": {
                                        "query": {
                                            "query_string": {
                                                "query": term
                                            }
                                        }
                                    }
                                },
                                {
                                    "fquery": {
                                        "query": {
                                            "query_string": {
                                                "query": ip
                                            }
                                        }
                                    }
                                },
                                {
                                    "fquery": {
                                        "query": {
                                            "query_string": {
                                                "query": port
                                            }
                                        }
                                    }
                                }
                            ]
                        }
                    }
                }
            }
            
        }
    )
    return terms

###method used for ip term searches##
def ipTermSearch(field, order, searchSize, ip, query):
    ipTerms = es.search(
        index=indexName,
        body={
            'size': 0,
            'query': {
                'filtered': {
                    'filter': {
                        'bool': {
                            "must": [
                                {
                                    "fquery": {
                                        "query": {
                                            "query_string": {
                                                "query": query
                                            }
                                        }
                                    }
                                },
                                {
                                    "fquery": {
                                        "query": {
                                            "query_string": {
                                                "query": ip
                                            }
                                        }
                                    }
                                }
                            ]
                        }
                    }
                }
            },
            'facets': {
                'terms': {
                    'terms': {
                        'field': field,
                        'order': order,
                        'size': searchSize
                    }
                }
            }
        }
    )
    return ipTerms

def portTermSearch(field, order, searchSize, ip, query, port):
    port = 'id.resp_p:' + str(port)
    ipTerms = es.search(
        index=indexName,
        body={
            'size': 0,
            'query': {
                'filtered': {
                    'filter': {
                        'bool': {
                            "must": [
                                {
                                    "fquery": {
                                        "query": {
                                            "query_string": {
                                                "query": query
                                            }
                                        }
                                    }
                                },
                                {
                                    "fquery": {
                                        "query": {
                                            "query_string": {
                                                "query": ip
                                            }
                                        }
                                    }
                                },
                                {
                                    "fquery": {
                                        "query": {
                                            "query_string": {
                                                "query": port
                                            }
                                        }
                                    }
                                }
                            ]
                        }
                    }
                }
            },
            'facets': {
                'terms': {
                    'terms': {
                        'field': field,
                        'order': order,
                        'size': searchSize
                    }
                }
            }
        }
    )
    return ipTerms

###method used for sorts##
def ipTermSort(field, order, searchSize, ip, query):
    ipTerms = es.search(
        index=indexName,
        body={
            'query': {
                'filtered': {
                    'filter': {
                        'bool': {
                            "must": [
                                {
                                    "fquery": {
                                        "query": {
                                            "query_string": {
                                                "query": query
                                            }
                                        }
                                    }
                                },
                                {
                                    "fquery": {
                                        "query": {
                                            "query_string": {
                                                "query": ip
                                            }
                                        }
                                    }
                                }
                            ]
                        }
                    }
                }
            },
            'size': searchSize,
            'sort': [
                {
                    field: {
                        'order': order,
                        'ignore_unmapped': 'true'
                    }
                }
            ]
        }
    )
    return ipTerms

def portTermSort(field, order, searchSize, ip, query, port):
    port = 'id.resp_p:' + str(port)
    portTerms = es.search(
        index=indexName,
        body={
            'query': {
                'filtered': {
                    'filter': {
                        'bool': {
                            "must": [
                                {
                                    "fquery": {
                                        "query": {
                                            "query_string": {
                                                "query": query
                                            }
                                        }
                                    }
                                },
                                {
                                    "fquery": {
                                        "query": {
                                            "query_string": {
                                                "query": ip
                                            }
                                        }
                                    }
                                },
                                {
                                    "fquery": {
                                        "query": {
                                            "query_string": {
                                                "query": port
                                            }
                                        }
                                    }
                                }
                            ]
                        }
                    }
                }
            },
            'size': searchSize,
            'sort': [
                {
                    field: {
                        'order': order,
                        'ignore_unmapped': 'true'
                    }
                }
            ]
        }
    )
    return portTerms

def dnsLog():
    # dns report starts here
    # CHANGE THIS VARIABLE FOR DIFFERENT BROLOGS
    term = 'BRO_dnslog'
    log = 'dns'
    portQuery = 53
    query = '_type:' + term
    print "<== Query: query"
    test = es.count(index=indexName, q=query)
    size = test['count']
    print size

    ####searching for ips and counts ###
    ips = termSearch('id.orig_h', 'count', size, query)
    print ips

    # finding ipCount for ips
    important = ips['facets']['terms']['terms']
    ipCount = {}
    for useful in important:
        ipCount[useful['term']] = useful['count']

    for ips in ipCount.keys():

        ipQuery = "id.orig_h:" + '"' + ips + '"'
        ipSearchSize = ipCount[ips]
        a = Attack(ips, ipSearchSize, 53)
        a.log = log

        a.method = 'dns'
        if (ipSearchSize / hostCount > 10):
            a.type = 'attack'
        else:
            a.type = 'scan'

        #try:
	   # finding the first timestamp
    	startTime = ipTermSort('@timestamp', 'asc', 1, ipQuery, query)

    	# finding the last timestamp
    	endTime = ipTermSort('@timestamp', 'desc', 1, ipQuery, query)
        #except:
        #continue
        #### /1000 is to fix miliseconds ####
        a.epoch_start = float(startTime['hits']['hits'][0]['_source']['ts'])
        a.epoch_end = float(endTime['hits']['hits'][0]['_source']['ts'])
        duration = (a.epoch_end - a.epoch_start)

        a.start_time = startTime['hits']['hits'][0]['_source']['@timestamp']
        a.end_time = endTime['hits']['hits'][0]['_source']['@timestamp']
        a.duration = duration

        # finding the queries and counts
        queryList = ipTermSearch('query', 'count', ipSearchSize, ipQuery, query)
        queryList = queryList['facets']['terms']['terms']
        for things in queryList:
            a.query[things['term']] = things['count']

        # finding the qtypes and counts
        qtypeList = ipTermSearch('qtype', 'count', ipSearchSize, ipQuery, query)
        qtypeList = qtypeList['facets']['terms']['terms']
        for things in qtypeList:
            a.qtype[things['term']] = things['count']

            # finding the origin ports and counts
        portList = ipTermSearch('id.orig_p', 'count', 10, ipQuery, query)
        portList = portList['facets']['terms']['terms']
        for things in portList:
            a.ports[things['term']] = things['count']

        # finding excess data
        hits = startTime['hits']['hits'][0]
        try:
            a.country = hits['_source']['geoip']['country_name']
        except KeyError:
            a.country = ''
        try:
            a.region = hits['_source']['geoip']['real_region_name']
        except KeyError:
            a.region = ''
        try:
            a.trans_id = hits['_source']['trans_id']
        except KeyError:
            a.trans_id = ''
        try:
            asn = gi.org_by_addr(a.ip).split(' ')[0]
            a.asn = asn.replace('AS', '')
        except AttributeError:
            a.asn = ''

        attacks.append(a)

        print a.ip
        print a.count
        print a.method
        print a.type
        print a.start_time
        print a.end_time
        print a.duration
        print a.query
        print a.qtype
        print a.country
        print a.region
        print a.ports
        print a.asn
        print ''

def ntpLog():
    # ntp report starts here
    # CHANGE THESE VARIABLES FOR DIFFERENT BROLOGS
    term = 'BRO_ntplog'
    log = 'ntp'
    query = '_type:' + term

    test = es.count(index=indexName, q=query)
    size = test['count']
    print size

    ####searching for ips and counts ###
    ips = termSearch('id.orig_h', 'count', size, query)

    # finding ipCount for ips
    important = ips['facets']['terms']['terms']
    ipCount = {}
    for useful in important:
        ipCount[useful['term']] = useful['count']

    for ips in ipCount.keys():

        ipQuery = "id.orig_h:" + '"' + ips + '"'
        ipSearchSize = ipCount[ips]
        a = Attack(ips, ipSearchSize, 123)
        a.log = log


        a.method = 'ntp'
        if (ipSearchSize / hostCount > 10):
            a.type = 'attack'
        else:
            a.type = 'scan'
        # finding the first timestamp
        startTime = ipTermSort('@timestamp', 'asc', 1, ipQuery, query)

        # finding the last timestamp
        endTime = ipTermSort('@timestamp', 'desc', 1, ipQuery, query)

        #### /1000 is to fix miliseconds ####
        a.epoch_start = float(startTime['hits']['hits'][0]['_source']['ts'])
        a.epoch_end = float(endTime['hits']['hits'][0]['_source']['ts'])
        duration = (a.epoch_end - a.epoch_start)
        a.start_time = startTime['hits']['hits'][0]['_source']['@timestamp']
        a.end_time = endTime['hits']['hits'][0]['_source']['@timestamp']
        a.duration = duration

        # finding the origin ports and counts
        portList = ipTermSearch('id.orig_p', 'count', 10, ipQuery, query)
        portList = portList['facets']['terms']['terms']
        for things in portList:
            a.ports[things['term']] = things['count']

        # finding excess data
        hits = startTime['hits']['hits'][0]
        for doc in hits:
            try:
                a.country = hits['_source']['geoip']['country_name']
            except KeyError:
                a.country = ''
            try:
                a.region = hits['_source']['geoip']['real_region_name']
            except KeyError:
                a.region = ''
            try:
                asn = gi.org_by_addr(a.ip).split(' ')[0]
                a.asn = asn.replace('AS', '')

            except AttributeError:
                a.asn = ''

        attacks.append(a)

        print a.ip
        print a.count
        print a.method
        print a.type
        print a.start_time
        print a.end_time
        print a.duration
        print a.country
        print a.region
        print a.ports
        print a.asn
        print ''

def connLog():
    # conn report starts here
    # CHANGE THESE VARIABLES FOR DIFFERENT BROLOGS
    term = 'BRO_connlog'
    log = 'conn'
    query = '_type:' + term

    test = es.count(index=indexName, q=query)
    size = test['count']
    print size

    print 'filtering logs...'

    ####searching for ips and counts ###
    ips = termSearch('id.orig_h', 'count', size, query)
    important = ips['facets']['terms']['terms']
    ipCount = {}
    for useful in important:
        ipCount[useful['term']] = useful['count']


    connReport = {}
    ####adding matching resp_p to connReports
    for ips in ipCount.keys():
        try:
            ipSearchSize = ipCount[ips]
            ipQuery = '"' + ips + '"'
            destList = ipTermSearch('id.resp_p', 'count', ipSearchSize, ipQuery, query)
            destList = destList['facets']['terms']['terms']
            for port in destList:
                if(int(port['term']) in attackDict.keys()):
                    connReport[ips] = int(port['term'])
        except:
            continue

    connAttackList = []

    for attackInstances in connReport.keys():
        try:
            ipQuery = "id.orig_h:" + attackInstances + '"' + ips + '"'
            count = portCount(query, ipQuery, connReport[attackInstances])
            count = count['count']
            connAttackList.append(Attack(attackInstances, count, connReport[attackInstances]))
        except:
            continue

    for a in connAttackList:
        try:
            ipQuery = "id.orig_h:" + a.ip

            # finding the first timestamp
            startTime = portTermSort('@timestamp', 'asc', 1, ipQuery, query, a.resp_p)

            # finding the last timestamp
            endTime = portTermSort('@timestamp', 'desc', 1, ipQuery, query, a.resp_p)

            #### /1000 is to fix miliseconds ####
            a.epoch_start = float(startTime['hits']['hits'][0]['_source']['ts'])
            a.epoch_end = float(endTime['hits']['hits'][0]['_source']['ts'])
            duration = (a.epoch_end - a.epoch_start)
            a.start_time = startTime['hits']['hits'][0]['_source']['@timestamp']
            a.end_time = endTime['hits']['hits'][0]['_source']['@timestamp']
            a.duration = duration

            # Searching for ports and counts
            portList = portTermSearch('id.orig_p', 'count', 10, ipQuery, query, a.resp_p)
            portList = portList['facets']['terms']['terms']
            for things in portList:
                a.ports[things['term']] = things['count']


            # finding excess data
            hits = startTime['hits']['hits'][0]
            for doc in hits:
                try:
                    a.country = hits['_source']['geoip']['country_name']
                except KeyError:
                    a.country = ''
                try:
                    a.region = hits['_source']['geoip']['real_region_name']
                except KeyError:
                    a.region = ''
                try:
                    asn = gi.org_by_addr(a.ip).split(' ')[0]
                    a.asn = asn.replace('AS', '')
                except AttributeError:
                    a.asn = ''

            # checking which scan it is
            a.method = attackDict[a.resp_p]

            # adding scan or attack variable
            if (a.count / hostCount > 10):
                a.type = 'attack'
            else:
                a.type = 'scan'

            attacks.append(a)

            print a.ip
            print a.count
            print a.method
            print a.type
            print a.start_time
            print a.end_time
            print a.duration
            print a.country
            print a.region
            print a.ports
            print a.asn
            print ''

        except IndexError:
            print 'no result'
     
def saveReport():
    # done making attack list - sort and write to file
    attacks.sort(key=lambda x: x.epoch_start)

    finalPretty = []
    finalJson = []


    finalPretty.append('Daily Attack Feed')
    finalPretty.append(date)
    finalPretty.append('Zane Witherspoon')
    finalPretty.append('Terrence Gareau')
    finalPretty.append('NexusGuard')
    finalPretty.append('Ports, Queries, and Qtypes are formatted: {"term": count}')
    finalPretty.append('')
    finalPretty.append('')
    ###printing and json dump###
    for info in attacks:
        if (info.log == 'dns'):
            finalPretty.append('ip: ' + info.ip)
            finalPretty.append('count: ' + str(info.count))
            finalPretty.append('method: ' + info.method)
            finalPretty.append('type: ' + info.type)
            finalPretty.append('start time: ' + info.start_time)
            finalPretty.append('end time: ' + info.end_time)
            finalPretty.append('country: ' + info.country)
            finalPretty.append('region: ' + info.region)
            finalPretty.append('queries: ' + str(info.query))
            finalPretty.append('qtype: ' + str(info.qtype))
            finalPretty.append('source ports: ' + str(info.ports))
            finalPretty.append('transaction id: ' + info.trans_id)
            finalPretty.append('asn: ' + info.asn)
            finalPretty.append('')

            finalJson.append({
                'ip': info.ip,
                'count': info.count,
                'method': info.method,                              
                'type': info.type,
                'start_time': info.start_time,
                'end_time': info.end_time,
                'country': info.country,
                'region': info.region,
                'queries': info.query,
                'qtype': info.qtype,
                'src_ports': info.ports,
                'transaction_id': info.trans_id,
                'asn': info.asn})

        elif (info.log == 'ntp'):
            finalPretty.append('ip: ' + info.ip)
            finalPretty.append('count: ' + str(info.count))
            finalPretty.append('method: ' + info.method)
            finalPretty.append('type: ' + info.type)
            finalPretty.append('start time: ' + info.start_time)
            finalPretty.append('end time: ' + info.end_time)
            finalPretty.append('country: ' + info.country)
            finalPretty.append('region: ' + info.region)
            finalPretty.append('source ports: ' + str(info.ports))
            finalPretty.append('asn: ' + info.asn)
            finalPretty.append('')

            finalJson.append({
                'ip': info.ip,
                'count': info.count,
                'method': info.method,                              
                'type': info.type,
                'start_time': info.start_time,
                'end_time': info.end_time,
                'country': info.country,
                'region': info.region,
                'src_ports': info.ports,
                'asn': info.asn})
        else:
            finalPretty.append('ip: ' + info.ip)
            finalPretty.append('count: ' + str(info.count))
            finalPretty.append('method: ' + info.method)
            finalPretty.append('type: ' + info.type)
            finalPretty.append('start time: ' + info.start_time)
            finalPretty.append('end time: ' + info.end_time)
            finalPretty.append('country: ' + info.country)
            finalPretty.append('region: ' + info.region)
            finalPretty.append('source ports: ' + str(info.ports))
            finalPretty.append('asn: ' + info.asn)
            finalPretty.append('')

            finalJson.append({
                'ip': info.ip,
                'count': info.count,
                'method': info.method,                              
                'type': info.type,
                'start_time': info.start_time,
                'end_time': info.end_time,
                'country': info.country,
                'region': info.region,
                'src_ports': info.ports,
                'asn': info.asn})


    headedJson = {'title':'Daily Attack Feed', 'date':date, 'developers':['Zane Witherspoon', 'Terrence Gareau'], 
    'company':'NexusGuard', 'attacks':finalJson}


    with open(os.path.join(path, date + '-attack-summary.json'), 'w') as outfile:
        json.dump(finalJson, outfile, indent=4)

    with open(os.path.join(path, date + '-attack-summary-comments'), 'w') as comments:
        comments.write('Daily Attack Feed' + '\n')
        comments.write(date + '\n') 
        comments.write('Zane Witherspoon' + '\n')
        comments.write('Terrence Gareau' + '\n')
        comments.write('NexusGuard' + '\n')
        comments.write('Ports, Queries, and Qtypes are formatted: {"term": count}' + '\n')
        comments.write('\n')
        comments.write('\n')

    with open(os.path.join(path, date + '-attack-pretty-summary'), 'w') as f:
        for lines in finalPretty:
            f.write(lines + '\n')



## main code ##
# Imports and Elasticearch object for searching and stuff
from elasticsearch import Elasticsearch
import datetime
import time
import json
import pprint
import os
import GeoIP

# Instantiate GeoIP ASN Library
gi = GeoIP.open("/usr/share/GeoIP/GeoLiteASNum.dat", GeoIP.GEOIP_MEMORY_CACHE)

# start recording program runtime
start = time.time()

# defining important variables
es = Elasticsearch(['10.240.7.145','10.240.223.58', '10.240.248.171'], timeout=10, sniff_on_start=True, sniff_on_connection_fail=True, sniffer_timeout=60)
date = datetime.datetime.strftime(
    datetime.datetime.now() - datetime.timedelta(1), '%Y.%m.%d')
    #datetime.datetime.now(), '%Y.%m.%d')
indexName = 'logstash-' + date
attacks = []
print indexName

es.indices.refresh(index=indexName)

attackDict = {19: 'CHARGEN', 7: 'Echo', 5353: 'MDNS', 1434: 'Mssql', 5351: 'NAT-PMP', 137: 'Netbios-137',
              27960: 'Quake', 520: 'RIP', 5093: 'Sentinal-5093', 161: 'SNMP', 1900: 'SSDP', 9987: 'TeamSpeak3',
              7778: 'UnrealTournament', 177: 'XDMCP', 9200: 'Elasticsearch', 500: 'IKE'}

# setting up directory
path = '/root/feeds/' + date + '-logs'
if not os.path.exists(path):
    os.makedirs(path)

####searching for variable hosts and count ####
hosts = termSearch('host', 'count', 100, '_type:BRO_dnslog')

# hostCount starts at -1 to make up for the non-existant 'com' host
hostCount = -1
for count in hosts['facets']['terms']['terms']:
    hostCount += 1




##calling major methods
dnsLog()

ntpLog()

connLog()

saveReport()

end = time.time()
print (end - start)



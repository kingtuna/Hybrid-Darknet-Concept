# DNS reports from es
# Zane Witherspoon
# and Terrence Gareau
# 25 December 2015

"""
Things you have to change when moving from dev to prod
IP of ES 
GEOloc directoty
feeds directory
"""

scanCount = 4
_ESSERVERS = ['0.0.0.0', '0.0.0.0']
_FEEDPATH = '/root/feeds/'
_GEOLOCDIR = "/opt/local/share/GeoIP/GeoLiteASNum.dat"
_PDNSAPIKEY = ''
_PDNSSERVER = 'https://api.dnsdb.info'

# Imports and Elasticearch object for searching and stuff
from elasticsearch import Elasticsearch
import datetime
import time
import json
import os
import GeoIP
import calendar
import sys
import urllib
import urllib2


# Attack object holds key information
class Attack:
    def __init__(self, ip, count, resp_p):
        self.ip = ip
        self.count = count
        self.resp_p = resp_p
        self.resp_h = ''
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
        self.queryCount = 0
        self.ports = {}
        self.trans_id = ''
        self.country = ''
        self.region = ''
        self.asn = ''
        self.lat = 0
        self.long = 0
        self.pdns = ''
        self.confidence = 75

class DnsdbClient(object):
    """Class for handeling rdns"""
    def __init__(self, limit=None):
        self.server = _PDNSSERVER
        self.apikey = _PDNSAPIKEY
        self.limit = limit
    def not_good(self,excepti,traci):
        """Shitty function included within code"""
        pass
    def quote(self,path):
        """defined this outside of the class"""
        return urllib.quote(path, safe='')
    def query_rrset(self, oname, rrtype=None, bailiwick=None, before=None, after=None):
        if bailiwick:
            if not rrtype:
                rrtype = 'ANY'
            path = 'rrset/name/%s/%s/%s' % (self.quote(oname), rrtype, self.quote(bailiwick))
        elif rrtype:
            path = 'rrset/name/%s/%s' % (self.quote(oname), rrtype)
        else:
            path = 'rrset/name/%s' % self.quote(oname)
        return self._query(path, before, after)

    def query_rdata_name(self, rdata_name, rrtype=None, before=None, after=None):
        if rrtype:
            path = 'rdata/name/%s/%s' % (self.quote(rdata_name), rrtype)
        else:
            path = 'rdata/name/%s' % self.quote(rdata_name)
        return self._query(path, before, after)

    def query_rdata_ip(self, rdata_ip, before=None, after=None):
        path = 'rdata/ip/%s' % rdata_ip.replace('/', ',')
        return self._query(path, before, after)

    def _query(self, path, before=None, after=None):
        url = '%s/lookup/%s' % (self.server, path)

        params = {}
        if self.limit:
            params['limit'] = self.limit
        if before and after:
            params['time_first_after'] = after
            params['time_last_before'] = before
        else:
            if before:
                params['time_first_before'] = before
            if after:
                params['time_last_after'] = after
        if params:
            url += '?{0}'.format(urllib.urlencode(params))

        req = urllib2.Request(url)
        req.add_header('Accept', 'application/json')
        req.add_header('X-Api-Key', self.apikey)
        try:
            http = urllib2.urlopen(req)
            while True:
                line = http.readline()
                if not line:
                    break
                yield json.loads(line)
        except (urllib2.HTTPError, urllib2.URLError), e:
            raise self.not_good, str(e), sys.exc_traceback


###method used for general term searches##
def termSearch(field, order, searchSize, term):
    terms = es.search(
        request_timeout=30,
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
    request_timeout=30,
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
        request_timeout=30,
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
        request_timeout=30,
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
        request_timeout=30,
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

def epoch_to_iso8601(timestamp):
    """
    epoch_to_iso8601 - convert the unix epoch time into a iso8601 formatted date
    >>> epoch_to_iso8601(1341866722)
    '2012-07-09T22:45:22'
    """
    return datetime.datetime.fromtimestamp(timestamp).isoformat()

def iso8601_to_epoch(datestring):
    """
    iso8601_to_epoch - convert the iso8601 date into the unix epoch time
    >>> iso8601_to_epoch("2012-07-09T22:27:50.272517")
    1341872870
    """
    return calendar.timegm(datetime.datetime.strptime(datestring, "%Y-%m-%dT%H:%M:%S.%f").timetuple())

def pdns_data(IP):
    client = DnsdbClient()
    try:
        ret = client.query_rdata_ip(IP)
    except:
        ret = ''
    try:
        if ret:
            pdns={}
            pdnsdata = []
            for i in ret:
                first = epoch_to_iso8601(i['time_first'])
                last = epoch_to_iso8601(i['time_last'])
                pdnsdata.append({'count':i['count'],'first_seen':first,
                                 'last_seen':last,'rrname':i['rrname'],
                                 'count':i['count']})
            pdns['pdns'] = pdnsdata
            #print pdns
            #print json.dumps(pdns,sort_keys=True, indent=4, separators=(',', ': '))
            return(pdns)
    except:
        ret = ''
    return(ret)

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
    ips = termSearch('id.orig_h.raw', 'count', size, query)
    print ips

    # finding ipCount for ips
    important = ips['facets']['terms']['terms']
    ipCount = {}
    for useful in important:
        ipCount[useful['term']] = useful['count']

    for ips in ipCount.keys():

        ipQuery = "id.orig_h:" + '"' + ips + '"'
        ipSearchSize = ipCount[ips]
        print ipSearchSize
        a = Attack(ips, ipSearchSize, 53)
        a.log = log

        a.method = 'dns'
        if (ipSearchSize / hostCount > scanCount):
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
        queryList = ipTermSearch('query.raw', 'count', ipSearchSize, ipQuery, query)
        a.queryCount = queryList['facets']['terms']['total']
        queryList = queryList['facets']['terms']['terms']
        for things in queryList:
            a.query[things['term']] = things['count']

        # finding the qtypes and counts
        qtypeList = ipTermSearch('qtype.raw', 'count', ipSearchSize, ipQuery, query)
        qtypeList = qtypeList['facets']['terms']['terms']
        for things in qtypeList:
            a.qtype[things['term']] = things['count']

            # finding the origin ports and counts
        portList = ipTermSearch('id.orig_p.raw', 'count', 10, ipQuery, query)
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
            a.lat = hits['_source']['geoip']['latitude']
        except KeyError:
            a.lat = 0
        try:
            a.long = hits['_source']['geoip']['longitude']
        except KeyError:
            a.long = 0
        try:
            a.trans_id = hits['_source']['trans_id']
        except KeyError:
            a.trans_id = ''
        try:
            a.resp_h = hits['_source']['id.resp_h']
        except KeyError:
            a.resp_h = ''
        try:
            asn = gi.org_by_addr(a.ip).split(' ')[0]
            a.asn = asn.replace('AS', '')
        except AttributeError:
            a.asn = ''
        try:
            a.pdns = pdns_data(a.ip)
        except AttributeError:
            a.pdns = ''

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
    ips = termSearch('id.orig_h.raw', 'count', size, query)

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
        if (ipSearchSize / hostCount > scanCount):
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
        portList = ipTermSearch('id.orig_p.raw', 'count', 10, ipQuery, query)
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
                a.lat = hits['_source']['geoip']['latitude']
            except KeyError:
                a.lat = 0
            try:
                a.long = hits['_source']['geoip']['longitude']
            except KeyError:
                a.long = 0
            try:
                a.resp_h = hits['_source']['id.resp_h']
            except KeyError:
                a.resp_h = ''
            try:
                asn = gi.org_by_addr(a.ip).split(' ')[0]
                a.asn = asn.replace('AS', '')

            except AttributeError:
                a.asn = ''
            try:
                a.pdns = pdns_data(a.ip)
            except AttributeError:
                a.pdns = ''

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
        print a.pdns
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
    ips = termSearch('id.orig_h.raw', 'count', size, query)
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
            destList = ipTermSearch('id.resp_p.raw', 'count', ipSearchSize, ipQuery, query)
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
            portList = portTermSearch('id.orig_p.raw', 'count', 10, ipQuery, query, a.resp_p)
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
                    a.lat = hits['_source']['geoip']['latitude']
                except KeyError:
                    a.lat = 0
                try:
                    a.long = hits['_source']['geoip']['longitude']
                except KeyError:
                    a.long = 0
                try:
                    a.resp_h = hits['_source']['id.resp_h']
                except KeyError:
                    a.resp_h = ''
                try:
                    asn = gi.org_by_addr(a.ip).split(' ')[0]
                    a.asn = asn.replace('AS', '')
                except AttributeError:
                    a.asn = ''
                try:
                    a.pdns = pdns_data(a.ip)
                except AttributeError:
                    a.pdns = ''

            # checking which scan it is
            a.method = attackDict[a.resp_p]

            ##setting ssdp to 50% confidence
            if(a.resp_p == 1900):
                a.confidence = 50

            # adding scan or attack variable
            if (a.count / hostCount > scanCount):
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
            print a.pdns
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
    for info in filteredAttacks:
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
            finalPretty.append('pdns: ' + str(info.pdns))
            finalPretty.append('confidence: ' + str(info.confidence))
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
                'asn': info.asn,
                'pdns': info.pdns,
                'confidence': str(info.confidence)})

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
            finalPretty.append('pdns: ' + str(info.pdns))
            finalPretty.append('confidence: ' + str(info.confidence))
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
                'asn': info.asn,
                'pdns': info.pdns,
                'confidence': str(info.confidence)})
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
            finalPretty.append('pdns: ' + str(info.pdns))
            finalPretty.append('confidence: ' + str(info.confidence))
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
                'asn': info.asn,
                'pdns': info.pdns,
                'confidence': str(info.confidence)})


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


def filterLogs():
    print "filtering for user rules"

    filterDict = {"workgroup":"query", "wpad":"query", "isatap":"query", "atlantic":"query", 
    "fe80::":"ip", "33":"qtype", "-":"qtype", "12":"qtype", "239.255.255.250":"resp_h"}


    for info in attacks:
        contains = False
        if(info.log == "dns"):
            if(info.type == "attack"):
                ratio = float(len(info.query))/float(info.queryCount)
                if(ratio >= 0.95):
                    contains = True
                    print 'removing becasue it\'s not actually a dns attack'
                    print '*' * 50
                    print 'ratio ' 
                    print ratio
                    print 'unique queries'
                    print float(len(info.query))
                    print 'total queries'
                    print info.queryCount
        for key in filterDict:
            attribute = getattr(info,filterDict[key])
            rule = key
            if(isinstance(attribute,dict)):
                for answer in attribute:
                    #print answer
                    #print rule
                    if(isinstance(answer, str) or isinstance(answer, unicode)):
                        if(answer.upper()==rule.upper() or (answer[0:len(rule)].upper()==rule.upper())):
                            print 'removing becasue of ' + answer
                            contains = True
                    else:
                        if(answer == rule):
                            print'removing becasue of ' + answer
                            contains = True
            else:
                answer = attribute
                if(isinstance(answer, str) or isinstance(answer, unicode)):
                    if(answer.upper()==rule.upper() or (answer[0:len(rule)].upper()==rule.upper())):
                        print 'removing becasue of ' + answer
                        contains = True
                else:
                    if(answer == rule):
                        print'removing becasue of ' + answer
                        contains = True
        if not contains:
            filteredAttacks.append(info)






## main code ##

# Instantiate GeoIP ASN Library
gi = GeoIP.open(_GEOLOCDIR, GeoIP.GEOIP_MEMORY_CACHE)

# start recording program runtime
start = time.time()

# defining important variables
## IP Address
es = Elasticsearch(_ESSERVERS, timeout=10)
date = datetime.datetime.strftime(
    #TG set back to 1
    datetime.datetime.now() - datetime.timedelta(1), '%Y.%m.%d')
    #datetime.datetime.now(), '%Y.%m.%d')
indexName = 'logstash-' + date
attacks = []
filteredAttacks = []
print indexName

es.indices.refresh(index=indexName)

attackDict = {19: 'CHARGEN', 7: 'Echo', 5353: 'MDNS', 1434: 'Mssql', 5351: 'NAT-PMP', 111: 'Portmapper',
              27960: 'Quake', 520: 'RIP', 5093: 'Sentinal-5093', 161: 'SNMP', 1900: 'SSDP', 9987: 'TeamSpeak3',
              7778: 'UnrealTournament', 177: 'XDMCP', 9200: 'Elasticsearch', 500: 'IKE'}

# setting up directory
path = _FEEDPATH + date + '-logs'
if not os.path.exists(path):
    os.makedirs(path)

####searching for variable hosts and count ####
hosts = termSearch('host.raw', 'count', 100, '_type:BRO_dnslog')

# hostCount starts at -1 to make up for the non-existant 'com' host
hostCount = 0
for count in hosts['facets']['terms']['terms']:
    hostCount += 1




##calling major methods
dnsLog()

ntpLog()

connLog()

filterLogs()

saveReport()

#buildHeatmap()

end = time.time()
print (end - start)

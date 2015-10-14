import json, os, csv
import geoip2.database
from collections import Counter

reader = geoip2.database.Reader('/usr/local/share/GeoIP/GeoIP2-ISP.mmdb')
readercunt = geoip2.database.Reader('/usr/local/share/GeoIP/GeoIP2-Country.mmdb')
dirlist = os.listdir('feeddata')

####### Classes
### AS Lookup class returns name
class asnLookup():
    """Write class to lookup asn"""
    def __init__(self):
        self.updateDir = "./"
        self.file = str(self.updateDir)+'cidr.txt'
        self.database = {}
        self.loadFile()
    def update(self):
        """Update the asn.txt file from arin and delete the header"""
        import urllib 
        urllib.urlretrieve('http://www.cidr-report.org/as2.0/autnums.html',self.file)
        lines = open(self.file).readlines()
        open(self.file, 'w').writelines(lines[13:-1])
    def remove_tags(self,text):
        import re
        TAG_RE = re.compile(r'<[^>]+>')
        return TAG_RE.sub('', text)
    def loadFile(self):
        """Load File into memory"""
        handler = open(self.file, 'ro')
        for i in handler:
            predata = self.remove_tags(i.strip())
            if predata[:2].upper() == 'AS':
                asn = predata.split(' ', 1)[0][2:]
                name = predata.split(' ', 1)[1]
                self.database[asn] = name
            else:
                continue
    def lookup(self,asn):
        try:
            if asn[:2].upper() == 'AS':
                asn = asn[2:] 
            #print asn
            #print self.database[asn].strip()
            return(self.database[asn].strip())
        except:
            return('')

## Get Directory Data 
direct=[]
direct1=[]
for i in dirlist:
    if i[0:8] == '2015.09.':
        direct.append(i)

for i in direct:
    direct1.append('./feeddata/' + i + str('/'+i[0:10]) + str('-attack-summary.json'))


datal = []
datal.append("time,asn,cuntry,ip,method")

for dirl in direct1:
        with open(dirl) as data_file:    
            data = json.load(data_file)
        for lines in data:
            if lines['method'] == 'Elasticsearch':
                continue
            if lines['asn'] =='':
                continue
            if lines['type'] == 'scan':
                try:
                    response2 = readercunt.country(lines['ip'])
                    cc = response2.country.iso_code
                    if cc == None:
                        cc = 'NA'
                except:
                    cc = 'NA'
                try:
                    ip = lines['ip']
                    if ip == None:
                        print lines
                except:
                    print ip
                try:
                    datal.append(lines['start_time']+"," +\
                                 lines['asn']+"," +\
                                 cc +"," +\
                                 unicode(lines['ip']) +"," +\
                                 lines['method'])
                except:
                    print cc,lines
                #start_time asn ip method


handler = open('scan.csv', 'wb')
for line in datal:
    if 'Elasticseasrch' in line:
        print line
    handler.write(line+'\n')
    #print line
handler.close()

#### Count ASNs-------------------
##usage asnn.lookup('4134') returns as name
asnn = asnLookup()
asns = []
for dirl in direct1:
    with open(dirl) as data_file:    
        data = json.load(data_file)
    for lines in data:
        if lines['method'] == 'Elasticsearch':
            continue
        if lines['asn'] =='':
            continue
        if lines['type'] == 'scan':
            asns.append(lines['asn'])

## Count 50
c = Counter(asns)
print"\n"

fieldnames = ('AS','Rank','Fullname','Count')
with open('scan_Top_50_Sources.csv', 'wb') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    print "Top 50 scan Sources\n(AS)\t(Count)"
    counter = 1
    for i in c.most_common(50):
        print str(i[0])+"\t"+str(i[1])+"\t"+asnn.lookup(i[0])
        AS = str(i[0])
        COUNT = str(i[1])
        FULLNAME = asnn.lookup(i[0])
        RANK = counter
        counter = counter + 1
        writer.writerow({'AS':AS,'Rank':RANK,'Fullname':FULLNAME,'Count':COUNT})
    
#### Count ASNs-------------------

#### Top scanner IP--------------------
ips = []
for dirl in direct1:
    with open(dirl) as data_file:    
        data = json.load(data_file)
    for lines in data:
        if lines['method'] == 'Elasticsearch':
            continue
        if lines['type'] == 'scan':
            ips.append(lines['ip'])


c = Counter(ips)
print"\n"
print "Top scan Sources\n(IP)\t(Count)"
for i in c.most_common(1):
    print str(i[0])+"\t"+str(i[1])
    top_ip = i[0]



top_IP_Data = []
for dirl in direct1:
    with open(dirl) as data_file:    
        data = json.load(data_file)
    for lines in data:
        if lines['method'] == 'Elasticsearch':
            continue
        if lines['ip'] == top_ip:
            top_IP_Data.append(lines)
            
with open('scan_Top_IP'+top_ip+'.txt', 'w') as fp:
    json.dump(top_IP_Data, fp, indent=4, sort_keys=True)
#### Top scanner IP--------------------

#### Top scanner Countries--------------------
countries = []
for dirl in direct1:
        with open(dirl) as data_file:    
            data = json.load(data_file)
        for lines in data:
            if lines['method'] == 'Elasticsearch':
                continue
            if lines['asn'] =='':
                continue
            if lines['type'] == 'scan':
                try:
                    response2 = readercunt.country(lines['ip'])
                    if cc == None:
                        continue
                    countries.append(response2.country.iso_code)
                except:
                    continue


c = Counter(countries)
print"\n"
counter = 1
fieldnames = ('Rank','Country','Count')
with open('scan_Top_Country.csv', 'wb') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    print "Top 10 scan Sources\n(Country)\t(Count)"
    for i in c.most_common(10):
        print str(i[0])+"\t"+str(i[1])
        RANK = counter
        counter = counter +1
        COUNTRY = str(i[0])
        COUNT = str(i[1])
        writer.writerow({'Rank':RANK,'Country':COUNTRY,'Count':COUNT})
#### Top scanner Countries--------------------


#### Top scanner methods --------------------
methods = []
for dirl in direct1:
        with open(dirl) as data_file:    
            data = json.load(data_file)
        for lines in data:
            if lines['method'] == 'Elasticsearch':
                continue
            if lines['asn'] =='':
                continue
            if lines['type'] == 'scan':
                try:
                    methods.append(lines['method'])
                except:
                    continue


c = Counter(methods)
counter = 1 
fieldnames = ('Rank','Method','Count')
with open('scan_methods.csv', 'wb') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    print"\n"
    print "scanning Type\n(Method)\t(Count)"
    for i in c.most_common(50):
        print str(i[0])+"\t"+str(i[1])
        METHOD = str(i[0])
        COUNT = str(i[1])
        RANK = counter
        counter = counter + 1
        writer.writerow({'Rank':RANK,'Method':METHOD,'Count':COUNT})
    
#### Top scanner methods--------------------
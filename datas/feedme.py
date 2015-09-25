import json, os

dirlist = os.listdir('feeddata')

direct=[]
direct1=[]
for i in dirlist:
    if i[0:8] == '2015.09.':
        direct.append(i)

for i in direct:
    direct1.append('./feeddata/' + i + str('/'+i[0:10]) + str('-attack-summary.json'))


datal = []
datal.append("time,asn,ip,tmethod")

for dirl in direct1:
    try:
        with open(dirl) as data_file:    
            data = json.load(data_file)
        for lines in data:
            if lines['type'] == 'scan':
                datal.append(lines['start_time']+"," +\
                           lines['asn']+"," +\
                           lines['ip']+"," +\
                           lines['method'])
                #start_time asn ip method
    except:
        pass



handler = open('test.csv', 'wb')
for line in datal:
    print line
    handler.write(line+'\n')

handler.close()
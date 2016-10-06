import smtplib
import datetime
from email.MIMEMultipart import MIMEMultipart
from email.MIMEBase import MIMEBase
from email.MIMEText import MIMEText
from email import Encoders
import gzip
import shutil
import sys

date = datetime.datetime.strftime(datetime.datetime.now() - datetime.timedelta(1), '%Y.%m.%d')
path = '/root/feeds/' + date + '-logs/'

username = "emails"
password = "password"

SUBJECT = "Attack data for " + date
EMAIL_FROM = 'feeds@nexusguard.com'

msg = MIMEMultipart()
msg['Subject'] = SUBJECT 
message = MIMEText("Your attack feed for " + date + '/n' + 'Json w/ comments and pretty print summaries' + 'NexusGuard')



####attaching items to email
try: 
    #attaching json
    part = MIMEBase('application', "octet-stream")
    name = date + "-attack-summary.json" 
    zname = date + "-attack-summary.json.gz" 
    with open(path + name, 'rb') as f_in, gzip.open(path + zname, 'wb') as f_out:
        shutil.copyfileobj(f_in, f_out)
    part.set_payload(open(path + zname, "rb").read())
    Encoders.encode_base64(part)
    part.add_header('Content-Disposition', 'attachment', filename=zname)
    msg.attach(part)
except:
    sys.exit() 
try:    
    #attaching comments
    part2 = MIMEBase('application', "octet-stream")
    name = date + "-attack-summary-comments" 
    part2.set_payload(open(path + name, "rb").read())
    Encoders.encode_base64(part2)
    part2.add_header('Content-Disposition', 'attachment', filename=date + "-json-comments.txt")
    msg.attach(part2)
except:
    pass
try:
    #attaching pretty
    part3 = MIMEBase('application', "octet-stream")
    name = date + "-attack-pretty-summary" 
    zname = date + "-attack-pretty-summary.gz" 
    with open(path + name, 'rb') as f_in, gzip.open(path + zname, 'wb') as f_out:
        shutil.copyfileobj(f_in, f_out)
    part3.set_payload(open(path + zname, "rb").read())
    Encoders.encode_base64(part3)
    part3.add_header('Content-Disposition', 'attachment', filename=zname)
    msg.attach(part3)
except:
    pass
#attaching ssh pretty
try:
    part4 = MIMEBase('application', "octet-stream")
    name = date + "-ssh-pretty-summary"
    part4.set_payload(open(path + name, "rb").read())
    Encoders.encode_base64(part4)
    part4.add_header('Content-Disposition', 'attachment', filename=name+".txt")
    msg.attach(part4)
except:
    pass

#attaching json ssh
try:
    part5 = MIMEBase('application', "octet-stream")
    name = date + "-ssh-summary.json" 
    part5.set_payload(open(path + name, "rb").read())
    Encoders.encode_base64(part5)
    part5.add_header('Content-Disposition', 'attachment', filename=name)
    msg.attach(part5)
except:
    pass

#attaching detailed ssh
try:
    part6 = MIMEBase('application', "octet-stream")
    name = date + "-ssh-detailed.json" 
    part6.set_payload(open(path + name, "rb").read())
    Encoders.encode_base64(part6)
    part6.add_header('Content-Disposition', 'attachment', filename=name)
    msg.attach(part6)
except:
    pass




server = smtplib.SMTP('smtp.gmail.com:587')
server.starttls()
server.login(username,password)

with open("/root/python/report_list.txt") as f:
    content = f.readlines()

try:
    for email in content:
        server.sendmail(EMAIL_FROM, email.strip(), msg.as_string())
except:
    print(email,"failed")

server.quit()

import smtplib
import datetime
from email.MIMEMultipart import MIMEMultipart
from email.MIMEBase import MIMEBase
from email.MIMEText import MIMEText
from email import Encoders

date = datetime.datetime.strftime(datetime.datetime.now() - datetime.timedelta(1), '%Y.%m.%d')
path = '/root/feeds/' + date + '-logs/'

username = "feeds@nexusguard.com"
password = "&fWP@q-buz.W57xU"

SUBJECT = "Attack data for " + date
EMAIL_FROM = 'feeds@nexusguard.com'

msg = MIMEMultipart()
msg['Subject'] = SUBJECT 
message = MIMEText("Your attack feed for " + date + '/n' + 'Json w/ comments and pretty print summaries' + 'NexusGuard')



####attaching items to email
#attaching json
part = MIMEBase('application', "octet-stream")
name = date + "-attack-summary.json" 
part.set_payload(open(path + name, "rb").read())
Encoders.encode_base64(part)
part.add_header('Content-Disposition', 'attachment', filename=name)
msg.attach(part)

#attaching comments
part2 = MIMEBase('application', "octet-stream")
name = date + "-attack-summary-comments" 
part2.set_payload(open(path + name, "rb").read())
Encoders.encode_base64(part2)
part2.add_header('Content-Disposition', 'attachment', filename=date + "-json-comments.txt")
msg.attach(part2)

#attaching pretty
part3 = MIMEBase('application', "octet-stream")
name = date + "-attack-pretty-summary"
part3.set_payload(open(path + name, "rb").read())
Encoders.encode_base64(part3)
part3.add_header('Content-Disposition', 'attachment', filename=name+".txt")
msg.attach(part3)


server = smtplib.SMTP('smtp.gmail.com:587')
server.starttls()
server.login(username,password)

with open("/root/python/report_list.txt") as f:
    content = f.readlines()

for email in content:
	server.sendmail(EMAIL_FROM, email, msg.as_string())


server.quit()

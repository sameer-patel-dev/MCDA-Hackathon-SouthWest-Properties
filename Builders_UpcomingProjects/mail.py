import smtplib
import dexel
import urbancapital
import bancgroup
import werkliv
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

dexelResults = dexel.dexel_script()
print(dexelResults)


urbanCapitalResults = urbancapital.urbanCapital_script()
print(urbanCapitalResults)


bancGroupResults = bancgroup.bancgroup_script()
print(bancGroupResults)


werklivResults = werkliv.werkliv_script()
print(werklivResults)


def generate_table(data, title, headers=None):
    table_html = f'<h3>{title}</h3>'
    table_html += '<table border="1">'

    if headers:
        table_html += '<tr>' + ''.join(f'<th>{header}</th>' for header in headers) + '</tr>'
    for row in data:
        table_html += '<tr>' + ''.join(f'<td>{item}</td>' for item in row.split('\n')) + '</tr>'
    table_html += '</table><br>'
    return table_html



email = 'sameer.patel201999@gmail.com'
reciever_email = 'sameer.patel201999@gmail.com'

locations_table = generate_table(dexelResults, "Dexel")
projects_table = generate_table([" | ".join(project) for project in urbanCapitalResults], "Urban Capital")
suits_table = generate_table([" | ".join(suit) for suit in bancGroupResults], "Banc Group") 
international_table = generate_table([" | ".join(item) for item in werklivResults], "Werkliv")
html_message = locations_table + projects_table + suits_table + international_table
print(html_message)



msg = MIMEMultipart()
msg['From'] = email
msg['To'] = reciever_email
msg['Subject'] = "Builder Alert - New Property Available"
msg.attach(MIMEText(html_message, 'html', 'utf-8'))


server = smtplib.SMTP("smtp.gmail.com", 587)
server.starttls()
server.login(email, "cltujjtrtquxwbdq")
server.sendmail(email, reciever_email, msg.as_string())
print("Email sent")

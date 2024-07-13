import smtplib 
from email.mime.multipart import MIMEMultipart 
from email.mime.text import MIMEText 
from email.mime.base import MIMEBase 
from email import encoders 

def sendMail(toAddr,month,year,pdf_location,filename):

    fromaddr = "rajjm397@gmail.com"

    msg = MIMEMultipart() 

    msg['From'] = fromaddr
    msg['To'] = toAddr
    msg['Subject'] = f"Salary slip of {month.capitalize()}-{year}"

    body = f"Please find attached below the salary slip of {month.capitalize()}-{year}"

    msg.attach(MIMEText(body, 'plain')) 

    with open(pdf_location, "rb") as attachment:

        p = MIMEBase('application', 'octet-stream') 
        p.set_payload((attachment).read()) 
        encoders.encode_base64(p) 

        p.add_header(f'Content-Disposition', f"attachment; filename={filename}") 

        msg.attach(p) 

        s = smtplib.SMTP('smtp.gmail.com', 587) 
        s.starttls() 
        s.login(fromaddr, "pqpdhxnvautwxvoh") 
        text = msg.as_string() 
        s.sendmail(fromaddr, toAddr, text) 
        s.quit() 

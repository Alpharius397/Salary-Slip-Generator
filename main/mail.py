import smtplib 
from email.mime.multipart import MIMEMultipart 
from email.mime.text import MIMEText 
from email.mime.base import MIMEBase 
from email import encoders 

# a class for Mailing (supports method-chaining)
class Mailing():
    def __init__(self,email:str,key:str) -> None:
        self.email = email
        self.key = key
        self.msg = MIMEMultipart()
        self.msg['From'] = email
        self.status = True
        self.smtp = smtplib.SMTP('smtp.gmail.com', 587)
    
    #adds text-based messages to email
    def addTxtMsg(self,msg:str,msgType:str):
        part = MIMEText(msg,f'{msgType}')
        
        try:
            if self.status: self.msg.attach(part)
        except:
            self.status = False
        
        return self
    
    # attach items to email
    def addAttach(self,file:str,filename:str):
        try:
            if self.status:
                with open(file, "rb") as attachment:
                    p = MIMEBase('application', 'octet-stream') 
                    p.set_payload((attachment).read()) 
                    encoders.encode_base64(p) 
                    p.add_header(f'Content-Disposition', f"attachment; filename={filename}") 
                    self.msg.attach(p)
        except:
            self.status = False
        
        return self
    
    # add subject to email
    def addDetails(self,subject:str):
        try: 
            if self.status: self.msg['Subject'] = subject
        except:
            self.status = False
        
        return self
    
    # attempts smtp login
    def login(self):
        try:
            if self.status: 
                self.smtp.starttls()
                self.smtp.login(self.email,self.key)
        except:
            self.status = False
        
        return self
    
    # sends mail
    def sendMail(self,toAddr:str):
        try:
            if self.status:
                self.smtp.sendmail(self.email,toAddr,self.msg.as_string())
        except:
            self.status = False
        
        return self
    # resets MIMEMultipart()
    def resetMIME(self):
        self.msg = MIMEMultipart()
        return self
        
    # quits current smtp
    def destroy(self):
        self.smtp.quit() 
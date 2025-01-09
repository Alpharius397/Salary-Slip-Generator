import smtplib 
from email.mime.multipart import MIMEMultipart 
from email.mime.text import MIMEText 
from email.mime.base import MIMEBase 
from email import encoders 
from logger import Logger

# a class for Mailing (supports method-chaining)
class Mailing():
    def __init__(self,email:str,key:str,error_log:Logger) -> None:
        self.email = email
        self.key = key
        self.error = error_log
        self.msg = MIMEMultipart()
        self.msg['From'] = email
        self.status = True
            
    #adds text-based messages to email
    def addTxtMsg(self,msg:str,msgType:str) -> 'Mailing':
        part = MIMEText(msg,f'{msgType}')
        
        try:
            if self.status: self.msg.attach(part)
        except Exception as e:
            self.add_smtp_error(self.error.get_error_info(e))
            self.status = False
        
        return self
    
    # attach items to email
    def addAttach(self,file:str,filename:str) -> 'Mailing':
        try:
            if self.status:
                with open(file, "rb") as attachment:
                    p = MIMEBase('application/pdf', 'octet-stream') 
                    p.set_payload((attachment).read()) 
                    encoders.encode_base64(p) 
                    p.add_header(f'Content-Disposition', f"attachment; filename={filename}") 
                    self.msg.attach(p)
        except Exception as e:
            self.add_smtp_error(self.error.get_error_info(e))
            self.status = False
        
        return self
    
    # add subject to email
    def addDetails(self,subject:str) -> 'Mailing':
        try: 
            if self.status: self.msg['Subject'] = subject
        except Exception as e:
            self.add_smtp_error(self.error.get_error_info(e))
            self.status = False
        
        return self
    
    # attempts smtp login
    def login(self) -> 'Mailing':
        try:
            if self.status: 
		self.smtp = smtplib.SMTP('smtp.gmail.com', 587)
                self.smtp.starttls()
                self.smtp.login(self.email,self.key)
                self.add_smtp_info('Login Successful')
                
        except Exception as e:
            self.add_smtp_error(self.error.get_error_info(e))
            self.status = False
        
        return self
    
    # sends mail
    def sendMail(self,toAddr:str) -> 'Mailing':
        try:
            if self.status:
                self.smtp.sendmail(self.email,toAddr,self.msg.as_string())
                self.add_smtp_info(f'Email to ({toAddr}) was send successfully')
        except Exception as e:
            self.add_smtp_error(self.error.get_error_info(e))
            self.status = False
        
        return self
    
    # resets MIMEMultipart()
    def resetMIME(self) -> 'Mailing':
        self.msg = MIMEMultipart()
        return self
        
    # quits current smtp
    def destroy(self) -> 'Mailing':
        try:
            self.smtp.quit() 
            self.add_smtp_info('Logout Successful')
        except Exception as e:
            self.add_smtp_error(self.error.get_error_info(e))
            self.status=False
            
        return self
    
    def add_smtp_error(self, msg:str) -> None:
        self.error.write_error(msg,'SMTP')
        
    def add_smtp_info(self, msg:str) -> None:
        self.error.write_info(msg,'SMTP')

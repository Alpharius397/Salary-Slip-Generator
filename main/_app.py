import io
from collections import defaultdict
import os
import sys
from tkinter import simpledialog,font
from typing import IO
import customtkinter as ctk
import tkinter as tk
import tkinter.messagebox as tkmb
from tkinter import filedialog, scrolledtext, Scrollbar,messagebox 
import pdfkit
import pyperclip
import pandas as pd
from database import dataRefine,Database,mapping,check_column,PandaGenerator,get_salary_column
from mail import Mailing
from html_style import HTML_CONTENT,DATA_CONTENT
from logger import Logger
import msoffcrypto
from multiprocessing import Process,Queue
from threading import Thread
import re
import types

IS_EXE = False # when building .exe set to true
IS_DEBUG = True # for testing set to true
APP_PATH = __file__ if not IS_EXE else sys.executable
MYSQL_CRED = {'host':'localhost','user':'root','password':'1234','database':'somaiya_salary'} # your mysql creds for testing (works if is_debug == True)
SMTP_CRED = {'email':'salary.tech@somaiya.edu','key':'mhenlcndnwonyadw'} if not IS_DEBUG else {'email':'rajjm397@gmail.com','key':'fjuygjqzmsutwfjt'}
EMAIL_REGEX = lambda x: True if re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', str(x)) else False # a helper function for email validation
YEAR_CHECK = lambda x: True if re.match(r'^(\d){4}$',x) else False # a helper function for year validation
FILE_REGEX = r'employee_(\w+|\d+).pdf$'

ERROR_LOG = Logger(os.path.dirname(APP_PATH))
custom_color_scheme = {"fg_color": "white","button_color": "dark red","text_color": "black","combo_box_color": "white"}

ctk.set_appearance_mode("light")

class BaseTemplate():
    """ Base Template for all tkinter frames """
    
    frame:ctk.CTkScrollableFrame = None
    process:Process = None
    """ Each frame will have 1 process to run big task """
    thread:Thread = None
    """ Each frame gets 1 thread to process gui changes """
    QUEUE = Queue()
    """ A queue for communication between thread and process """
    stop_flag:bool = False
    """ A stop flag for thread to stop """
    visible:bool = False
    
    to_disable:list[ctk.CTkButton|ctk.CTkOptionMenu|ctk.CTkEntry] = []
    
    def appear(self) -> None:
        """ Add frame to the tkinter app """
        if(not self.visible):
            self.frame.pack(pady=20, padx=40, fill='both', expand=True)
            self.visible = True
        else:
            print("Already Visible")

    def hide(self) -> None:
        """ Hides the current frame """
        if(self.visible):        
            self.frame.pack_forget()
            self.visible = False
        else:
            print("Already Hidden")
            
    def cancel_thread(self) -> None:
        """ Basic function to cancel/quit out of process and thread (using flags) """
        if(self.process and self.process.is_alive()):
            self.process.terminate()

        if(self.thread and self.thread.is_alive()):
            self.stop_flag = True
            
    def can_start_thread(self) -> bool:
        """ Check if threading can begin """
        can_we_start = ((self.process is None) or (self.process and (not self.process.is_alive())) and ((self.thread is None) or (self.thread and (not self.thread.is_alive()))))
        if(can_we_start): self.stop_flag = False
        return can_we_start
    
    def get_widgets_to_disable(self):
        all_attribute = dir(self)
        
        to_disable = []        
        for i in range(len(all_attribute)):
            
            object = self.__getattribute__(all_attribute[i])
            if((all_attribute[i]!="quit") and (isinstance(object,ctk.CTkButton) or isinstance(object,ctk.CTkOptionMenu) or isinstance(object,ctk.CTkEntry))):
                to_disable.append(object)
                
        return to_disable

class App:
    """ Main class representing the application """
    
    APP:ctk.CTk = ctk.CTk()    
    TOGGLE:dict[str,tuple[str]] = {'Somaiya':('Teaching','NonTeaching','Temporary'),'SVV':('svv',)}
    CRED:dict = {'host':None,'user':None,'password':None,'database':None}
    MONTH:dict[str,int] = {"jan":1, "feb":2, "mar":3, "apr":4, "may":5, "jun":6, "jul":7, "aug":8, "sept":9, "oct":10, "nov":11, "dec":12}
    DB = Database(ERROR_LOG)
    
    def __init__(self, width:int, height:int, title:str) -> None:
        self.APP.geometry(f"{width}x{height}")
        self.APP.title(title)
        self.CHILD:dict[str,MySQLLogin|SendMail|SendBulkMail|Login|Interface|DataPreview|DataView|FileInput|UploadData] = {UploadData.__name__:UploadData(self),FileInput.__name__:FileInput(self),DataView.__name__:DataView(self),MySQLLogin.__name__:MySQLLogin(self),SendMail.__name__:SendMail(self),SendBulkMail.__name__:SendBulkMail(self),Login.__name__:Login(self),Interface.__name__:Interface(self),MailCover.__name__:MailCover(self),DataPreview.__name__:DataPreview(self)}
    
    """ To start application run this """
    def start_app(self):
        self.CHILD[Login.__name__].appear()
        self.APP.mainloop()
        
    def exit_app(self):
        try:
            self.APP.destroy()
        finally:
            ERROR_LOG.write_info('User Logged Out')

class PDFGenerator:
    """ Class to handle everything related to PDF Generation """
    
    """ Generates the pdf from html """
    def _generate_pdf(self, pdf_file_path:str, html_content:str) -> None:
        pdfkit.from_string(html_content, pdf_file_path,options={
            'page-size': 'A4',
            'margin-top': '0.5in',
            'margin-right': '0.5in',
            'margin-bottom': '0.5in',
            'margin-left': '0.5in',
            'no-outline': None
        })

    """ Wrapper Function to generate one pdf  """
    def generate_one_pdf(self, emp_data:dict[str,str],month:str,year:int,file_path:str) -> tuple[bool,str]:
        
        try:
            os.remove(file_path)
            where = os.path.dirname(file_path)

            filename = f"employee_{emp_data['hr_emp']}.pdf"

            if (re.match(FILE_REGEX,filename)):
                pdf_file = os.path.join(where,filename)
                html_content = HTML_CONTENT + DATA_CONTENT(month,year,emp_data)
                self._generate_pdf(pdf_file, html_content)
                return (True,"PDF Generation Successful")
            else:
                ERROR_LOG.write_info(f"{filename} does not match pattern '{FILE_REGEX}'")
                return (False,f"{filename} does not match pattern '{FILE_REGEX}'")
                
        except Exception as e:
            ERROR_LOG.write_error(ERROR_LOG.get_error_info(e))
            tkmb.showerror("Error", f"An error occurred while generating the PDF: {str(e)}")
            
        return (False,f"An error occurred while generating the PDF: {str(e)}")
            

    """ Wrapper Function to generate multiple pdfs """
    def generate_many_pdf(self, emp_data:dict[str,str],month:str,year:int,where:str) -> tuple[bool,str]:
        
        try:
            filename = f"employee_{emp_data['hr_emp']}.pdf"

            if (re.match(FILE_REGEX,filename)):
                pdf_file = os.path.join(where,filename)
                html_content = HTML_CONTENT + DATA_CONTENT(month,year,emp_data)
                self._generate_pdf(pdf_file, html_content)
                return (True,"PDF Generation Successful")
            else:
                ERROR_LOG.write_info(f"{filename} does not match pattern '{FILE_REGEX}'")
                return (False,f"{filename} does not match pattern '{FILE_REGEX}'")
                
        except Exception as e:
            ERROR_LOG.write_error(ERROR_LOG.get_error_info(e))
            tkmb.showerror("Error", f"An error occurred while generating the PDF: {str(e)}")
            
            return (False,f"An error occurred while generating the PDF: {str(e)}")

class GUI_Handler:
    """ Handles GUI """
    
    def view_excel(self, data: pd.DataFrame, text_excel:scrolledtext.ScrolledText) -> None:
        """ Changes the text on the text excel thing  """
        def replace_new(x:str): return x.replace('\n',"")
        
        text = [[str(i) for i in data.columns]]
        col_widths = {i:len(str(j)) for i,j in enumerate(data.columns)}
        
        for row in data.itertuples(index=False):
            row_data = []
            
            for idx,cell in enumerate(row):
                row_data.append(str(cell))
                col_widths[idx] = max(col_widths[idx],len(str(cell)))
                
            text.append(row_data)
        
        formatted_data = "\n".join([" " + " | ".join([f"{replace_new(cell):^{col_widths[i]}}" for i, cell in enumerate(row)]) + " " for row in text])
        
        text_excel.delete(1.0, tk.END)
        text_excel.insert(tk.END, formatted_data)
        
    def change_text_font(self, text_excel: scrolledtext.ScrolledText, size:int = 15) -> None:
        """ Change the size of text """
        text_excel.configure(font=("Courier", size))
        
    def lock_gui_button(self, buttons:list[ctk.CTkButton]) -> None:
        """ Disable buttons """
        for i in range(len(buttons)):
            buttons[i].configure(state="disabled")
    
    def unlock_gui_button(self, buttons:list[ctk.CTkButton]) -> None:
        """ Enable buttons """
        for i in range(len(buttons)):
            buttons[i].configure(state="normal")

    def change_file_holder(self, file_path_holder:ctk.CTkEntry, new_path:str) -> None:
        """ Change the file path holders """
        file_path_holder.delete(0, tk.END)
        file_path_holder.insert(0,new_path)
        file_path_holder.configure(width=7*len(new_path))
        
    def place_after(self, anchor:ctk.CTkBaseClass, to_place:ctk.CTkBaseClass, padx:int = 10, pady:int = 10) -> None:
        """ Places widget after the anchor widgets """
        to_place.pack_configure(after=anchor,padx=padx,pady=pady)
    
    def place_before(self, anchor:ctk.CTkBaseClass, to_place:ctk.CTkBaseClass, padx:int = 10, pady:int = 10) -> None:
        """ Places widget before the anchor widgets """
        to_place.pack_configure(before=anchor,padx=padx,pady=pady)
        
    def remove_widget(self, this_widget:ctk.CTkBaseClass) -> None:
        """ Remove widget from frame """
        this_widget.pack_forget()
        
    def setOptions(self, new_values:list[str], optionMenu:ctk.CTkOptionMenu, new_variable:ctk.StringVar):
        """ Changes values of optionMenu and  set the corresponding variable to the options """
        optionMenu.configure(values=new_values)
        new_variable.set(new_values[0])
        
    def changeOptions(self, options:list[str], OptionList:ctk.CTkOptionMenu) -> None:
        """ Updates optionmenu with options """
        OptionList.configure(values=options)
        
    def changeCommand(self, widgets:ctk.CTkBaseClass, new_command:types.FunctionType) -> None:
        """ Changes command of a widget """
        widgets.configure(command=new_command)
        
    def changeText(self, widgets:ctk.CTkLabel, text:str) -> None:
        """ Changes text of widgets """
        widgets.configure(text=text)

    def place(self, widget:ctk.CTkBaseClass,padx:int = 10, pady:int = 10) -> None:
        """ Places widget after the last widget present on frame """
        widget.pack(padx=padx,pady=pady)

class Decryption:
    """ Handles file decryption  """
        
    def is_encrypted(self, file:io.BufferedReader) -> bool:
        """ Checks if file is encrypted """
        return msoffcrypto.OfficeFile(file).is_encrypted()
    

    def decrypting_file(self, file_path:str, decrypted:io.BytesIO, password:str) -> tuple[bool,io.BytesIO]:
        """ Decrypts the file and extracts content into BytesIO """
        success = False
        
        with open(file_path, "rb") as f:

            file = msoffcrypto.OfficeFile(f)
            
            try:
                file.load_key(password=password)  
                file.decrypt(decrypted)
                self.prev_password = password
                success = True
                
            except msoffcrypto.exceptions.InvalidKeyError as e:
                ERROR_LOG.write_error(ERROR_LOG.get_error_info(e))
    
            except msoffcrypto.exceptions.DecryptionError as e:
                ERROR_LOG.write_error(ERROR_LOG.get_error_info(e))
            
        return (success,decrypted)
    
    def is_encrypted_wrapper(self, queue: Queue,file_path:str) -> None:
        def process_work():
            if(os.path.isfile(file_path)):
                
                try:
                    with open(file_path,'rb') as f:
                        return self.is_encrypted(f)
                except Exception as e:
                    ERROR_LOG.write_error(ERROR_LOG.get_error_info(e))
            return None
            
        queue.put(process_work())
                
    def fetch_decrypted_file(self, queue: Queue, file_path:str, skip:int = 0) -> None:
        data = pd.read_excel(io=file_path,sheet_name=None,skiprows=skip)
        result = [None,None]
        
        
        if(data):
            sheets = list(data.keys())
            
            for i in sheets:
                dataRefine(data[i])
            
            result[0] = sheets
            result[1] = data
            
        queue.put((result[0],result[1]))
        
    def fetch_encrypted_file(self, queue: Queue, file_path:str, password:str, skip:int = 0) -> None:
        
        result = [None,None]
        with io.BytesIO() as decrypted:
            success, file = self.decrypting_file(file_path,decrypted,password)
        
            if(success):
                
                data = pd.read_excel(io=file,sheet_name=None,skiprows=skip)
                
                if(data):
                    sheets = list(data.keys())
                    
                    for i in sheets:
                        dataRefine(data[i])
                    
                    result[0] = sheets
                    result[1] = data
            
        queue.put((result[0],result[1]))    

class MailingWrapper:
    """ Wrapper for Mailing class """
    
    month = 'jan'
    year = 2024
        
    def change_state(self, month:str, year:int) -> 'MailingWrapper':
        self.month = month
        self.year = year
        return self
    
    def attempt_mail_process(self,pdf_path:str, id:str,toAddr:str,queue:Queue) -> None:
        """ Updates queue when mailing process is done """
        queue.put(self.attemptMail(pdf_path,id,toAddr))
        
    def attemptMail(self, pdf_path:str, id:str,toAddr:str) -> bool:
        """ Sends one email with the pdf file has attachment """
        return Mailing(SMTP_CRED["email"],SMTP_CRED["key"],ERROR_LOG).login().addTxtMsg(f"Please find attached below the salary slip of {self.month.capitalize()}-{self.year}",'plain').addAttach(pdf_path,f'employee_{id}.pdf').addDetails(f"Salary slip of {self.month.capitalize()}-{self.year}").sendMail(toAddr).resetMIME().destroy().status
            
    def _sendMail(self, mail:'Mailing', pdf_path:str, id:str, toAddr:str) -> bool:
        """ Wrapper for continuous mail sending """
        return mail.addTxtMsg(f"Please find attached below the salary slip of {self.month.capitalize()}-{self.year}",'plain').addAttach(pdf_path,f'employee_{id}.pdf').addDetails(f"Salary slip of {self.month.capitalize()}-{self.year}").sendMail(toAddr).resetMIME().status
                
    def massMail(self,email_server:Mailing,data:pd.DataFrame,code_column:str,email_col:str,dir_path:str,queue:Queue) -> None:
        """ Sends email on basis of pdf files present in chosen directory """
                
        count,total = 0, 0
        email_server.login()
        data = PandaGenerator(data,code_column)
        
        try:
            mails = os.listdir(dir_path)
            for mail in mails:
                
                try:
                    find = re.findall(FILE_REGEX,mail)
                    if not find: continue
                    
                    id = find[0]
                    
                    pdf_path = os.path.join(dir_path,mail)
                    if not (os.path.isfile(pdf_path)):
                        continue
                    
                    total+=1
                    
                    toAddr = data[id][email_col].values[0]
                    if self._sendMail(email_server,pdf_path,id,toAddr):
                        count+=1

                except Exception as e:
                    ERROR_LOG.write_error(ERROR_LOG.get_error_info(e))

                queue.put((count,total))
                
        except Exception as e:
            ERROR_LOG.write_error(ERROR_LOG.get_error_info(e))
        
        queue.put("Done")
        email_server.destroy()

class DatabaseWrapper:
    
    DATABASE:Database = Database(ERROR_LOG)
    
    def connectToDatabase(self) -> Database:
        return self.DATABASE.connectDatabase(self.host,self.user,self.password,self.database)
    
    def __init__(self, host:str, user:str, password:str, database:str):
        self.host = host
        self.user = user
        self.password = password
        self.database = database
    
    def check_table(self, queue:Queue) -> None:
        queue.put(self.connectToDatabase().showTables())
        self.endThis()
    
    def get_data(self, queue: Queue,institute:str, type:str, year:int, month:str) -> None:
        queue.put(self.connectToDatabase().fetchAll(month,year,institute,type))
        self.endThis()
        
    def create_table(self, queue: Queue,institute:str, type:str, year:int, month:str, data_columns: list[str]) -> None:
        # create attempt
        create_result = self.connectToDatabase().createData(month,year,data_columns,institute,type)
        queue.put(create_result)
        self.endThis()
        
    def fill_table(self, queue: Queue,institute:str, type:str, year:int, month:str, data: pd.DataFrame):
        """ Attempts to insert data or update data in db (Doesn't ask for updation)"""
        upsert_result = self.connectToDatabase().updateData(data,month,year,institute,type)
        queue.put(upsert_result)
        self.endThis()
        
    def delete_table(self, queue: Queue,institute:str, type:str, year:int, month:str):
        """ Delete Table """
        delete_result = self.connectToDatabase().dropTable(institute,type,month,year)
        queue.put(delete_result)
        self.endThis()
        
    def endThis(self):
        self.DATABASE.endDatabase()
        
class PandaGeneratorWrapper:
    """ PandasGenerator wrapper for process (aka Warhammer Class) """
    def __init__(self, servitor:PandaGenerator) -> None:
        self.servitor = servitor
    
    def find_by_id(self, queue: Queue,emp_id:str):
        if(emp_id in self.servitor):
            queue.put(self.litany_of_auspex(emp_id))
        else:
            queue.put(self.litany_of_failure())
            
    def litany_of_failure(self): 
        """ The labyrith does not bears the knowledge you wish too seek, Tech Adept """
        return None
    
    def litany_of_auspex(self, index:str):
        """ Praised be the machine spirit of the blessed augurs (Returns data about id, which should exist)"""
        return self.servitor[index]
    
    def litany_of_scrolls(self, queue: Queue,dropzone:str,month:str,year:int):
        """ Oh holy generator, grants us the sacred ink of thou's blessed blood (BulkPrint Process)"""
        column_auspex = get_salary_column(sorted(self.servitor.columns.keys(),key=len))
        task_completed = 0
        total_task = self.servitor.data.shape[0]
        for data in self.servitor:
            
            emp_data = {key:data[val].values[0] if val else val for key,val in column_auspex.items()}
            task_success, _ = PDFGenerator().generate_many_pdf(emp_data,month,year,dropzone)
            task_completed += task_success
            queue.put((task_completed,total_task))
        
        queue.put((None,None))
        
    def litany_of_scroll(self, queue: Queue, data_slate_path:str, month:str, year:int, emp_id:str):
        column_auspex = get_salary_column(sorted(self.servitor.columns.keys(),key=len))
        data = self.litany_of_auspex(emp_id) if (emp_id in self.servitor.dict_iter()) else self.litany_of_failure()
        
        if(data is not None):
            emp_data = {key:data[val].values[0] if val else val for key,val in column_auspex.items()}
            status,msg = PDFGenerator().generate_one_pdf(emp_data,month,year,data_slate_path)
            queue.put((status,msg))
            
        else:
            queue.put((None,"Data not available"))

class MailCover(BaseTemplate):
    """ Mailing Cover to choose either single-mailing / bulk-mailing """
    
    def __init__(self,outer:App):
        self.outer = outer    
        master = self.outer.APP
        self.frame = ctk.CTkScrollableFrame(master=master,fg_color=custom_color_scheme["fg_color"])
        
        ctk.CTkLabel(master=self.frame , text="Select mailing option", text_color=custom_color_scheme["text_color"], font=("Ubuntu", 16, "bold"),width=250).pack(pady=10)
        ctk.CTkButton(master=self.frame, text='Single Mail', command=self.single, fg_color=custom_color_scheme["button_color"], font=("Ubuntu", 16, "bold"),width=250).pack(pady=10, padx=10)
        ctk.CTkButton(master=self.frame, text='Bulk Mail', command=self.many, fg_color=custom_color_scheme["button_color"], font=("Ubuntu", 16, "bold"),width=250).pack(pady=10, padx=10)
        ctk.CTkButton(master=self.frame, text='Back', command=self.back_to_landing, fg_color=custom_color_scheme["button_color"], font=("Ubuntu", 16, "bold"),width=250).pack(pady=10, padx=10)

    def single(self) -> None:
        """ Redirect to Single Mailing """
        self.hide()
        self.outer.CHILD[SendMail.__name__].appear()
    
    def many(self) -> None:
        """ Redirect to Bulk Mailing """
        self.hide()
        # self.outer.CHILD[SendMails.__name__].appear()

    # back to landing
    def back_to_landing(self) -> None:
        self.hide() 
        # self.outer.CHILD[Landing.__name__].appear()

class SendMail(BaseTemplate):
    """ Page for single mail """    
    chosen_institute = ctk.StringVar(value='Somaiya')
    chosen_type = ctk.StringVar(value='Teaching')
    chosen_month = ctk.StringVar(value='Jan')   
    
    def __init__(self,outer:App):
        self.outer = outer
        master = self.outer.APP
        self.frame = ctk.CTkScrollableFrame(master=master,fg_color=custom_color_scheme["fg_color"])
        
        ctk.CTkLabel(master=self.frame , text="Single Mail", text_color=custom_color_scheme["text_color"], font=("Ubuntu", 25, "bold"),width=250).pack(pady=20,padx=10)
        
        frame = ctk.CTkFrame(master=self.frame, fg_color=custom_color_scheme["fg_color"])
        ctk.CTkLabel(master=frame , text="Selected PDF File:", text_color=custom_color_scheme["text_color"], font=("Ubuntu", 16, "bold")).pack(padx=10,pady=10,side='left')
        self.file = ctk.CTkEntry(master=frame , width=100, text_color=custom_color_scheme["text_color"], font=("Ubuntu", 16, "bold"))
        self.file.pack(padx=10,pady=10,side='left')
        frame.pack()
        
        self.browse_button = ctk.CTkButton(master=self.frame , text="Browse", command=self.browse_file, fg_color=custom_color_scheme["button_color"], font=("Ubuntu", 16, "bold"),width=250)
        self.browse_button.pack(pady=10)
        
        frame = ctk.CTkFrame(master=self.frame, fg_color=custom_color_scheme["fg_color"])
        ctk.CTkLabel(master=frame, text="Institute:", text_color=custom_color_scheme["text_color"], font=("Ubuntu", 16, "bold")).pack(padx=10,pady=10,side='left')
        ctk.CTkOptionMenu(master=frame,variable=self.chosen_institute,values=list(self.outer.TOGGLE.keys()),command=self.changeType,button_color=custom_color_scheme["button_color"],fg_color=custom_color_scheme["button_color"], font=("Ubuntu", 16, "bold"),width=250).pack(pady=10, padx=10)
        frame.pack()
        
        frame = ctk.CTkFrame(master=self.frame, fg_color=custom_color_scheme["fg_color"])
        ctk.CTkLabel(master=frame, text="Type:", text_color=custom_color_scheme["text_color"], font=("Ubuntu", 16, "bold")).pack(padx=10,pady=10,side='left')
        self.toggle_type = ctk.CTkOptionMenu(master=frame,variable=self.chosen_type,values=self.outer.TOGGLE[list(self.outer.TOGGLE.keys())[0]][0],button_color=custom_color_scheme["button_color"],fg_color=custom_color_scheme["button_color"], font=("Ubuntu", 16, "bold"),width=250)
        self.toggle_type.pack(pady=10, padx=10)
        frame.pack()
        
        frame = ctk.CTkFrame(master=self.frame, fg_color=custom_color_scheme["fg_color"])
        ctk.CTkLabel(master=frame, text="Month:", text_color=custom_color_scheme["text_color"], font=("Ubuntu", 16, "bold")).pack(padx=10,pady=10,side='left')
        ctk.CTkOptionMenu(master=frame,variable=self.chosen_month,values=[str(i).capitalize() for i in self.outer.MONTH],button_color=custom_color_scheme["button_color"],fg_color=custom_color_scheme["button_color"], font=("Ubuntu", 16, "bold"),width=250).pack(pady=10, padx=10)
        frame.pack()
        
        frame = ctk.CTkFrame(master=self.frame, fg_color=custom_color_scheme["fg_color"])
        ctk.CTkLabel(master=frame , text="Enter Year:", text_color=custom_color_scheme["text_color"], font=("Ubuntu", 16, "bold")).pack(side='left',pady=10, padx=10)
        self.year = ctk.CTkEntry(master=frame ,placeholder_text="Eg. 2024", text_color=custom_color_scheme["text_color"], font=("Ubuntu", 16, "bold"),width=100)
        self.year.pack(side='left',pady=10, padx=10)
        frame.pack()
        
        frame = ctk.CTkFrame(master=self.frame, fg_color=custom_color_scheme["fg_color"])
        ctk.CTkLabel(master=frame , text="Enter Employee ID:", text_color=custom_color_scheme["text_color"], font=("Ubuntu", 16, "bold")).pack(side='left',pady=10, padx=10)
        self.emp_id = ctk.CTkEntry(master=frame ,placeholder_text="Eg. 2200317", text_color=custom_color_scheme["text_color"], font=("Ubuntu", 16, "bold"),width=150)
        self.emp_id.pack(side='left',pady=10, padx=10)
        frame.pack()
        
        frame = ctk.CTkFrame(master=self.frame, fg_color=custom_color_scheme["fg_color"])
        ctk.CTkLabel(master=frame , text="Enter Employee Email:", text_color=custom_color_scheme["text_color"], font=("Ubuntu", 16, "bold")).pack(side='left',pady=10, padx=10)
        self.email = ctk.CTkEntry(master=frame ,placeholder_text="Eg. asd@somaiya.edu", text_color=custom_color_scheme["text_color"], font=("Ubuntu", 16, "bold"),width=250)
        self.email.pack(side='left',pady=10, padx=10)
        frame.pack()
        
        send_button = ctk.CTkButton(master=self.frame , text='Send Mail', command=self.send_mail, fg_color=custom_color_scheme["button_color"], font=("Ubuntu", 16, "bold"),width=250)
        send_button.pack(pady=10,padx=10)
        
        ctk.CTkButton(master=self.frame , text='Back', command=self.back, fg_color=custom_color_scheme["button_color"], font=("Ubuntu", 16, "bold"),width=250).pack(pady=10,padx=10)
        
        self.quit = ctk.CTkButton(master=self.frame,text='Quit the process',command=self.cancel_thread_wrapper,fg_color=custom_color_scheme["button_color"], font=("Ubuntu", 16, "bold"),width=250)
        
        self.to_disable = self.get_widgets_to_disable()
        
    def cancel_thread_wrapper(self) -> None:
        self.cancel_thread()
        
        GUI_Handler().unlock_gui_button(self.to_disable)
        GUI_Handler().remove_widget(self.quit)
        tkmb.showinfo('Email Status','Email Sending Stopped')
            
            
    def send_mail_thread_wrapper(self) -> None:
        GUI_Handler().lock_gui_button(self.to_disable)
        GUI_Handler().place_after(self.browse_button,self.quit)
        done = None
        
        while True:
            
            if(self.stop_flag): return None
            
            try:
                done = self.QUEUE.get(block=False)
                break
            
            except: pass
            
        GUI_Handler().unlock_gui_button(self.to_disable)
        GUI_Handler().remove_widget(self.quit)
        
        if(done):
            tkmb.showinfo('Email Status',"Email Send Successfully")
        else:
            tkmb.showinfo('Email Status','Email was not send successfully')
        
        
    def changeType(self, event:tk.Event = None):
        institute = self.chosen_institute.get()
        type = self.outer.TOGGLE[institute]
        GUI_Handler().setOptions(type,self.toggle_type,self.chosen_type)

    def send_mail(self) -> None:

        file_path = self.file.get()
        toAddr = self.email.get()
        month = self.chosen_month.get()
        year = self.year.get()
        id = self.emp_id.get()
        
        if(not YEAR_CHECK(year)):
            tkmb.showwarning('Year Check','Improper Year format')
            return
        
        if(not EMAIL_REGEX(toAddr)):
            tkmb.showwarning('Email Check',"Improper Email Address format")
            return
        
        if(not (re.match(r'^(\w+|\d+)$',id))):
            tkmb.showwarning('Employee ID check','Improper Employee ID format')
        
        if(self.can_start_thread()):
            self.process = Process(target=MailingWrapper().change_state(month,year).attempt_mail_process,kwargs={'pdf_path': file_path,'toAddr': toAddr,'id': id,'queue':self.QUEUE},daemon=True)
            self.thread = Thread(target=self.send_mail_thread_wrapper,daemon=True)
            self.stop_flag = False
            self.thread.start()
            self.process.start()

    def browse_file(self) -> None:
        """ Browse for file to send """
        file_path = filedialog.askopenfilename(filetypes=[("PDF Files", ".pdf")],initialdir=APP_PATH)
        
        if file_path:
            GUI_Handler().change_file_holder(self.file,file_path)
            
    # back button
    def back(self) -> None:
        self.hide()
        self.outer.CHILD[MailCover.__name__].appear()

class SendBulkMail(BaseTemplate):
    """ Page for Bulk Mailing """
    chosen_institute = ctk.StringVar(value='Somaiya')
    chosen_type = ctk.StringVar(value='Teaching')
    chosen_month = ctk.StringVar(value='Jan')  
    email_server = Mailing(SMTP_CRED['email'],SMTP_CRED['key'],ERROR_LOG)
    count, total = 0, 0
    
    def __init__(self,outer:App):
        self.outer = outer
        master = self.outer.APP
        
        self.frame = ctk.CTkScrollableFrame(master=master, fg_color=custom_color_scheme["fg_color"])

        ctk.CTkLabel(master=self.frame , text="Bulk Mail", text_color=custom_color_scheme["text_color"], font=("Ubuntu", 25, "bold"),width=250).pack(pady=20,padx=10)

        frame = ctk.CTkFrame(master=self.frame, fg_color=custom_color_scheme["fg_color"])
        ctk.CTkLabel(master=frame , text="Selected Folder Location:", text_color=custom_color_scheme["text_color"], font=("Ubuntu", 16, "bold")).pack(padx=10,pady=10,side='left')
        self.folder = ctk.CTkEntry(master=frame , width=100, text_color=custom_color_scheme["text_color"], font=("Ubuntu", 16, "bold"))
        self.folder.pack(padx=10,pady=10,side='left')
        frame.pack()
        
        self.browse_button = ctk.CTkButton(master=self.frame , text='Browse', command=self.folder_browse, fg_color=custom_color_scheme["button_color"], font=("Ubuntu", 16, "bold"),width=250)
        self.browse_button.pack(pady=10)
        
        frame = ctk.CTkFrame(master=self.frame, fg_color=custom_color_scheme["fg_color"])
        ctk.CTkLabel(master=frame, text="Institute:", text_color=custom_color_scheme["text_color"], font=("Ubuntu", 16, "bold")).pack(padx=10,pady=10,side='left')
        self.entry_institute =ctk.CTkOptionMenu(master=frame,variable=self.chosen_institute,values=list(self.outer.TOGGLE.keys()),command=self.changeType,button_color=custom_color_scheme["button_color"],fg_color=custom_color_scheme["button_color"], font=("Ubuntu", 16, "bold"),width=250)
        self.entry_institute.pack(pady=10, padx=10,side='left')
        frame.pack()
        
        frame = ctk.CTkFrame(master=self.frame, fg_color=custom_color_scheme["fg_color"])
        ctk.CTkLabel(master=frame, text="Type:", text_color=custom_color_scheme["text_color"], font=("Ubuntu", 16, "bold")).pack(padx=10,pady=10,side='left')
        self.toggle_type = ctk.CTkOptionMenu(master=frame,variable=self.chosen_type,values=self.outer.TOGGLE[list(self.outer.TOGGLE.keys())[0]][0],button_color=custom_color_scheme["button_color"],fg_color=custom_color_scheme["button_color"], font=("Ubuntu", 16, "bold"),width=250)
        self.toggle_type.pack(pady=10, padx=10,side='left')
        frame.pack()
        
        frame = ctk.CTkFrame(master=self.frame, fg_color=custom_color_scheme["fg_color"])
        ctk.CTkLabel(master=frame, text="Month:", text_color=custom_color_scheme["text_color"], font=("Ubuntu", 16, "bold")).pack(padx=10,pady=10,side='left')
        self.entry_month = ctk.CTkOptionMenu(master=frame,variable=self.chosen_month,values=[str(i).capitalize() for i in self.outer.MONTH],button_color=custom_color_scheme["button_color"],fg_color=custom_color_scheme["button_color"], font=("Ubuntu", 16, "bold"),width=250)
        self.entry_month.pack(pady=10, padx=10,side='left')
        frame.pack()
        
        frame = ctk.CTkFrame(master=self.frame, fg_color=custom_color_scheme["fg_color"])
        ctk.CTkLabel(master=frame , text="Enter Year:", text_color=custom_color_scheme["text_color"], font=("Ubuntu", 16, "bold")).pack(side='left',pady=10, padx=10)
        self.entry_year = ctk.CTkEntry(master=frame ,placeholder_text="Eg. 2024", text_color=custom_color_scheme["text_color"], font=("Ubuntu", 16, "bold"),width=100)
        self.entry_year.pack(side='left',pady=10, padx=10)
        frame.pack()
        
        mail_button = ctk.CTkButton(master=self.frame , text='Send Emails', command=self.sendEvery, fg_color=custom_color_scheme["button_color"], font=("Ubuntu", 16, "bold"),width=250)
        mail_button.pack(pady=10, padx=10)
        
        self.quit = ctk.CTkButton(master=self.frame,text='Quit the process',command=self.cancel_thread_wrapper,fg_color=custom_color_scheme["button_color"], font=("Ubuntu", 16, "bold"),width=250)
        
        ctk.CTkButton(master=self.frame , text='Back', command=self.button_mailing, fg_color=custom_color_scheme["button_color"], font=("Ubuntu", 16, "bold"),width=250).pack(pady=10, padx=10)
        self.to_disable = self.get_widgets_to_disable()
        
        
    def changeType(self, event:tk.Event = None):
        institute = self.chosen_institute.get()
        type = self.outer.TOGGLE[institute]
        GUI_Handler().setOptions(type,self.toggle_type,self.chosen_type)
        
    def cancel_thread_wrapper(self) -> None:
        self.cancel_thread()
        
        GUI_Handler().unlock_gui_button(self.to_disable)
        GUI_Handler().remove_widget(self.quit)
        tkmb.showinfo('Email Status','Email Sending Stopped')
        self.email_result(self.count,self.total)
            
    def send_mail_thread_wrapper(self) -> None:
        GUI_Handler().lock_gui_button(self.to_disable)
        GUI_Handler().place_after(self.browse_button,self.quit)
        
        while True:
            
            if(self.stop_flag): return None
            
            try:
                curr = self.QUEUE.get()
            
                if(curr=="Done"):
                    break
                elif(isinstance(curr,tuple[int,int])):
                    self.count, self.total = curr
                
            except: pass
        
        GUI_Handler().unlock_gui_button(self.to_disable)
        GUI_Handler().remove_widget(self.quit)
        self.email_result(self.count,self.total)
    
    
    def email_result(self, count:int, total:int) -> None:
        if(self.count>0):
            tkmb.showinfo('Email Status',f"{count}/{total} emails were send successfully")
        elif(self.total>0):
            tkmb.showinfo('Email Status','No emails were send')
        else:
            tkmb.showinfo('Email Status',f"No pdf files of format '{FILE_REGEX}' were found")
        
    
    def changeType(self, event:tk.Event = None):
        institute = self.chosen_institute.get()
        type = self.outer.TOGGLE[institute]
        GUI_Handler().setOptions(type,self.toggle_type,self.chosen_type)

    def send_mail(self) -> None:

        file_path = self.folder.get()
        month = self.chosen_month.get()
        year = self.year.get()
        
        if(not YEAR_CHECK(year)):
            tkmb.showwarning('Year Check','Improper Year format')
            return
                
        if((self.process is None) or (self.process and (not self.process.is_alive)) and (self.thread is None) or (self.thread and (not self.thread.is_alive))):
            self.process = Process(target=MailingWrapper().change_state(month,year).attempt_mail_process,kwargs={'pdf_path': file_path,'toAddr': toAddr,'id': id,'queue':self.QUEUE},daemon=True)
            self.thread = Thread(target=self.send_mail_thread_wrapper,daemon=True)
            
            self.thread.start()
            self.process.start()

    def folder_browse(self) -> None:
        current_dir = os.path.dirname(APP_PATH)
        entry_folder = filedialog.askdirectory(initialdir=current_dir)

        if entry_folder:
            GUI_Handler().change_file_holder(self.folder,entry_folder)


    # back button
    def button_mailing(self) -> None:
        self.hide()
        self.outer.CHILD[MailCover.__name__].appear()
        

    # fetches data from the chosen table
    def sendEvery(self) -> None:
        month = self.month.get().lower()
        year = self.year.get()
        chosen = self.chosen.get().lower()
        type_ = self.type_.get().lower()
        pdf_path = self.folder.get()
        
        global stop_email
        
        if YEAR_CHECK(year):
            data = self.outer.db.fetchAll(month,year,chosen,type_)
        else:
            tkmb.showwarning("Alert","Incorrect year format")
            return
            
        if data is not None:
            email_col = mapping(data,'email mail')
            code_col = mapping(data,'hr emp code')

            if email_col and code_col:
                
                if((self.thread is None) or (not(self.thread and self.thread.is_alive()))):
                    stop_email = False
                    self.thread = Thread(daemon=True,target=MailSending(month=month,year=year,type_=type_,insti=chosen).massMail,kwargs={'data':data,'code_column': code_col,'email_col': email_col,'pdf_path': pdf_path,'caller': self.mass_mail,'quit':self.stop_email})
                    self.thread.start()
            else:
                tkmb.showerror('Data Status','Data in DB does not have either HR EMP CODE/Email column')

        else:
            tkmb.showerror('Data Status','Data is not present in DB.\n Please upload data to DB')

class Login(BaseTemplate):
    """ Login Page """
    
    def __init__(self,outer:App) -> None:
        self.outer = outer
        master = self.outer.APP
        
        self.frame = ctk.CTkScrollableFrame(master=master, fg_color=custom_color_scheme["fg_color"])

        ctk.CTkLabel(master=self.frame , text="Admin Login Page", text_color=custom_color_scheme["text_color"], font=("Ubuntu", 25, "bold"),width=250).pack(pady=20,padx=10)
        
        frame = ctk.CTkFrame(master=self.frame, fg_color=custom_color_scheme["fg_color"])
        ctk.CTkLabel(master=frame,text="Username:", text_color=custom_color_scheme["text_color"], font=("Ubuntu", 16, "bold")).pack(padx=10,pady=10,side='left')
        self.user_entry = ctk.CTkEntry(master=frame,placeholder_text="Username" , width=250, text_color=custom_color_scheme["text_color"], font=("Ubuntu", 16, "bold"))
        self.user_entry.pack(padx=10,pady=10,side='left')
        frame.pack()
        
        frame = ctk.CTkFrame(master=self.frame, fg_color=custom_color_scheme["fg_color"])
        ctk.CTkLabel(master=frame , text="Password:", text_color=custom_color_scheme["text_color"], font=("Ubuntu", 16, "bold")).pack(padx=10,pady=10,side='left')
        self.user_password = ctk.CTkEntry(master=frame,placeholder_text="Password" ,show="*",width=250, text_color=custom_color_scheme["text_color"], font=("Ubuntu", 16, "bold"))
        self.user_password.pack(padx=10,pady=10,side='left')
        frame.pack()

        ctk.CTkButton(master=self.frame, text='Login', command=self.login, fg_color=custom_color_scheme["button_color"], font=("Ubuntu", 16, "bold"),width=250).pack(pady=10, padx=10)
        ctk.CTkButton(master=self.frame, text='Exit', command=self.quit, fg_color=custom_color_scheme["button_color"], font=("Ubuntu", 16, "bold"),width=250).pack(pady=10, padx=10)
        
        self.to_disable = self.get_widgets_to_disable()

    def login(self) -> None:
        """ Check username and password """
        known_user = 'admin' # actual username
        known_pass = 'kjs2024' # actual password
        
        username = self.user_entry.get() if not IS_DEBUG else known_user
        password = self.user_password.get() if not IS_DEBUG else known_pass
        
        if(not username or not password):
            tkmb.showwarning(title='Empty Field', message='Please fill the all fields')

        if known_user == username and known_pass == password:
            tkmb.showinfo(title="Login Successful", message="You have logged in Successfully")
            ERROR_LOG.write_info('User Logged in')
            self.hide()
            self.outer.CHILD[MySQLLogin.__name__].appear()
            
        else:
            tkmb.showwarning(title='Wrong password', message='Please check your username/password')

    def quit(self):
        if messagebox.askyesnocancel("Confirmation", f"Are you sure you want to exit"):
            self.outer.APP.quit()

class MySQLLogin(BaseTemplate):
    def __init__(self,outer:App) -> None:
        self.outer = outer
        master = self.outer.APP
        
        self.frame = ctk.CTkScrollableFrame(master=master, fg_color=custom_color_scheme["fg_color"])

        ctk.CTkLabel(master=self.frame , text="MySQL Login Page", text_color=custom_color_scheme["text_color"], font=("Ubuntu", 25, "bold"),width=250).pack(pady=20,padx=10)

        frame = ctk.CTkFrame(master=self.frame, fg_color=custom_color_scheme["fg_color"])
        ctk.CTkLabel(master=frame,text="Host:", text_color=custom_color_scheme["text_color"], font=("Ubuntu", 16, "bold")).pack(padx=10,pady=10,side='left')
        self.host = ctk.CTkEntry(master=frame ,placeholder_text="Host", width=250, text_color=custom_color_scheme["text_color"], font=("Ubuntu", 16, "bold"))
        self.host.insert(0,"localhost")
        self.host.pack(padx=10,pady=10,side='left')
        frame.pack()
        
        frame = ctk.CTkFrame(master=self.frame, fg_color=custom_color_scheme["fg_color"])
        ctk.CTkLabel(master=frame,text="Username:", text_color=custom_color_scheme["text_color"], font=("Ubuntu", 16, "bold")).pack(padx=10,pady=10,side='left')
        self.user = ctk.CTkEntry(placeholder_text="Username",master=frame , width=250, text_color=custom_color_scheme["text_color"], font=("Ubuntu", 16, "bold"))
        self.user.insert(0,"root")
        self.user.pack(padx=10,pady=10,side='left')
        frame.pack()
        
        frame = ctk.CTkFrame(master=self.frame, fg_color=custom_color_scheme["fg_color"])
        ctk.CTkLabel(master=frame,text="Password:", text_color=custom_color_scheme["text_color"], font=("Ubuntu", 16, "bold")).pack(padx=10,pady=10,side='left')
        self.password = ctk.CTkEntry(master=frame,placeholder_text="Password" , width=250, text_color=custom_color_scheme["text_color"], font=("Ubuntu", 16, "bold"))
        self.password.pack(padx=10,pady=10,side='left')
        frame.pack()
        
        frame = ctk.CTkFrame(master=self.frame, fg_color=custom_color_scheme["fg_color"])
        ctk.CTkLabel(master=frame,text="Database:", text_color=custom_color_scheme["text_color"], font=("Ubuntu", 16, "bold")).pack(padx=10,pady=10,side='left')
        self.database = ctk.CTkEntry(master=frame, placeholder_text="Database" , width=250, text_color=custom_color_scheme["text_color"], font=("Ubuntu", 16, "bold"))
        self.database.pack(padx=10,pady=10,side='left')
        frame.pack()
        
        ctk.CTkButton(master=self.frame, text='Continue', command=self.next, fg_color=custom_color_scheme["button_color"], font=("Ubuntu", 16, "bold"),width=250).pack(pady=10, padx=10)
        ctk.CTkButton(master=self.frame, text='Back', command=self.back, fg_color=custom_color_scheme["button_color"], font=("Ubuntu", 16, "bold"),width=250).pack(pady=10, padx=10)
        self.to_disable = self.get_widgets_to_disable()

    # back to login page
    def back(self):
        self.hide()
        self.outer.CHILD[Login.__name__].appear()
            
    # moves to next page (landing) is mysql connection was established
    def next(self):
        self.outer.CRED['host'] = self.host.get() if not IS_DEBUG else MYSQL_CRED['host']
        self.outer.CRED['user'] = self.user.get() if not IS_DEBUG else MYSQL_CRED['user']
        self.outer.CRED['password'] = self.password.get() if not IS_DEBUG else MYSQL_CRED['password']
        self.outer.CRED['database'] = self.database.get() if not IS_DEBUG else MYSQL_CRED['database']
        
        if(self.outer.CRED['host'] and self.outer.CRED['user'] and self.outer.CRED['password'] and self.outer.CRED['database']):
        
            if(self.outer.DB.connectDatabase(host=self.outer.CRED['host'],user=self.outer.CRED['user'],password=self.outer.CRED['password'],database=self.outer.CRED['database']).status):
                tkmb.showinfo('MySQL Status','MySQL Connection Established')
                self.hide()
                self.outer.CHILD[Interface.__name__].appear()
            else:
                tkmb.showinfo('MySQL Status','MySQL Connection Failed')
        
        else:
            tkmb.showwarning(title='Empty Field', message='Please fill the all fields')

class Interface(BaseTemplate):
    def __init__(self,outer:App) -> None:
        self.outer = outer
        master = self.outer.APP
        
        self.frame = ctk.CTkScrollableFrame(master=master, fg_color=custom_color_scheme["fg_color"])
        
        ctk.CTkLabel(master=self.frame , text="Excel-To-PDF Generator", text_color=custom_color_scheme["text_color"], font=("Ubuntu", 25, "bold"),width=250).pack(pady=20,padx=10)
        
        self.preview_db = ctk.CTkButton(master=self.frame , text='Preview Existing Data', command=self.preview, fg_color=custom_color_scheme["button_color"], font=("Ubuntu", 16, "bold"),width=250)
        self.preview_db.pack(pady=10, padx=10)
        
        upload = ctk.CTkButton(master=self.frame , text='Upload Excel data', command=self.upload, fg_color=custom_color_scheme["button_color"], font=("Ubuntu", 16, "bold"),width=250)
        upload.pack(pady=10, padx=10)
        
        mail = ctk.CTkButton(master=self.frame , text='Send Mail', command=self.mail, fg_color=custom_color_scheme["button_color"], font=("Ubuntu", 16, "bold"),width=250)
        mail.pack(pady=10, padx=10)
        
        self.back = ctk.CTkButton(master=self.frame , text='Back', command=self.back_to_mysql, fg_color=custom_color_scheme["button_color"], font=("Ubuntu", 16, "bold"),width=250)
        self.back.pack(pady=10, padx=10)
        
        self.quit = ctk.CTkButton(master=self.frame,text='Quit the process',command=self.cancel_thread_wrapper,fg_color=custom_color_scheme["button_color"], font=("Ubuntu", 16, "bold"),width=250)
        self.to_disable = self.get_widgets_to_disable()
        
    # back to mysql setup page
    def back_to_mysql(self) -> None:
        self.hide()
        self.outer.CHILD[MySQLLogin.__name__].appear()

    # proceeds to upload page
    def upload(self) -> None:
        self.hide()
        self.outer.CHILD[FileInput.__name__].appear()

    def mail(self) -> None:
        self.hide()
        self.outer.CHILD[MailCover.__name__].appear()
    
    def check_database_thread(self):
        GUI_Handler().lock_gui_button(self.to_disable)
        GUI_Handler().place_after(self.preview_db,self.quit)
        table = {}
        
        while True:
            if(self.stop_flag): return None
            
            try:
                table = self.QUEUE.get(block=False)
                break
            except: pass
        
        GUI_Handler().unlock_gui_button(self.to_disable)
        GUI_Handler().remove_widget(self.quit)
        if(table):
            self.outer.CHILD[DataPreview.__name__].appear()
            self.outer.CHILD[DataPreview.__name__].tables = table
            self.outer.CHILD[DataPreview.__name__].changeData()
            self.hide()
        else:
            tkmb.showerror("MySQL Error","No Data Available to preview")
    
    def cancel_thread_wrapper(self) -> None:
        self.cancel_thread()
        
        GUI_Handler().unlock_gui_button(self.to_disable)
        GUI_Handler().remove_widget(self.quit)
        tkmb.showinfo('Fetch Status','Data Fetching Stopped')

    # proceeds to pre-existing data page
    def preview(self) -> None:
        
        if(self.can_start_thread()):
            self.process = Process(target=DatabaseWrapper(**self.outer.CRED).check_table,kwargs={'queue':self.QUEUE},daemon=True)
            self.thread = Thread(target=self.check_database_thread,daemon=True)
            self.stop_flag = False
            self.thread.start()
            self.process.start()

class DataPreview(BaseTemplate):
    """ Previews data in database """
    entry_year = ctk.StringVar(value='2024')
    entry_month = ctk.StringVar(value='Jan')
    entry_institute = ctk.StringVar(value='Somaiya')
    entry_type = ctk.StringVar(value='Teaching')
    tables:dict[str,dict[str,dict[str,set[str]]]] = {}
    
    def __init__(self,outer:App) -> None:
        self.outer = outer
        master = self.outer.APP
        self.frame = ctk.CTkScrollableFrame(master=master, fg_color=custom_color_scheme["fg_color"])

        ctk.CTkLabel(master=self.frame , text="Data Preview", text_color=custom_color_scheme["text_color"], font=("Ubuntu", 25, "bold"),width=250).pack(pady=20,padx=10)
        
        frame = ctk.CTkFrame(master=self.frame, fg_color=custom_color_scheme["fg_color"])
        ctk.CTkLabel(master=frame, text="Institute:", text_color=custom_color_scheme["text_color"], font=("Ubuntu", 16, "bold")).pack(padx=10,pady=10,side='left')
        self.entry_instituteList = ctk.CTkOptionMenu(master=frame,variable=self.entry_institute,values=[],command=self.changeInstitute,button_color=custom_color_scheme["button_color"],fg_color=custom_color_scheme["button_color"], font=("Ubuntu", 16, "bold"),width=200)
        self.entry_instituteList.pack(padx=10,pady=10,side='left')
        frame.pack()
        
        frame = ctk.CTkFrame(master=self.frame, fg_color=custom_color_scheme["fg_color"])
        ctk.CTkLabel(master=frame, text="Type:", text_color=custom_color_scheme["text_color"], font=("Ubuntu", 16, "bold")).pack(padx=10,pady=10,side='left')
        self.entry_typeList = ctk.CTkOptionMenu(master=frame,variable=self.entry_type,values=[],command=self.changeType,button_color=custom_color_scheme["button_color"],fg_color=custom_color_scheme["button_color"], font=("Ubuntu", 16, "bold"),width=200)
        self.entry_typeList.pack(padx=10,pady=10,side='left')
        frame.pack()
        
        frame = ctk.CTkFrame(master=self.frame, fg_color=custom_color_scheme["fg_color"])
        ctk.CTkLabel(master=frame, text="Year:", text_color=custom_color_scheme["text_color"], font=("Ubuntu", 16, "bold")).pack(padx=10,pady=10,side='left')
        self.entry_yearList = ctk.CTkOptionMenu(master=frame,variable=self.entry_year,values=[],command=self.changeYear,button_color=custom_color_scheme["button_color"],fg_color=custom_color_scheme["button_color"], font=("Ubuntu", 16, "bold"),width=200)
        self.entry_yearList.pack(padx=10,pady=10,side='left')
        frame.pack()
        
        frame = ctk.CTkFrame(master=self.frame, fg_color=custom_color_scheme["fg_color"])
        ctk.CTkLabel(master=frame, text="Month:", text_color=custom_color_scheme["text_color"], font=("Ubuntu", 16, "bold")).pack(padx=10,pady=10,side='left')
        self.entry_monthList = ctk.CTkOptionMenu(master=frame,variable=self.entry_month,values=[],button_color=custom_color_scheme["button_color"],fg_color=custom_color_scheme["button_color"], font=("Ubuntu", 16, "bold"),width=200)
        self.entry_monthList.pack(padx=10,pady=10,side='left')
        frame.pack()
        
        self.fetch_data = ctk.CTkButton(master=self.frame , text='Continue', command=self.getData, fg_color=custom_color_scheme["button_color"], font=("Ubuntu", 16, "bold"),width=250)
        self.fetch_data.pack(pady=10, padx=10)
        
        ctk.CTkButton(master=self.frame , text='Back', command=self.back_to_interface, fg_color=custom_color_scheme["button_color"], font=("Ubuntu", 16, "bold"),width=250).pack(pady=10, padx=10)
        self.quit = ctk.CTkButton(master=self.frame,text='Quit the process',command=self.cancel_thread_wrapper,fg_color=custom_color_scheme["button_color"], font=("Ubuntu", 16, "bold"),width=250)
        self.to_disable = self.get_widgets_to_disable()
        
        
    def back_to_interface(self) -> None:
        """ Moves back to the earlier page """
        self.hide()
        self.outer.CHILD[Interface.__name__].appear()
            
    def changeData(self):
        """ Initialization of the optionmenus """        
        curr_institute = list(self.tables.keys())
        curr_type = list(self.tables[curr_institute[0]].keys())
        curr_year = list(self.tables[curr_institute[0]][curr_type[0]].keys())
        curr_month = sorted(list(self.tables[curr_institute[0]][curr_type[0]][curr_year[0]]),key=lambda x:self.outer.MONTH[x])
        
        GUI_Handler().setOptions(curr_type,self.entry_typeList,self.entry_type)
        GUI_Handler().setOptions(curr_institute,self.entry_instituteList,self.entry_institute)
        GUI_Handler().setOptions(curr_year,self.entry_yearList,self.entry_year)
        GUI_Handler().setOptions(curr_month,self.entry_monthList,self.entry_month)
        
    def changeInstitute(self,event:tk.Event) -> None:
        """ Changes Institute Type """
        curr_institute = self.entry_institute.get()
        curr_type = list(self.tables[curr_institute].keys())
        curr_year = list(self.tables[curr_institute][curr_type[0]].keys())
        curr_month = sorted(list(self.tables[curr_institute][curr_type[0]][curr_year[0]]),key=lambda x:self.outer.MONTH[x])

        GUI_Handler().setOptions(curr_type,self.entry_typeList,self.entry_type)
        GUI_Handler().setOptions(curr_year,self.entry_yearList,self.entry_year)
        GUI_Handler().setOptions(curr_month,self.entry_monthList,self.entry_month)
        
    def changeType(self,event:tk.Event):
        """ Changes Type Type """
        curr_institute = self.entry_institute.get()
        curr_type = self.entry_type.get()
        curr_year = list(self.tables[curr_institute][curr_type].keys())
        curr_month = sorted(list(self.tables[curr_institute][curr_type][curr_year[0]]),key=lambda x:self.outer.MONTH[x])
        
        GUI_Handler().setOptions(curr_year,self.entry_yearList,self.entry_year)
        GUI_Handler().setOptions(curr_month,self.entry_monthList,self.entry_month)
        
    # updates menu when year changes
    def changeYear(self,event:tk.Event) -> None:
        """ Changes the year """
        curr_institute = self.entry_institute.get()
        curr_type = self.entry_type.get()
        curr_year = self.entry_year.get()
        curr_month = sorted(list(self.tables[curr_institute][curr_type][curr_year]),key=lambda x:self.outer.MONTH[x])

        GUI_Handler().setOptions(curr_month,self.entry_monthList,self.entry_month)
        
        
    def check_database_thread(self):
        """ Database thread to check database (Might be overkill) """
        GUI_Handler().lock_gui_button(self.to_disable)
        GUI_Handler().place_after(self.fetch_data,self.quit)
        table:pd.DataFrame = None
        
        while True:
            if(self.stop_flag): return None
            
            try:
                table = self.QUEUE.get(block=False)
                break
            except: pass
            
        if(table is not None):
            self.data = table
            GUI_Handler().view_excel(table,self.outer.CHILD[DataView.__name__].text_excel)
            unique_col = mapping(table.columns,"hr emp code")
            
            if(unique_col is not None):
                self.outer.CHILD[DataView.__name__].data = PandaGenerator(table,unique_col)
                self.hide()
                self.outer.CHILD[DataView.__name__].appear()
                tkmb.showinfo('Fetch Status','Data Fetched Successfully')
            else:
                tkmb.showinfo('Fetch Status','Data does not have HR EMP Code Column in table')
                
        else:
            tkmb.showinfo('Fetch Status','Data Fetching Stopped')
            
        GUI_Handler().unlock_gui_button(self.to_disable)
        GUI_Handler().remove_widget(self.quit)
            
    def cancel_thread_wrapper(self) -> None:
        self.cancel_thread()
        
        GUI_Handler().unlock_gui_button(self.to_disable)
        GUI_Handler().remove_widget(self.quit)
        tkmb.showinfo('Fetch Status','Data Fetching Stopped')
        
    # fetches data from the chosen table
    def getData(self) -> None:
        curr_institute = self.entry_institute.get()
        curr_type = self.entry_type.get()
        curr_year = self.entry_year.get()
        curr_month = self.entry_month.get()
        
        self.outer.CHILD[DataView.__name__].chosen_month = curr_month
        self.outer.CHILD[DataView.__name__].chosen_year = curr_year
        self.outer.CHILD[DataView.__name__].chosen_type = curr_institute
        self.outer.CHILD[DataView.__name__].chosen_institute = curr_type
        self.outer.CHILD[DataView.__name__].changeHeading()
        
        if (self.can_start_thread()):
            self.process = Process(target=DatabaseWrapper(**self.outer.CRED).get_data,kwargs={'queue':self.QUEUE,'institute': curr_institute,'type': curr_type,'year': curr_year,'month': curr_month},daemon=True)
            self.thread = Thread(target=self.check_database_thread,daemon=True)
            self.process.start()
            self.thread.start()
            
        else:
            tkmb.showerror("Processing Error","Cannot fetch data from Database now. Please try again")
            
class DataView(BaseTemplate):
    
    chosen_month = "None"
    chosen_year = "None"
    chosen_type = "None"
    chosen_institute = "None"
    size = 12
    data:PandaGenerator = None
    
    def __init__(self,outer:App):

        self.outer = outer
        master = self.outer.APP
        
        self.frame = ctk.CTkScrollableFrame(master=master, fg_color=custom_color_scheme["fg_color"])
        
        self.label_date = ctk.CTkLabel(master=self.frame , text=f"Data View for {self.chosen_institute.capitalize()} {self.chosen_type.capitalize()} {self.chosen_month.capitalize()}/{self.chosen_year.upper()}", text_color=custom_color_scheme["text_color"], font=("Ubuntu", 25, "bold"),width=250)
        self.label_date.pack(pady=20,padx=10)
        
        frame = ctk.CTkFrame(master=self.frame, fg_color=custom_color_scheme["fg_color"])
        ctk.CTkLabel(master=frame, text="Enter Employee ID:", text_color=custom_color_scheme["text_color"], font=("Ubuntu", 16, "bold")).pack(padx=10,pady=10,side='left')
        self.entry_id = ctk.CTkEntry(master=frame , text_color=custom_color_scheme["text_color"], font=("Ubuntu", 16, "bold"),width=250)
        self.entry_id.pack(padx=10,pady=10,side='left')
        frame.pack()
        
        self.clipboard = ctk.CTkButton(master=self.frame , text="Copy Row to Clipboard", command=self.copy_row_to_clipboard, fg_color=custom_color_scheme["button_color"], font=("Ubuntu", 16, "bold"),width=250)
        self.clipboard.pack(pady=10)
        
        self.single_print = ctk.CTkButton(master=self.frame , text="Generate Single PDF", command=self.single_print_pdf_cover, fg_color=custom_color_scheme["button_color"], font=("Ubuntu", 16, "bold"),width=250)
        self.single_print.pack(pady=10)
        
        self.bulk_print = ctk.CTkButton(master=self.frame , text="Bulk Print PDFs", command=self.bulk_print_pdfs_cover, fg_color=custom_color_scheme["button_color"], font=("Ubuntu", 16, "bold"),width=250)
        self.bulk_print.pack(pady=10)
        
        ctk.CTkButton(master=self.frame , text='Back', command=self.back_to_interface, fg_color=custom_color_scheme["button_color"], font=("Ubuntu", 16, "bold"),width=250).pack(pady=10, padx=10)
        ctk.CTkLabel(master=self.frame , text="Text Size of Sheet:", text_color=custom_color_scheme["text_color"], font=("Ubuntu", 16, "bold"),width=250).pack(pady=10,padx=10)
        
        frame = ctk.CTkFrame(master=self.frame, fg_color=custom_color_scheme["fg_color"])
        
        self.minus = ctk.CTkButton(master=frame , text="-", command=self.decrease_size, fg_color=custom_color_scheme["button_color"], font=("Ubuntu", 16, "bold"),width=50)
        self.minus.pack(side="left",padx=10)
        
        self.row = ctk.CTkLabel(master=frame , text=f"{self.size}", text_color=custom_color_scheme["text_color"], font=("Ubuntu", 16, "bold"),width=100)
        self.row.pack(side="left",padx=10)
        
        self.plus = ctk.CTkButton(master=frame , text="+", command=self.increase_size, fg_color=custom_color_scheme["button_color"], font=("Ubuntu", 16, "bold"),width=50)
        self.plus.pack(side="left",padx=10)  
        
        frame.pack()

        self.text_excel = scrolledtext.ScrolledText(master=self.frame, width=90, height=25,  bg="black", fg="white", wrap=tk.NONE, font=("Courier", 12))
        x_scrollbar = Scrollbar(self.frame, orient="horizontal",command=self.text_excel.xview)
        self.text_excel.pack(pady=10,padx=10, fill='both', expand=True)
        x_scrollbar.pack(side='bottom', fill='x')

        self.text_excel.configure(xscrollcommand=x_scrollbar.set)
        self.quit = ctk.CTkButton(master=self.frame, text='Quit the Process',command=self.cancel_thread, fg_color=custom_color_scheme["button_color"], font=("Ubuntu", 16, "bold"),width=250)
        self.to_disable = self.get_widgets_to_disable()

    # back to interface
    def changeHeading(self):
        GUI_Handler().changeText(self.label_date,f"Data View for {self.chosen_institute.capitalize()} {self.chosen_type.capitalize()} {self.chosen_month.capitalize()}/{self.chosen_year}")
    
    def back_to_interface(self) -> None:
        self.hide()
        self.outer.CHILD[Interface.__name__].appear()
        
    def decrease_size(self):
        self.row.configure(text=max(1,self.size-1))
        self.size = max(1,self.size-1)
        
        GUI_Handler().change_text_font(self.text_excel,self.size)
        GUI_Handler().unlock_gui_button([self.plus])
        if(self.size==1): GUI_Handler().lock_gui_button([self.minus])
        
    def increase_size(self):
        self.row.configure(text=min(25,self.size+1))
        self.size = min(25,self.size+1)
        
        GUI_Handler().change_text_font(self.text_excel,self.size)
        GUI_Handler().unlock_gui_button([self.minus])
        if(self.size==25): GUI_Handler().lock_gui_button([self.plus])
    
    def copy_to_clipboard_thread(self, emp_id:str):
        
        GUI_Handler().lock_gui_button(self.to_disable)

        if(self.data and (emp_id in self.data.dict_iter())): 
            pyperclip.copy(','.join(self.data[emp_id].values[0]))
            tkmb.showinfo("ClipBoard Status", "Employee data copied to clipboard.")
        else:
            tkmb.showwarning("Error", "Employee ID was not found.")

        GUI_Handler().unlock_gui_button(self.to_disable)
        GUI_Handler().remove_widget(self.quit)
        
    def copy_row_to_clipboard(self):
        emp_id = self.entry_id.get()
        
        if(emp_id):
            if(self.can_start_thread()):
                self.thread = Thread(target=self.copy_to_clipboard_thread,kwargs={'emp_id':emp_id},daemon=True)
                self.thread.start()
        else:
            tkmb.showerror("Empty Data","Empty Search String Detected")

    def single_pdf_thread(self):
        
        GUI_Handler().lock_gui_button(self.to_disable)
        GUI_Handler().place_after(self.single_print,self.quit)
        status:bool = None
        msg:str = None
        
        while True:
            if(self.stop_flag):return None
            
            try:
                status, msg = self.QUEUE.get(block=False)
                break
            except: pass
            
        if(status):
            tkmb.showinfo('Single PDF Status',msg)
        else:
            tkmb.showwarning('Single PDF Status',msg)
            
        GUI_Handler().unlock_gui_button(self.to_disable)
        GUI_Handler().remove_widget(self.quit)
        
    def stop_pdf_thread(self):
        self.cancel_thread()
        GUI_Handler().unlock_gui_button(self.to_disable)
        GUI_Handler().remove_widget(self.quit)
        
        tkmb.showinfo('Process Status','PDF Generation Cancelled')

    # cover for extract_data
    def single_print_pdf_cover(self) -> None:
        month = self.chosen_month
        year = self.chosen_year
        emp_id = self.entry_id.get()
        
        if((emp_id is not None) and (self.data is not None) and (emp_id in self.data.dict_iter())):
            
            file = None
            
            try:
                _file = filedialog.asksaveasfile(initialfile=f"employee_{emp_id}",defaultextension=".pdf",filetypes=[("PDF File","*.pdf")])
                file = _file.name
            except Exception as e:
                ERROR_LOG.write_error(ERROR_LOG.get_error_info(e))
                tkmb.showwarning("Error",f"Some error has occured: {e}")
                file = None
        
            if file:
            
                if(self.can_start_thread()):
                    self.process = Process(target=PandaGeneratorWrapper(self.data).litany_of_scroll,kwargs={'queue':self.QUEUE,'data_slate_path': file,'month': month,'year': year,'emp_id': emp_id},daemon=True)
                    self.thread = Thread(target=self.single_pdf_thread,daemon=True)
                    self.process.start()
                    GUI_Handler().changeCommand(self.quit,self.stop_pdf_thread)
                    self.thread.start()
            else:
                tkmb.showerror("File Error","File was not found")
                
        elif(emp_id is not None):
            tkmb.showerror("Data Search",f"Employee ID: {emp_id} was not found")
        
        else:
            tkmb.showerror("Empty Data","Empty Search String Detected")
                        
    def bulk_print_pdfs_thread(self):
        
        GUI_Handler().lock_gui_button(self.to_disable)
        GUI_Handler().place_after(self.bulk_print,self.quit)
        done:int|None = None
        total:int|None = None
        
        while True:
            if(self.stop_flag): return None
            
            try:
                a, b = self.QUEUE.get(block=False)
                
                if(b is None): 
                    break
                
                done, total = a, b
                
            except: pass
            
        if(total):
            tkmb.showinfo('Bulk PDF Status',f"Generated {done} PDFs out of {total} records")
        else:
            tkmb.showwarning('Bulk PDF Status',f"No PDFs were generated")
            
        GUI_Handler().unlock_gui_button(self.to_disable)
        GUI_Handler().remove_widget(self.quit)
        
    def bulk_print_pdfs_cover(self) -> None:
                
        month = self.chosen_month
        year = self.chosen_year
        institute = self.chosen_institute
        type = self.chosen_type
        
        try:
            where = os.path.join(os.path.dirname(APP_PATH),'pdfs')
            where = os.path.join(where,institute)
            where = os.path.join(where,type)
            where = os.path.join(where,year)
            where = os.path.join(where,month)

            os.makedirs(where)

        except OSError as e:
            print('Directory exists')
            ERROR_LOG.write_error(ERROR_LOG.get_error_info(e))

        if(self.can_start_thread()):
            self.process = Process(target=PandaGeneratorWrapper(self.data).litany_of_scrolls,kwargs={'queue': self.QUEUE,'dropzone': where,'month': month,'year': year},daemon=True)
            self.thread = Thread(target=self.bulk_print_pdfs_thread,daemon=True)
            GUI_Handler().changeCommand(self.quit,self.stop_pdf_thread)
            
            self.process.start()
            self.thread.start()

class FileInput(BaseTemplate):
    
    data:dict[str,pd.DataFrame] = None
    sheet = ctk.StringVar(value='Sheet1')
    row_index:int = 6
    size:int = 12
    max_row:int = 0
    encryption:bool = False
    prev_password:str = None
    current_data:pd.DataFrame = None
    
    def __init__(self, outer:App):
        self.outer = outer
        master = self.outer.APP
        
        self.frame = ctk.CTkScrollableFrame(master=master, fg_color=custom_color_scheme["fg_color"])

        # title
        ctk.CTkLabel(master=self.frame , text=f"File Upload", text_color=custom_color_scheme["text_color"], font=("Ubuntu", 25, "bold"),width=250).pack(pady=20,padx=10)

        # file path input
        frame = ctk.CTkFrame(master=self.frame, fg_color=custom_color_scheme["fg_color"])
        ctk.CTkLabel(master=frame, text="Select Excel File:", text_color=custom_color_scheme["text_color"], font=("Ubuntu", 16, "bold")).pack(padx=10,pady=10,side='left')
        self.file = ctk.CTkEntry(master=frame , text_color=custom_color_scheme["text_color"], font=("Ubuntu", 16, "bold"),width=250)
        self.file.pack(padx=10,pady=10,side='left')
        frame.pack()

        # browse button
        self.browse_button = ctk.CTkButton(master=self.frame , text="Browse", command=self.select_file, fg_color=custom_color_scheme["button_color"], font=("Ubuntu", 16, "bold"),width=250)
        self.browse_button.pack(pady=10)
        
        self.upload_button = ctk.CTkButton(master=self.frame , text="Upload", command=self.load_decrypted_file, fg_color=custom_color_scheme["button_color"], font=("Ubuntu", 16, "bold"),width=250)
        
        # password frame
        self.password_frame = ctk.CTkFrame(master=self.frame, fg_color=custom_color_scheme["fg_color"])
        ctk.CTkLabel(master=self.password_frame, text="Enter Password for File:",text_color=custom_color_scheme["text_color"], font=("Ubuntu", 16, "bold")).pack(padx=10,pady=10,side='left')
        self.password_box = ctk.CTkEntry(master=self.password_frame ,show='*',text_color=custom_color_scheme["text_color"], font=("Ubuntu", 16, "bold"),width=250)
        self.password_box.pack(padx=10,pady=10,side='left')

        self.variable_frame = ctk.CTkFrame(master=self.frame, fg_color=custom_color_scheme["fg_color"])
        """ frames are added after file is uploaded """
        
        
        frame = ctk.CTkFrame(master=self.variable_frame, fg_color=custom_color_scheme["fg_color"])
        ctk.CTkLabel(master=frame, text="Sheet Present:", text_color=custom_color_scheme["text_color"], font=("Ubuntu", 16, "bold")).pack(padx=10,pady=10,side='left')
        self.sheetList = ctk.CTkOptionMenu(master=frame,variable=self.sheet,values=[],command=self.changeView,button_color=custom_color_scheme["button_color"],fg_color=custom_color_scheme["button_color"], font=("Ubuntu", 16, "bold"),width=200)
        self.sheetList.pack(side='left',pady=10, padx=10)
        frame.pack()
        
        ctk.CTkLabel(master=self.variable_frame , text="Row Change:", text_color=custom_color_scheme["text_color"], font=("Ubuntu", 16, "bold"),width=250).pack(pady=10,padx=10)
        
        frame = ctk.CTkFrame(master=self.variable_frame, fg_color=custom_color_scheme["fg_color"])
        self.row_minus = ctk.CTkButton(master=frame , text="-", command=self.prev_row, fg_color=custom_color_scheme["button_color"], font=("Ubuntu", 16, "bold"),width=50)
        self.row_minus.pack(side="left",padx=10)
        self.row = ctk.CTkLabel(master=frame , text=f"{self.row_index}", text_color=custom_color_scheme["text_color"], font=("Ubuntu", 16, "bold"),width=150)
        self.row.pack(side="left",padx=10)
        self.row_plus = ctk.CTkButton(master=frame , text="+", command=self.next_row, fg_color=custom_color_scheme["button_color"], font=("Ubuntu", 16, "bold"),width=50)
        self.row_plus.pack(side="left",padx=10)        
        frame.pack(pady=10, padx=10)
        
        self.upload = ctk.CTkButton(master=self.variable_frame , text="Save to DB", command=self.go_to_upload, fg_color=custom_color_scheme["button_color"], font=("Ubuntu", 16, "bold"),width=250)
        self.upload.pack(pady=10)
        
        self.back = ctk.CTkButton(master=self.frame , text='Back', command=self.back_to_interface, fg_color=custom_color_scheme["button_color"], font=("Ubuntu", 16, "bold"),width=250)
        self.back.pack(pady=10, padx=10)

        ctk.CTkLabel(master=self.variable_frame , text="Text Size of Sheet:", text_color=custom_color_scheme["text_color"], font=("Ubuntu", 16, "bold"),width=250).pack(pady=10,padx=10)
        
        frame = ctk.CTkFrame(master=self.variable_frame, fg_color=custom_color_scheme["fg_color"])
        
        self.size_minus = ctk.CTkButton(master=frame , text="-", command=self.decrease_size, fg_color=custom_color_scheme["button_color"], font=("Ubuntu", 16, "bold"),width=50)
        self.size_minus.pack(side="left",padx=10)
        self.font_size = ctk.CTkLabel(master=frame , text=f"{self.size}", text_color=custom_color_scheme["text_color"], font=("Ubuntu", 16, "bold"),width=100)
        self.font_size.pack(side="left",padx=10)
        self.size_plus = ctk.CTkButton(master=frame , text="+", command=self.increase_size, fg_color=custom_color_scheme["button_color"], font=("Ubuntu", 16, "bold"),width=50)
        self.size_plus.pack(side="left",padx=10)  
        frame.pack()

        self.text_excel = scrolledtext.ScrolledText(master=self.variable_frame, width=300, height=50,  bg="black", fg="white", wrap=tk.NONE, font=("Courier", 12))
        x_scrollbar = Scrollbar(self.variable_frame, orient="horizontal",command=self.text_excel.xview)
        x_scrollbar.pack(side='bottom', fill='x')

        self.text_excel.configure(xscrollcommand=x_scrollbar.set)
        self.text_excel.pack(pady=10,padx=10, fill='both', expand=True)
        
        
        self.quit = ctk.CTkButton(master=self.frame, text='Quit the Process',command=self.cancel_thread_wrapper, fg_color=custom_color_scheme["button_color"], font=("Ubuntu", 16, "bold"),width=250)
        self.to_disable = self.get_widgets_to_disable()
        
    def back_to_interface(self):
        self.hide()
        self.outer.CHILD[Interface.__name__].appear()
        
    def go_to_upload(self):
        # passing data
        self.outer.CHILD[UploadData.__name__].data = self.current_data
        self.hide()
        GUI_Handler().view_excel(self.current_data,self.outer.CHILD[UploadData.__name__].text_excel)
        self.outer.CHILD[UploadData.__name__].appear()
        
        
    def cancel_thread_wrapper(self):
        self.can_start_thread()
        GUI_Handler().unlock_gui_button(self.to_disable)
        GUI_Handler().remove_widget(self.quit)
        
    def next_row(self):
        max_row = self.current_data.shape[0]
        
        self.row_index = min(max_row, self.row_index+1)
        
        GUI_Handler().changeText(self.row,self.row_index)
        if(self.row_index==max_row): GUI_Handler().lock_gui_button([self.row_plus])
        else:
            self.get_data()
            GUI_Handler().unlock_gui_button([self.row_minus])

    def prev_row(self):
        
        self.row_index = max(0, self.row_index-1)
        GUI_Handler().changeText(self.row,self.row_index)
        
        if(self.row_index==0): GUI_Handler().lock_gui_button([self.row_minus])
        else:
            self.get_data()
            GUI_Handler().unlock_gui_button([self.row_plus])

    def get_data(self):
        file_path = self.file.get()
        password = self.prev_password
        
        if(file_path):
            
            if(self.encryption and password):                
                if(self.can_start_thread()):
                    self.thread = Thread(target=self.change_row_thread,daemon=True)
                    self.process = Process(target=Decryption().fetch_encrypted_file,kwargs={'queue': self.QUEUE,'file_path': file_path,'password':password,'skip':self.row_index},daemon=True)
                    self.thread.start()
                    self.process.start()
                    
            elif(self.encryption):
                tkmb.showinfo('Encryption Status',f"File '{file_path}' is encrypted. Please enter the password")
                
            elif(not self.encryption):
                if(self.can_start_thread()):
                    self.thread = Thread(target=self.change_row_thread,daemon=True)
                    self.process = Process(target=Decryption().fetch_decrypted_file,kwargs={'queue': self.QUEUE,'file_path': file_path,'skip':self.row_index},daemon=True)
                    self.thread.start()
                    self.process.start()
        else:
            tkmb.showerror('File Status',f"Empty file_path was detected")


    def decrease_size(self):
        self.font_size.configure(text=max(1,self.size-1))
        self.size = max(1,self.size-1)
        
        GUI_Handler().change_text_font(self.text_excel,self.size)
        GUI_Handler().unlock_gui_button([self.size_plus])
        if(self.size==1): GUI_Handler().lock_gui_button([self.size_minus])
        
    def increase_size(self):
        self.font_size.configure(text=min(25,self.size+1))
        self.size = min(25,self.size+1)
        
        GUI_Handler().change_text_font(self.text_excel,self.size)
        GUI_Handler().unlock_gui_button([self.size_minus])
        if(self.size==25): GUI_Handler().lock_gui_button([self.size_plus])
        
    def encryption_check_thread(self):
        """ Locks present GUI and places quit button after browse button """
        GUI_Handler().lock_gui_button(self.to_disable)
        GUI_Handler().place_after(self.browse_button,self.quit)  
        
    def set_after_upload_state(self):
        """ Places variable frame and removes upload and password frame """
        GUI_Handler().remove_widget(self.upload_button)
        GUI_Handler().remove_widget(self.password_frame)
        GUI_Handler().place_before(self.back,self.variable_frame)
        
    def set_after_file_is_encrypted_state(self):
        """ Places password frame before upload button """
        GUI_Handler().place_before(self.upload_button,self.password_frame)
        
    def set_for_file_upload_state(self):
        """ Removes password and variable frame """
        GUI_Handler()
        GUI_Handler().remove_widget(self.variable_frame)
        GUI_Handler().remove_widget(self.password_frame)
        
    def is_encrypted_thread(self):
        GUI_Handler().lock_gui_button(self.to_disable)
        GUI_Handler().place_after(self.browse_button,self.quit)
        self.set_for_file_upload_state()  
        GUI_Handler().changeCommand(self.upload_button,self.load_decrypted_file)
        
        is_encrypted:bool|None = None
        
        while True:
            
            if(self.stop_flag): return None
            
            try:
                is_encrypted = self.QUEUE.get(block=False)
                break
            except: pass
        
        self.encryption = is_encrypted
        
        if(is_encrypted is not None):
            GUI_Handler().place_after(self.browse_button,self.upload_button)
            if(is_encrypted):
                self.set_after_file_is_encrypted_state()
                GUI_Handler().changeCommand(self.upload_button,self.load_encrypted_file)
                
                tkmb.showinfo('Encrypted Status',f"Excel File '{self.file.get()}' is encrypted. Please provide the password")
        else:    
            tkmb.showerror('File Status',f"File '{self.file.get()}' was not found")
        
        GUI_Handler().unlock_gui_button(self.to_disable)
        GUI_Handler().remove_widget(self.quit)
        
        
    def select_file(self) -> None:
        file_path = filedialog.askopenfilename(filetypes=[("Excel Files", ".xlsx;.xls")])

        if(file_path):
            GUI_Handler().change_file_holder(self.file,file_path)
            
            if(self.can_start_thread()):
                self.thread = Thread(target=self.is_encrypted_thread,daemon=True)
                self.process = Process(target=Decryption().is_encrypted_wrapper,kwargs={'queue': self.QUEUE,'file_path': file_path},daemon=True)
                self.thread.start()
                self.process.start()
        
        else:
            tkmb.showerror('File Status',f"Empty file_path was detected")
            
    
    def load_unprotected_data_thread(self):
        GUI_Handler().lock_gui_button(self.to_disable)
        GUI_Handler().place_after(self.upload_button,self.quit)
        self.set_for_file_upload_state()  
        
        sheets:list[str] = None
        data:pd.DataFrame = None
        
        while True:
            
            if(self.stop_flag): return None
            
            try:
                sheets, data = self.QUEUE.get(block=False)
                break
            except: pass
        
        if((sheets is not None) and (data is not None)):
            self.data = data
            self.current_data = data[sheets[0]]
            GUI_Handler().setOptions(sheets,self.sheetList,self.sheet)
            self.set_after_upload_state()
            GUI_Handler().view_excel(data[sheets[0]],self.text_excel)
            
            tkmb.showinfo('Upload Status',f"Excel File '{self.file.get()}' was loaded")
        else:
            
            tkmb.showwarning('File Status',f"Excel File '{self.file.get()}' could not be loaded")
            
        GUI_Handler().unlock_gui_button(self.to_disable)
        GUI_Handler().remove_widget(self.quit)
    
    
    def load_decrypted_file(self):
        file_path = self.file.get()
                
        if(file_path):
            
            if(self.can_start_thread()):
                self.thread = Thread(target=self.load_unprotected_data_thread,daemon=True)
                self.process = Process(target=Decryption().fetch_decrypted_file,kwargs={'queue': self.QUEUE,'file_path': file_path,'skip':self.row_index},daemon=True)
                self.thread.start()
                self.process.start()
        
        else:
            tkmb.showerror('File Status',f"Empty file_path was detected")
    
    
    def load_protected_data_thread(self):
        
        GUI_Handler().lock_gui_button(self.to_disable)
        GUI_Handler().place_after(self.upload,self.quit)
        
        sheets:list[str] = None
        data:pd.DataFrame = None
        
        while True:
            
            if(self.stop_flag): return None
            
            try:
                sheets, data = self.QUEUE.get(block=False)
                break
            except: pass
        
        if((sheets is not None) and (data is not None)):
            self.data = data
            self.current_data = data[sheets[0]]
            GUI_Handler().setOptions(sheets,self.sheetList,self.sheet)
            self.set_after_upload_state()
            GUI_Handler().view_excel(data[sheets[0]],self.text_excel)
            self.prev_password = self.password_box.get()
            tkmb.showinfo('Upload Status',f"Excel File '{self.file.get()}' was loaded")
        else:
            
            tkmb.showwarning('File Status',f"Excel File '{self.file.get()}' could not be loaded. Please check the password")
            
        GUI_Handler().unlock_gui_button(self.to_disable)
        GUI_Handler().remove_widget(self.quit)
        
    def load_encrypted_file(self):
        file_path = self.file.get()
        password = self.password_box.get()
        
        if(file_path):
            
            if(self.encryption and (not password)):
                tkmb.showinfo('Encryption Status',f"File '{file_path}' is encrypted. Please enter the password")
                return None
                
            if(self.can_start_thread()):
                self.thread = Thread(target=self.load_protected_data_thread,daemon=True)
                self.process = Process(target=Decryption().fetch_encrypted_file,kwargs={'queue': self.QUEUE,'file_path': file_path,'password':password,'skip':self.row_index},daemon=True)
                self.thread.start()
                self.process.start()
        
        else:
            tkmb.showerror('File Status',f"Empty file_path was detected")
            
    
    def change_view_thread(self):
        GUI_Handler().lock_gui_button(self.to_disable)
        current_sheet = self.sheet.get()
        self.current_data = self.data[current_sheet]
        
        GUI_Handler().view_excel(self.data[current_sheet],self.text_excel)
        GUI_Handler().unlock_gui_button(self.to_disable)
        
    def change_row_thread(self):
        
        GUI_Handler().lock_gui_button(self.to_disable)
        GUI_Handler().place_before(self.text_excel,self.quit)
        current_sheet = self.sheet.get()
        data:pd.DataFrame = None
        
        while True:
            
            if(self.stop_flag): return None
            
            try:
                _, data = self.QUEUE.get(block=False)
                break
            except: pass
        
        if((current_sheet is not None) and (data is not None)):
            self.data = data
            self.current_data = data[current_sheet]
            self.set_after_upload_state()
            GUI_Handler().view_excel(data[current_sheet],self.text_excel)
            self.prev_password = self.password_box.get()
        else:
            
            tkmb.showwarning('File Status',f"Excel File '{self.file.get()}' could not be loaded. Please check the password")
        
        GUI_Handler().view_excel(self.current_data,self.text_excel)
        GUI_Handler().unlock_gui_button(self.to_disable)    
        GUI_Handler().remove_widget(self.quit)
        
    
    def changeView(self, event: tk.Event = None):
        sheet = self.sheet.get()
                
        if(sheet):
            
            if(self.can_start_thread()):
                self.thread = Thread(target=self.change_view_thread,daemon=True)
                self.thread.start()
        
        else:
            tkmb.showerror('File Status',f"Empty file_path was detected")

class UploadData(BaseTemplate):
    data:pd.DataFrame = None
    size:int = 12    
    
    chosen_institute = ctk.StringVar(value='Somaiya')
    chosen_type = ctk.StringVar(value='Teaching')
    chosen_month = ctk.StringVar(value='Jan')   

    def __init__(self, outer:App):
        self.outer = outer
        master = self.outer.APP
        
        self.frame = ctk.CTkScrollableFrame(master=master, fg_color=custom_color_scheme["fg_color"])

        # title
        ctk.CTkLabel(master=self.frame , text=f"Data Upload", text_color=custom_color_scheme["text_color"], font=("Ubuntu", 25, "bold"),width=250).pack(pady=20,padx=10)

        # file path input
        ctk.CTkLabel(master=self.frame, text="Please Enter Details about data", text_color=custom_color_scheme["text_color"], font=("Ubuntu", 18, "bold")).pack(padx=10,pady=10)


        frame = ctk.CTkFrame(master=self.frame, fg_color=custom_color_scheme["fg_color"])
        ctk.CTkLabel(master=frame, text="Institute:", text_color=custom_color_scheme["text_color"], font=("Ubuntu", 16, "bold")).pack(padx=10,pady=10,side='left')
        self.entry_institute =ctk.CTkOptionMenu(master=frame,variable=self.chosen_institute,values=list(self.outer.TOGGLE.keys()),command=self.changeType,button_color=custom_color_scheme["button_color"],fg_color=custom_color_scheme["button_color"], font=("Ubuntu", 16, "bold"),width=250)
        self.entry_institute.pack(pady=10, padx=10,side='left')
        frame.pack()
        
        frame = ctk.CTkFrame(master=self.frame, fg_color=custom_color_scheme["fg_color"])
        ctk.CTkLabel(master=frame, text="Type:", text_color=custom_color_scheme["text_color"], font=("Ubuntu", 16, "bold")).pack(padx=10,pady=10,side='left')
        self.toggle_type = ctk.CTkOptionMenu(master=frame,variable=self.chosen_type,values=self.outer.TOGGLE[list(self.outer.TOGGLE.keys())[0]][0],button_color=custom_color_scheme["button_color"],fg_color=custom_color_scheme["button_color"], font=("Ubuntu", 16, "bold"),width=250)
        self.toggle_type.pack(pady=10, padx=10,side='left')
        frame.pack()
        
        frame = ctk.CTkFrame(master=self.frame, fg_color=custom_color_scheme["fg_color"])
        ctk.CTkLabel(master=frame, text="Month:", text_color=custom_color_scheme["text_color"], font=("Ubuntu", 16, "bold")).pack(padx=10,pady=10,side='left')
        self.entry_month = ctk.CTkOptionMenu(master=frame,variable=self.chosen_month,values=[str(i).capitalize() for i in self.outer.MONTH],button_color=custom_color_scheme["button_color"],fg_color=custom_color_scheme["button_color"], font=("Ubuntu", 16, "bold"),width=250)
        self.entry_month.pack(pady=10, padx=10,side='left')
        frame.pack()
        
        frame = ctk.CTkFrame(master=self.frame, fg_color=custom_color_scheme["fg_color"])
        ctk.CTkLabel(master=frame , text="Enter Year:", text_color=custom_color_scheme["text_color"], font=("Ubuntu", 16, "bold")).pack(side='left',pady=10, padx=10)
        self.entry_year = ctk.CTkEntry(master=frame ,placeholder_text="Eg. 2024", text_color=custom_color_scheme["text_color"], font=("Ubuntu", 16, "bold"),width=100)
        self.entry_year.pack(side='left',pady=10, padx=10)
        frame.pack()
        
        self.create_button = ctk.CTkButton(master=self.frame , text='Create Table', command=self.create_in_db, fg_color=custom_color_scheme["button_color"], font=("Ubuntu", 16, "bold"),width=250)
        self.create_button.pack(pady=10, padx=10)
        
        self.update_button = ctk.CTkButton(master=self.frame , text='Upload To DB', command=self.update_in_db, fg_color=custom_color_scheme["button_color"], font=("Ubuntu", 16, "bold"),width=250)
        
        self.delete_button = ctk.CTkButton(master=self.frame , text='Delete from DB', command=self.delete_from_db, fg_color=custom_color_scheme["button_color"], font=("Ubuntu", 16, "bold"),width=250)
        self.delete_button.pack(pady=10, padx=10)
        
        ctk.CTkLabel(master=self.frame , text="Text Size of Sheet:", text_color=custom_color_scheme["text_color"], font=("Ubuntu", 16, "bold"),width=250).pack(pady=10,padx=10)
        
        frame = ctk.CTkFrame(master=self.frame, fg_color=custom_color_scheme["fg_color"])
        
        self.size_minus = ctk.CTkButton(master=frame , text="-", command=self.decrease_size, fg_color=custom_color_scheme["button_color"], font=("Ubuntu", 16, "bold"),width=50)
        self.size_minus.pack(side="left",padx=10)
        self.font_size = ctk.CTkLabel(master=frame , text=f"{self.size}", text_color=custom_color_scheme["text_color"], font=("Ubuntu", 16, "bold"),width=100)
        self.font_size.pack(side="left",padx=10)
        self.size_plus = ctk.CTkButton(master=frame , text="+", command=self.increase_size, fg_color=custom_color_scheme["button_color"], font=("Ubuntu", 16, "bold"),width=50)
        self.size_plus.pack(side="left",padx=10)  
        frame.pack()

        self.text_excel = scrolledtext.ScrolledText(master=self.frame, width=300, height=50,  bg="black", fg="white", wrap=tk.NONE, font=("Courier", 12))
        x_scrollbar = Scrollbar(self.frame, orient="horizontal",command=self.text_excel.xview)
        x_scrollbar.pack(side='bottom', fill='x')

        self.text_excel.configure(xscrollcommand=x_scrollbar.set)
        self.text_excel.pack(pady=10,padx=10, fill='both', expand=True)
        
        self.back = ctk.CTkButton(master=self.frame , text='Back', command=self.back_to_input, fg_color=custom_color_scheme["button_color"], font=("Ubuntu", 16, "bold"),width=250)
        self.back.pack(pady=10, padx=10)
        
        self.quit = ctk.CTkButton(master=self.frame, text='Quit the Process',command=self.cancel_thread_wrapper, fg_color=custom_color_scheme["button_color"], font=("Ubuntu", 16, "bold"),width=250)
        self.to_disable = self.get_widgets_to_disable()

    def back_to_input(self):
        self.hide()
        GUI_Handler().remove_widget(self.update_button)
        self.outer.CHILD[FileInput.__name__].appear()
        
    def cancel_thread_wrapper(self):
        self.cancel_thread()
        GUI_Handler().unlock_gui_button(self.to_disable)    
        GUI_Handler().remove_widget(self.quit)
        
    def decrease_size(self):
        self.font_size.configure(text=max(1,self.size-1))
        self.size = max(1,self.size-1)
        
        GUI_Handler().change_text_font(self.text_excel,self.size)
        GUI_Handler().unlock_gui_button([self.size_plus])
        if(self.size==1): GUI_Handler().lock_gui_button([self.size_minus])
        
    def increase_size(self):
        self.font_size.configure(text=min(25,self.size+1))
        self.size = min(25,self.size+1)
        
        GUI_Handler().change_text_font(self.text_excel,self.size)
        GUI_Handler().unlock_gui_button([self.size_minus])
        if(self.size==25): GUI_Handler().lock_gui_button([self.size_plus])

    def changeType(self, event:tk.Event = None):
        institute = self.chosen_institute.get()
        type = self.outer.TOGGLE[institute]
        GUI_Handler().setOptions(type,self.toggle_type,self.chosen_type)
        
    def create_thread(self,month:str,year:int,institute:str,type:str):
        GUI_Handler().lock_gui_button(self.to_disable)
        GUI_Handler().place_after(self.create_button,self.quit)
        result:int = None
    
        while True:
            if(self.stop_flag): return None
            
            try:
                result = self.QUEUE.get(block=False)
                break
            except: pass
            
        
        if(result is not None):
            match result:
                case -1: tkmb.showwarning('Column Info',"Duplicate Columns Found in Data")
                case 0: tkmb.showwarning('Column Info',"HR EMP Code column not found!")
                case 1: tkmb.showinfo("Database Status", f"Table {institute.lower()}_{type.lower()}_{month.lower()}_{year} was created. Data Insertion Possible")
                case -2: tkmb.showinfo("Database Status", f"Table {institute.lower()}_{type.lower()}_{month.lower()}_{year} already exists and the columns of table doesn't match data's columns. Please do the necessary")
                case 2: tkmb.showinfo("Database Status", f"Table {institute.lower()}_{type.lower()}_{month.lower()}_{year} already exists and the columns of table matches data's columns. Data Updation Possible")
                case 3: tkmb.showinfo("Database Status", f"MySQL Error occured")
                
            if(result in {1,2}):
                GUI_Handler().place_after(self.create_button,self.update_button)
                
        else:
            tkmb.showinfo("Database Status", f"MySQL Error occured")
        
        GUI_Handler().unlock_gui_button(self.to_disable)
        GUI_Handler().remove_widget(self.quit)
                
    
    def create_in_db(self):
        institute = self.chosen_institute.get()
        type = self.chosen_type.get()
        month = self.chosen_month.get()
        year = self.entry_year.get()
        
        if(YEAR_CHECK(year)):
            if(self.can_start_thread()):
                self.thread = Thread(target=self.create_thread,kwargs={'month': month,'year': year,'institute': institute,'type': type},daemon=True)
                self.process = Process(target=DatabaseWrapper(**self.outer.CRED).create_table,kwargs={'queue': self.QUEUE,'institute': institute,'type': type,'year': year,'month': month,'data_columns': list(self.data.columns)},daemon=True)
                self.thread.start()
                self.process.start()
                
        else:
            tkmb.showwarning("Alert","Incorrect year format")

    def update_thread(self):
        GUI_Handler().lock_gui_button(self.to_disable)
        GUI_Handler().place_after(self.update_button,self.quit)
        result:int = None
    
        while True:
            if(self.stop_flag): return None
            
            try:
                result = self.QUEUE.get(block=False)
                break
            except: pass
            
        
        if(result is not None):
            match result:
                case -1: tkmb.showwarning('Column Info',"Data Columns don't match table's columns")
                case 0: tkmb.showwarning('Column Info',"HR EMP Code column not found or MySQL error occured")
                case 1: tkmb.showinfo("Database Status", f"Data Upload Completed")
                
        else:
            tkmb.showinfo("Database Status", f"MySQL Error occured")
                
        GUI_Handler().unlock_gui_button(self.to_disable)
        GUI_Handler().remove_widget(self.quit)

    def update_in_db(self):
        institute = self.chosen_institute.get()
        type = self.chosen_type.get()
        month = self.chosen_month.get()
        year = self.entry_year.get()
        data = self.data
        
        
        if(YEAR_CHECK(year)):
            if(self.can_start_thread()):
                self.thread = Thread(target=self.update_thread,daemon=True)
                self.process = Process(target=DatabaseWrapper(**self.outer.CRED).fill_table,kwargs={'data':data,'queue': self.QUEUE,'institute': institute,'type': type,'year': year,'month': month},daemon=True)
                self.thread.start()
                self.process.start()
                
        else:
            tkmb.showwarning("Alert","Incorrect year format")

    def delete_thread(self):
        GUI_Handler().lock_gui_button(self.to_disable)
        GUI_Handler().place_after(self.delete_button,self.quit)
        result:bool = None
    
        while True:
            if(self.stop_flag): return None
            
            try:
                result = self.QUEUE.get(block=False)
                break
            except: pass
            
        
        if(result is not None):
            if(result):
                tkmb.showinfo("Database Status", f"Table dropped successfully")
            else:
                tkmb.showinfo("Database Status", f"Table does not exists")
                
        else:
            tkmb.showinfo("Database Status", f"MySQL Error occured")
                
        GUI_Handler().unlock_gui_button(self.to_disable)
        GUI_Handler().remove_widget(self.quit)
        

    def delete_from_db(self):
        institute = self.chosen_institute.get()
        type = self.chosen_type.get()
        month = self.chosen_month.get()
        year = self.entry_year.get()
        
        
        if(YEAR_CHECK(year)):
            if(self.can_start_thread()):
                self.thread = Thread(target=self.delete_thread,daemon=True)
                self.process = Process(target=DatabaseWrapper(**self.outer.CRED).delete_table,kwargs={'queue': self.QUEUE,'institute': institute,'type': type,'year': year,'month': month},daemon=True)
                self.thread.start()
                self.process.start()
                
        else:
            tkmb.showwarning("Alert","Incorrect year format")



if __name__ == "__main__":
    # initialize main app
    app = App(500,500,'Machine Spirit')
    print(app.CHILD[FileInput.__name__].get_widgets_to_disable())
    # app.start_app()

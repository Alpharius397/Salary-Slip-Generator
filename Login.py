import os
import customtkinter as ctk
import tkinter as tk
import tkinter.messagebox as tkmb
from tkinter import filedialog, scrolledtext, Scrollbar,messagebox 
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
import pyperclip
import pandas as pd
from test import dataRefine,Database

# Set custom appearance and color theme
ctk.set_appearance_mode("light")  # The custom color theme will be applied manually

class ExcelFunc():
    def generate_pdf(self,employee_data,month,year,type,chosen,file,bulk):
        try:
            if file is not None and not bulk:
                name = file.name
                file.close()
                os.remove(name)
                file_path = '/'.join(name.split('/')[:-1])
                pdf_file = f"{file_path}/{chosen}_{type}_{month}_{year}_employee_{employee_data[0]}.pdf"

            elif bulk:
                try:
                    where = os.path.join(os.path.dirname(__file__),chosen)
                    where = os.path.join(where,type)
                    where = os.path.join(where,year)
                    where = os.path.join(where,month)

                    os.makedirs(where)

                except OSError as e:
                    print('Director exists')

                pdf_file = os.path.join(where,f"{chosen}_{type}_{month}_{year}_employee_{employee_data[0]}.pdf")

            
            doc = SimpleDocTemplate(pdf_file, pagesize=letter)
            elements = []

            styles = getSampleStyleSheet()
            style_normal = styles["Normal"]
            
            # Title
            title_data = [
                ["K.J SOMAIYA INSTITUTE OF ENGINEERING & INFORMATION TECHNOLOGY, SOMAIYA AYURVIHAR EVARAD NAGAR, EASTERN EXPRESS HIGHWAY SION"],
                [f"PAY SLIP FOR THE MONTH OF {month.capitalize()}-{year}     31 DAYS     1"]
            ]
            title_table = Table(title_data, colWidths=[540])
            title_table.setStyle(TableStyle([
                ('SPAN', (0, 0), (0, 0)),
                ('SPAN', (0, 1), (0, 1)),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold')
            ]))
            elements.append(title_table)
            elements.append(Paragraph("<br/><br/>", style_normal))  # Add spacing

            # Employee Info
            employee_info_data = [
                ["NAME", employee_data[1], "DESIGNATION", employee_data[2]],
                ["DATE OF JOINING", employee_data[3], "NO OF DAYS PRESENT", employee_data[4]],
                ["PF NO", employee_data[5], "PAN NO", employee_data[6]],
                ["EMP CODE", employee_data[0], "SALARY A/C NO", employee_data[7]],
                ["Aadhar Card No", employee_data[8], "UNA", employee_data[9]],
            ]
            employee_info_table = Table(employee_info_data, colWidths=[120, 160, 120, 160])
            employee_info_table.setStyle(TableStyle([
                ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold')
            ]))
            elements.append(employee_info_table)
            elements.append(Paragraph("<br/><br/>", style_normal))  # Add spacing

            # Earnings and Deductions
            earnings_deductions_data = [
                ["EARNINGS", "RS", "DEDUCTIONS", "RS"],
                ["Basic Pay", employee_data[10], "PROF TAX", employee_data[26]],
                ["Basic", employee_data[10], "", ""],
                ["RENT HRA", employee_data[11], "PF", employee_data[27]],
                ["30%", employee_data[11], "TDS", employee_data[28]],
                ["TA/ Conveyance", employee_data[12], "LIC", employee_data[29]],
                ["SPECIAL ALW", employee_data[13], ""],
                ["Salary Arrears", employee_data[14], "Principle loan amount PM", employee_data[30]],
                ["Vehicle", employee_data[15], "", ""],
                ["Books and Periodicals", employee_data[16], "Interest 6% on bal amount", employee_data[30]],
                ["Etn Alw", employee_data[17], "", ""],
                ["Petrol Alw", employee_data[18], "", ""],
                ["Telephone", employee_data[19], "Other Deduction", employee_data[30]],
                ["Medical", employee_data[20], "", ""],
                ["LTA", employee_data[21], "", ""],
                ["Alw", employee_data[22], "", ""],
                ["EX-Grataia", employee_data[23], "", ""],
                ["Ent All", employee_data[24], "", ""],
                ["GROSS SALARY", employee_data[25], "TOTAL DEDUCTION", employee_data[30]],
                ["NET SALARY PAYABLE", employee_data[30], "", ""]
            ]
            earnings_deductions_table = Table(earnings_deductions_data, colWidths=[180, 100, 180, 100])
            earnings_deductions_table.setStyle(TableStyle([
                ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
                ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER')
            ]))
            elements.append(earnings_deductions_table)
            elements.append(Paragraph("<br/><br/>", style_normal))  # Add spacing

            # Footer
            footer_data = [
                ["This is a computer generated salary slip", ""],
                ["ACCOUNT OFFICER", ""]
            ]
            footer_table = Table(footer_data, colWidths=[300, 240])
            footer_table.setStyle(TableStyle([
                ('SPAN', (0, 0), (-1, 0)),
                ('ALIGN', (0, 0), (0, 0), 'CENTER'),
                ('ALIGN', (0, 1), (0, 1), 'RIGHT'),
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold')
            ]))
            elements.append(footer_table)

            doc.build(elements)
        except Exception as e:
            tkmb.showerror("Error", f"An error occurred while generating the PDF: {str(e)}")

    def view_excel(self):
        self.text_excel.delete(1.0, tk.END)

        data = [[i for i in self.data.columns]]
        for index,row in self.data.iterrows():
            row_data = [str(cell) for cell in row.values]
            data.append(row_data)

        col_widths = [max(len(str(cell)) for cell in col) for col in zip(*data)]
        formatted_data = "\n".join([" "+" | ".join([f"{cell:<{col_widths[i]}}" for i, cell in enumerate(row)]) +" " for row in data])
        
        self.text_excel.insert(tk.END, formatted_data)

    def changeType(self,event):
        institute = self.chosen.get()
        self.toggle_type.configure(values = list(self.outer.database[institute]))
        self.type.set(list(self.outer.database[institute])[0])

    def changeSheets(self,event=None):
        self.sheetList.configure(values=self.sheets)

    def changeView(self,event=None):
        self.data = pd.read_excel(self.file.get(),sheet_name=self.sheet.get(),dtype=str)
        dataRefine(self.data)
        self.view_excel()

    def load_database(self,month,year,chosen,type):
        db = Database(host="localhost", user="root", password="1234",database="somaiya_salary")
        self.data=db.fetchAll(month,year,chosen,type)
        db.endDatabase()
        self.view_excel()

    def bulk_print_pdfs(self):
        for i in self.data['HR_EMP_CODE'].values:
            search = self.data[self.data['HR_EMP_CODE']==i]
            self.generate_pdf(search.values[0],self.month,self.year,self.type,self.chosen)

        tkmb.showinfo("Bulk Print", "Bulk PDF generation completed.")

    def extract_data(self):
        employee_id = self.entry_id.get()

        search = self.data[self.data['HR_EMP_CODE']==employee_id]

        if search.shape[0]:
            self.saveLocation(employee_data=search.values[0],month=self.month,year=self.year,type=self.type,chosen=self.chosen)
            tkmb.showinfo("Single Print", "PDF generation completed.")
        else:
            tkmb.showwarning("Error", "Employee ID not found.")

    def copy_row_to_clipboard(self):
        employee_id = self.entry_id.get()

        search = self.data[self.data['HR_EMP_CODE']==employee_id]

        if search.shape[0]:
            pyperclip.copy(','.join(search.values[0]))
            tkmb.showinfo("Copy Row", "Employee data copied to clipboard.")
        else:
            tkmb.showwarning("Error", "Employee ID not found.")

    def bulk_print_pdfs(self):
        for i in self.data['HR_EMP_CODE'].values:
            search = self.data[self.data['HR_EMP_CODE']==str(i)]
            self.generate_pdf(search.values[0],self.month,self.year,self.type,self.chosen,file=None,bulk=True)

        tkmb.showinfo("Bulk Print", "Bulk PDF generation completed.")

    def saveLocation(self,chosen,type,month,year,employee_data):
        file = filedialog.asksaveasfile(initialfile=f"{chosen}_{type}_{month}_{year}_employee_{employee_data[0]}",defaultextension=".pdf",filetypes=[("PDF Fie","*.pdf")])
        if file:
            self.generate_pdf(employee_data,month,year,type,chosen,file,False)
        else:
            return
        
class BaseTemplate():

    def appear(self):
        for child in self.outer.children:
            self.outer.children[child].hide()
            
        if not self.visible:
            self.frame.pack(pady=20, padx=40, fill='both', expand=True)
            self.visible = True
        else:
            print(' Already visible')

    def hide(self):
        if self.visible:
            self.frame.pack_forget()
            self.visible = False
        else:
            print(' Already hidden')

# Initialize main application
class App():
    def __init__(self):
        self.app = ctk.CTk()
        self.app.geometry(f"{self.app.winfo_screenwidth()}x{self.app.winfo_screenheight()}")
        self.app.title("Salary-slip Generator")
        self.database = {'Somaiya':['Teaching','NonTeaching','Temporary'],'SVV':['svv']}

        self.children = {'login':self.Login(self,self.app),'fileinput':self.FileInput(self,self.app),'landing':self.Landing(self,self.app),'interface':self.Interface(self,self.app),'DB':self.DBFetch(self,self.app),'upload':self.DBUpload(self,self.app)}

        self.children['login'].appear()

    class Login(BaseTemplate):
        def __init__(self,outer,master):
            self.visible = False
            self.outer = outer
            self.frame = ctk.CTkScrollableFrame(master=master, fg_color=custom_color_scheme["fg_color"])

            self.label_login = ctk.CTkLabel(master=self.frame, text='Admin login page', text_color=custom_color_scheme["text_color"], font=("Helvetica", 16))
            self.label_login.pack(pady=20)

            self.user_entry = ctk.CTkEntry(master=self.frame, placeholder_text="Username", text_color=custom_color_scheme["text_color"], font=("Helvetica", 16))
            self.user_entry.pack(pady=12, padx=10)

            self.user_pass = ctk.CTkEntry(master=self.frame, placeholder_text="Password", show="*", text_color=custom_color_scheme["text_color"], font=("Helvetica", 16))
            self.user_pass.pack(pady=12, padx=10)

            self.button_login = ctk.CTkButton(master=self.frame, text='Login', command=self.login, fg_color=custom_color_scheme["button_color"], font=("Helvetica", 16))
            self.button_login.pack(pady=12, padx=10)

            self.checkbox = ctk.CTkCheckBox(master=self.frame, text='Remember Me', fg_color=custom_color_scheme["button_color"], font=("Helvetica", 16))
            self.checkbox.pack(pady=12, padx=10)


        def login(self):
            known_user = 'admin'
            known_pass = 'kjs2024'
            username = 'admin' #self.user_entry.get()
            password = 'kjs2024' #self.user_pass.get()

            if known_user == username and known_pass == password:
                tkmb.showinfo(title="Login Successful", message="You have logged in Successfully")
                self.outer.children['landing'].appear()
            elif known_user == username and known_pass != password:
                tkmb.showwarning(title='Wrong password', message='Please check your password')
            elif known_user != username and known_pass == password:
                tkmb.showwarning(title='Wrong username', message='Please check your username')
            else:
                tkmb.showerror(title="Login Failed", message="Invalid Username and password")

    class Landing(BaseTemplate):
        def __init__(self,outer,master):
            self.visible = False
            self.frame = ctk.CTkScrollableFrame(master=master, fg_color=custom_color_scheme["fg_color"])
            self.outer = outer

            button_continue = ctk.CTkButton(master=self.frame , text='Preview Existing Data', command=self.preview, fg_color=custom_color_scheme["button_color"], font=("Helvetica", 16))
            button_continue.pack(pady=12, padx=10)

            button_upload= ctk.CTkButton(master=self.frame , text='Upload Excel data', command=self.upload, fg_color=custom_color_scheme["button_color"], font=("Helvetica", 16))
            button_upload.pack(pady=12, padx=10)

        def upload(self):
            self.outer.children['fileinput'].appear()

        def preview(self):
            self.outer.children['interface'].appear()

    class Interface(BaseTemplate,ExcelFunc):
        def __init__(self,outer,master):
            self.visible = False
            self.prev_type = 'Teaching'
            self.prev_insti = 'Somaiya'
            self.outer = outer
            self.frame = ctk.CTkScrollableFrame(master=master, fg_color=custom_color_scheme["fg_color"])
            self.options = {}

            label_input = ctk.CTkLabel(master=self.frame , text="Enter Details", text_color=custom_color_scheme["text_color"], font=("Helvetica", 16))
            label_input.pack(pady=20)

            self.button_continue = ctk.CTkButton(master=self.frame , text='Continue', command=self.getData, fg_color=custom_color_scheme["button_color"], font=("Helvetica", 16))
            self.button_continue.pack(pady=12, padx=10)

            self.entry_year = ctk.StringVar()
            self.entry_year.set('')
            self.entry_yearList = ctk.CTkOptionMenu(master=self.frame,variable=self.entry_year,values=[],command=self.changeMenu,button_color=custom_color_scheme["button_color"],fg_color=custom_color_scheme["button_color"], font=("Helvetica", 16))
            self.entry_yearList.pack(pady=12, padx=10)

            self.entry_month = ctk.StringVar()
            self.entry_month.set('')
            self.entry_monthList = ctk.CTkOptionMenu(master=self.frame,variable=self.entry_month,values=[],button_color=custom_color_scheme["button_color"],fg_color=custom_color_scheme["button_color"], font=("Helvetica", 16))
            self.entry_monthList.pack(pady=12, padx=10)

            self.chosen = ctk.StringVar()
            self.chosen.set('Somaiya')
            self.toggle_institute  = ctk.CTkOptionMenu(master=self.frame,variable=self.chosen,values=["Somaiya", "SVV"],command=self.changeType,button_color=custom_color_scheme["button_color"],fg_color=custom_color_scheme["button_color"], font=("Helvetica", 16))
            self.toggle_institute.pack(pady=12, padx=10)

            self.type = ctk.StringVar()
            self.type.set('Teaching')
            self.toggle_type  = ctk.CTkOptionMenu(master=self.frame,variable=self.type,values=[],command=self.checkDB,button_color=custom_color_scheme["button_color"],fg_color=custom_color_scheme["button_color"], font=("Helvetica", 16))
            self.toggle_type.pack(pady=12, padx=10)

            self.button_back_to_login = ctk.CTkButton(master=self.frame , text='Back', command=self.back_to_landing, fg_color=custom_color_scheme["button_color"], font=("Helvetica", 16))
            self.button_back_to_login.pack(pady=12, padx=10)

            self.available_data()
            self.changeType(event=None)

        def back_to_landing(self):
            self.outer.children['landing'].appear()

        def checkDB(self,event):
            self.available_data()

        def available_data(self):
            data = Database( host="localhost",user="root", password="1234", database="somaiya_salary").showTables().get(self.chosen.get().lower())
            data = data.get(self.type.get().lower()) if data else None

            if data and len(data)>0:
                self.options = data

                self.entry_monthList.configure(values=data[list(data)[0]])
                self.entry_yearList.configure(values=list(data))

                self.entry_year.set(list(data)[0])
                self.entry_month.set(data[list(data)[0]][0])
                self.prev_type =  self.type.get()
                self.prev_insti = self.chosen.get()
            else:
                self.chosen.set(self.prev_insti)
                self.chosen.set(self.prev_type)
                self.changeType(event=None)
                tkmb.showwarning("Error", "No Data found!")

        def changeMenu(self,event=None):
            year = self.entry_year.get()
            self.entry_monthList.configure(values=[month for month in self.options[year]])
            self.entry_month.set(self.options[year][0])

        def changeType(self,event):
            ExcelFunc.changeType(self,event=event)
            self.available_data()

        def getData(self):
            month = self.entry_month.get()
            year = self.entry_year.get()
            chosen = self.toggle_institute.get().lower()
            type = self.toggle_type.get().lower()

            print(month,year,chosen,type)
            self.outer.children['DB'].month = month
            self.outer.children['DB'].year = year
            self.outer.children['DB'].chosen = chosen
            self.outer.children['DB'].type = type
            self.outer.children['DB'].load_database(month,year,chosen,type)
            self.outer.children['DB'].label_date.configure(text=f"{chosen.capitalize()}-{type.capitalize()}-{month.capitalize()}-{year.upper()}")
            self.outer.children['DB'].appear()

    class FileInput(BaseTemplate,ExcelFunc):
        def __init__(self,outer,master):
            self.visible = False
            self.outer = outer
            self.frame = ctk.CTkScrollableFrame(master=master, fg_color=custom_color_scheme["fg_color"])
            self.sheets = []
            self.data = pd.DataFrame([])

            self.label_file = ctk.CTkLabel(master=self.frame , text="Selected Excel File:", text_color=custom_color_scheme["text_color"], font=("Helvetica", 16))
            self.label_file.pack(pady=10)

            self.file = ctk.CTkEntry(master=self.frame , width=100, text_color=custom_color_scheme["text_color"], font=("Helvetica", 16))
            self.file.pack(pady=5)

            self.button_browse = ctk.CTkButton(master=self.frame , text="Browse", command=self.select_file, fg_color=custom_color_scheme["button_color"], font=("Helvetica", 16))
            self.button_browse.pack(pady=5)

            self.sheet = ctk.StringVar()
            self.sheet.set('')
            self.sheetList = ctk.CTkOptionMenu(master=self.frame,variable=self.sheet,values=[],command=self.changeView,button_color=custom_color_scheme["button_color"],fg_color=custom_color_scheme["button_color"], font=("Helvetica", 16))
            self.sheetList.pack(pady=12, padx=10)

            self.chosen = ctk.StringVar()
            self.chosen.set('Somaiya')
            self.toggle_institute  = ctk.CTkOptionMenu(master=self.frame,variable=self.chosen,values=["Somaiya", "SVV"],command=self.changeType,button_color=custom_color_scheme["button_color"],fg_color=custom_color_scheme["button_color"], font=("Helvetica", 16))
            self.toggle_institute.pack(pady=12, padx=10)

            self.type = ctk.StringVar()
            self.type.set('Teaching')
            self.toggle_type  = ctk.CTkOptionMenu(master=self.frame,variable=self.type,values=[],button_color=custom_color_scheme["button_color"],fg_color=custom_color_scheme["button_color"], font=("Helvetica", 16))
            self.toggle_type.pack(pady=12, padx=10)

            self.month = ctk.StringVar()
            self.month.set('jan')
            monthList = ctk.CTkOptionMenu(master=self.frame,variable=self.month,values=["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sept", "oct", "nov", "dec"],button_color=custom_color_scheme["button_color"],fg_color=custom_color_scheme["button_color"], font=("Helvetica", 16))
            monthList.pack(pady=12, padx=10)

            year = ctk.CTkLabel(master=self.frame , text="Enter Year:", text_color=custom_color_scheme["text_color"], font=("Helvetica", 16))
            year.pack()

            
            self.year = ctk.CTkEntry(master=self.frame , text_color=custom_color_scheme["text_color"], font=("Helvetica", 16))
            self.year.pack()

            label_id = ctk.CTkLabel(master=self.frame , text="Enter Employee ID:", text_color=custom_color_scheme["text_color"], font=("Helvetica", 16))
            label_id.pack()

            self.entry_id = ctk.CTkEntry(master=self.frame , text_color=custom_color_scheme["text_color"], font=("Helvetica", 16))
            self.entry_id.pack(pady=5)

            self.button_extract = ctk.CTkButton(master=self.frame , text="Generate pdf", command=self.extract_data, fg_color=custom_color_scheme["button_color"], font=("Helvetica", 16))
            self.button_extract.pack(pady=10)

            self.button_bulk_print = ctk.CTkButton(master=self.frame , text="Bulk Print PDFs", command=self.bulk_print_pdfs, fg_color=custom_color_scheme["button_color"], font=("Helvetica", 16))
            self.button_bulk_print.pack(pady=10)

            self.button_copy = ctk.CTkButton(master=self.frame , text="Copy Row to Clipboard", command=self.copy_row_to_clipboard, fg_color=custom_color_scheme["button_color"], font=("Helvetica", 16))
            self.button_copy.pack(pady=10)

            self.upload_to_db = ctk.CTkButton(master=self.frame , text="Save to DB", command=self.uploadTime, fg_color=custom_color_scheme["button_color"], font=("Helvetica", 16))
            self.upload_to_db.pack(pady=10)

            self.button_back_to_interface = ctk.CTkButton(master=self.frame , text='Back', command=self.back_to_landing, fg_color=custom_color_scheme["button_color"], font=("Helvetica", 16))
            self.button_back_to_interface.pack(pady=12, padx=10)

            self.text_excel = scrolledtext.ScrolledText(master=self.frame, width=90, height=25,  bg="black", fg="white", wrap=tk.NONE, font=("Courier", 12))
            x_scrollbar = Scrollbar(self.frame, orient="horizontal",command=self.text_excel.xview)
            y_scrollbar = Scrollbar(self.frame,command=self.text_excel.yview)

            x_scrollbar.pack(side='bottom', fill='x')
            y_scrollbar.pack(side='right', fill='y')

            self.text_excel.configure(xscrollcommand=x_scrollbar.set,yscrollcommand=y_scrollbar.set)
            self.text_excel.pack(pady=10,padx=10, fill='both', expand=True)

        def uploadTime(self):
            if self.data.shape[0]:
                self.outer.children['upload'].data = self.data
                self.outer.children['upload'].sheet.set(self.sheet.get())
                self.outer.children['upload'].file.delete(0, tk.END)
                self.outer.children['upload'].file.insert(0, self.file.get())
                self.outer.children['upload'].sheetList.configure(values=self.sheets)
                self.outer.children['upload'].view_excel()
                self.outer.children['upload'].appear()
            else:
                tkmb.showwarning("Error", "No data found")


        def back_to_landing(self):
            self.outer.children['landing'].appear()

        def select_file(self):
            file_path = filedialog.askopenfilename(filetypes=[("Excel Files", ".xlsx;.xls")])
            if file_path:
                self.file.delete(0, tk.END)
                self.file.insert(0, file_path)
                self.file.configure(width=7*len(file_path))
                self.sheets = list(pd.read_excel(file_path,sheet_name=None).keys())
                self.sheet.set(self.sheets[0])
                self.changeSheets(event=None)
                self.changeView()

    class DBFetch(BaseTemplate,ExcelFunc):
        def __init__(self,outer,master):

            self.visible = False
            self.outer = outer
            self.frame = ctk.CTkScrollableFrame(master=master, fg_color=custom_color_scheme["fg_color"])
            self.month = "None"
            self.year = "None"
            self.type = "None"
            self.chosen = "None"
            self.data = []
            self.label_date = ctk.CTkLabel(master=self.frame , text=f"{self.month.capitalize()}-{self.year.upper()}", text_color=custom_color_scheme["text_color"], font=("Helvetica", 16))
            self.label_date.pack()

            self.label_id = ctk.CTkLabel(master=self.frame , text="Enter Employee ID:", text_color=custom_color_scheme["text_color"], font=("Helvetica", 16))
            self.label_id.pack()

            self.entry_id = ctk.CTkEntry(master=self.frame , text_color=custom_color_scheme["text_color"], font=("Helvetica", 16))
            self.entry_id.pack(pady=5)

            self.button_extract = ctk.CTkButton(master=self.frame , text="Generate pdf", command=self.extract_data, fg_color=custom_color_scheme["button_color"], font=("Helvetica", 16))
            self.button_extract.pack(pady=10)

            self.button_bulk_print = ctk.CTkButton(master=self.frame , text="Bulk Print PDFs", command=self.bulk_print_pdfs, fg_color=custom_color_scheme["button_color"], font=("Helvetica", 16))
            self.button_bulk_print.pack(pady=10)

            self.button_copy = ctk.CTkButton(master=self.frame , text="Copy Row to Clipboard", command=self.copy_row_to_clipboard, fg_color=custom_color_scheme["button_color"], font=("Helvetica", 16))
            self.button_copy.pack(pady=10)

            self.button_back_to_interface = ctk.CTkButton(master=self.frame , text='Back', command=self.back_to_interface, fg_color=custom_color_scheme["button_color"], font=("Helvetica", 16))
            self.button_back_to_interface.pack(pady=12, padx=10)

            self.text_excel = scrolledtext.ScrolledText(master=self.frame, width=90, height=25,  bg="black", fg="white", wrap=tk.NONE, font=("Courier", 12))
            x_scrollbar = Scrollbar(self.frame, orient="horizontal",command=self.text_excel.xview)
            y_scrollbar = Scrollbar(self.frame,command=self.text_excel.yview)

            x_scrollbar.pack(side='bottom', fill='x')
            y_scrollbar.pack(side='right', fill='y')

            self.text_excel.configure(xscrollcommand=x_scrollbar.set,yscrollcommand=y_scrollbar.set)
            self.text_excel.pack(pady=10,padx=10, fill='both', expand=True)


        def back_to_interface(self):
            self.outer.children['interface'].appear()

    class DBUpload(BaseTemplate,ExcelFunc):
        def __init__(self,outer,master):

            self.visible = False
            self.outer = outer
            self.frame = ctk.CTkScrollableFrame(master=master, fg_color=custom_color_scheme["fg_color"])
            self.sheets = []
            self.data = []

            self.file = ctk.CTkEntry(master=self.frame , width=100, text_color=custom_color_scheme["text_color"], font=("Helvetica", 16))
            self.file.pack(pady=5)

            self.sheet = ctk.StringVar()
            self.sheet.set('')
            self.sheetList = ctk.CTkOptionMenu(master=self.frame,variable=self.sheet,values=[],command=self.changeView,button_color=custom_color_scheme["button_color"],fg_color=custom_color_scheme["button_color"], font=("Helvetica", 16))
            self.sheetList.pack(pady=12, padx=10)

            self.chosen = ctk.StringVar()
            self.chosen.set('Somaiya')
            self.toggle_institute  = ctk.CTkOptionMenu(master=self.frame,variable=self.chosen,values=["Somaiya", "SVV"],command=self.changeType,button_color=custom_color_scheme["button_color"],fg_color=custom_color_scheme["button_color"], font=("Helvetica", 16))
            self.toggle_institute.pack(pady=12, padx=10)

            self.type = ctk.StringVar()
            self.type.set('Teaching')
            self.toggle_type  = ctk.CTkOptionMenu(master=self.frame,variable=self.type,values=[],button_color=custom_color_scheme["button_color"],fg_color=custom_color_scheme["button_color"], font=("Helvetica", 16))
            self.toggle_type.pack(pady=12, padx=10)

            self.month = ctk.StringVar()
            self.month.set('jan')
            monthList = ctk.CTkOptionMenu(master=self.frame,variable=self.month,values=["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sept", "oct", "nov", "dec"],button_color=custom_color_scheme["button_color"],fg_color=custom_color_scheme["button_color"], font=("Helvetica", 16))
            monthList.pack(pady=12, padx=10)

            year = ctk.CTkLabel(master=self.frame , text="Enter Year:", text_color=custom_color_scheme["text_color"], font=("Helvetica", 16))
            year.pack()
            
            self.year = ctk.CTkEntry(master=self.frame , text_color=custom_color_scheme["text_color"], font=("Helvetica", 16))
            self.year.pack()

            self.upload_to_db = ctk.CTkButton(master=self.frame , text="Upload to DB",command=self.upload, fg_color=custom_color_scheme["button_color"], font=("Helvetica", 16))
            self.upload_to_db.pack(pady=10)

            self.deload_from_db = ctk.CTkButton(master=self.frame , text="Delete from DB",command=self.deload, fg_color=custom_color_scheme["button_color"], font=("Helvetica", 16))
            self.deload_from_db.pack(pady=10)

            self.button_back_to_interface = ctk.CTkButton(master=self.frame , text='Back', command=self.back_to_view, fg_color=custom_color_scheme["button_color"], font=("Helvetica", 16))
            self.button_back_to_interface.pack(pady=12, padx=10)

            self.text_excel = scrolledtext.ScrolledText(master=self.frame, width=90, height=25,  bg="black", fg="white", wrap=tk.NONE, font=("Courier", 12))
            x_scrollbar = Scrollbar(self.frame, orient="horizontal",command=self.text_excel.xview)
            y_scrollbar = Scrollbar(self.frame,command=self.text_excel.yview)

            x_scrollbar.pack(side='bottom', fill='x')
            y_scrollbar.pack(side='right', fill='y')

            self.text_excel.configure(xscrollcommand=x_scrollbar.set,yscrollcommand=y_scrollbar.set)
            self.text_excel.pack(pady=10,padx=10, fill='both', expand=True)

            self.changeType(event=None)


        def deload(self):
            database = Database(host="localhost", user="root", password="1234",database="somaiya_salary")
            if self.year.get():
                try:
                    year = int(self.year.get())
                except ValueError:
                    tkmb.showwarning("Alert","Incorrect year format")
            else:
                tkmb.showwarning("Alert","Please enter year")
                return 
            
            month = self.month.get()
            sheet = self.sheet.get()
            chosen = self.chosen.get().lower()
            type = self.type.get().lower()

            if year and sheet and month and chosen and type and messagebox.askyesnocancel("Confirmation", f"Month: {month}, Year: {year} \n Institue:{ chosen}, Type: {type} \n Are you sure you want to clear this data from DB?"):

                if messagebox.askyesnocancel("Warning","Once data is dropped it cannot be retrieved. Are you sure about this?") and messagebox.askyesnocancel("Warning","Are you sure about this again?"):
                    if database.dropTable(chosen,type,month,year):
                        tkmb.showinfo("Alert", "Table dropped")
                    else:
                        tkmb.showinfo("Alert", "Table dropped (Table does not exists)")

                 
            database.endDatabase()

        def upload(self):
            database = Database(host="localhost", user="root", password="1234",database="somaiya_salary")
            if self.year.get():
                try:
                    year = int(self.year.get())
                except ValueError:
                    tkmb.showwarning("Alert","Incorrect year format")
            else:
                tkmb.showwarning("Alert","Please enter year")
                return 
            
            month = self.month.get()
            sheet = self.sheet.get()
            chosen = self.chosen.get().lower()
            type = self.type.get().lower()

            if year and sheet and month and chosen and type and messagebox.askyesnocancel("Confirmation", f"Month: {month}, Year: {year} \n Institue:{ chosen}, Type: {type} \n Are you sure details are correct?"):

                if database.createData(month,year,self.data.columns,chosen,type):
                    tkmb.showinfo("Alert", "Table created")

                    res = database.updateData(self.data,month,year,chosen,type)
                    if res is not None:
                        tkmb.showinfo("Upload","Data was successfully")
                    elif res==-1:
                        tkmb.showinfo("Upload","Columns do not match")
                    else:
                        tkmb.showwarning('Error','Some error occured')

                else:
                    response = messagebox.askyesnocancel("Table exists", "This data already exists. Would you like to update it?")

                    if response:
                        res = database.updateData(self.data,month,year,chosen,type)
                        if res is not None and res!=-1:
                            tkmb.showinfo("Upload","Data was successfully")
                        elif res==-1:
                            tkmb.showinfo("Upload","Columns do not match")
                        else:
                            tkmb.showwarning('Error','Some error occured')
                    else:
                        tkmb.showinfo("Upload","Data upload aborted")

            database.endDatabase()

        def back_to_view(self):
            self.outer.children['fileinput'].appear()

# Apply custom colors
custom_color_scheme = {
    "fg_color": "white",
    "button_color": "dark red",
    "text_color": "black",
    "combo_box_color": "white"  # Added for combo box color
}


app = App()

app.app.mainloop()
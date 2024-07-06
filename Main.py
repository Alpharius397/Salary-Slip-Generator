import datetime
import customtkinter as ctk
import tkinter.messagebox as tkmb
import tkinter as tk
from tkinter import filedialog, scrolledtext, Scrollbar
from openpyxl import load_workbook
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
import pyperclip
import os
import mysql.connector
import pandas as pd
from test import dataRefine,Database


# Set custom appearance and color theme
ctk.set_appearance_mode("light")  # The custom color theme will be applied manually

# Initialize main application
class App():
    def __init__(self):
        self.app = ctk.CTk()
        self.app.geometry(f"{self.app.winfo_screenwidth()}x{self.app.winfo_screenheight()}")
        self.app.title("Salary-slip Generator")
        self.database = {'Somaiya':['Teaching','Non-Teaching','Temporary'],'SVV':['svv']}
        self.children = {'login':self.Login(self,self.app),'fileinput':self.FileInput(self,self.app),'landing':self.Landing(self,self.app),'interface':self.Interface(self,self.app),'DB':self.DBFetch(self,self.app),'upload':self.DBUpload(self,self.app)}

        self.children['login'].appear()

    
    class Login:
        def __init__(self, outer, master):
            self.visible = False
            self.outer = outer
            self.frame = ctk.CTkScrollableFrame(master=master, fg_color=custom_color_scheme["fg_color"])

            # Title Label
            self.label_login = ctk.CTkLabel(
                master=self.frame,
                text='Admin Login Page',
                text_color=custom_color_scheme["text_color"],
                font=("Helvetica", 18, "bold")
            )
            self.label_login.pack(pady=(40, 20))

            # Username Entry
            self.user_entry = ctk.CTkEntry(
                master=self.frame,
                placeholder_text="Username",
                text_color=custom_color_scheme["text_color"],
                font=("Helvetica", 16),
                width=250
            )
            self.user_entry.pack(pady=12, padx=10)

            # Password Entry
            self.user_pass = ctk.CTkEntry(
                master=self.frame,
                placeholder_text="Password",
                show="*",
                text_color=custom_color_scheme["text_color"],
                font=("Helvetica", 16),
                width=250
            )
            self.user_pass.pack(pady=12, padx=10)

            # Login Button
            self.button_login = ctk.CTkButton(
                master=self.frame,
                text='Login',
                command=self.login,
                fg_color=custom_color_scheme["button_color"],
                font=("Helvetica", 16),
                width=250
            )
            self.button_login.pack(pady=(20, 10), padx=10)

            # Remember Me Checkbox
            self.checkbox = ctk.CTkCheckBox(
                master=self.frame,
                text='Remember Me',
                fg_color=custom_color_scheme["button_color"],
                font=("Helvetica", 16)
            )
            self.checkbox.pack(pady=10, padx=10)

            # Footer with link (Optional)
            self.footer_label = ctk.CTkLabel(
                master=self.frame,
                text='Forgot Password?',
                text_color=custom_color_scheme["button_color"],
                font=("Helvetica", 14, "underline")
            )
            self.footer_label.pack(pady=(20, 40))

        def appear(self):
            for child in self.outer.children:
                self.outer.children[child].hide()
                    
            if not self.visible:
                self.frame.pack(pady=20, padx=40, fill='both', expand=True)
                self.visible = True
            else:
                print('Already visible')

        def hide(self):
            if self.visible:
                self.frame.pack_forget()
                self.visible = False
            else:
                print('Already hidden')

        def login(self):
            known_user = 'admin'
            known_pass = 'kjs2024'
            username = self.user_entry.get()
            password = self.user_pass.get()

            if known_user == username and known_pass == password:
                tkmb.showinfo(title="Login Successful", message="You have logged in Successfully")
                self.outer.children['landing'].appear()
            elif known_user == username and known_pass != password:
                tkmb.showwarning(title='Wrong password', message='Please check your password')
            elif known_user != username and known_pass == password:
                tkmb.showwarning(title='Wrong username', message='Please check your username')
            else:
                tkmb.showerror(title="Login Failed", message="Invalid Username and password")

    class Landing:
        def __init__(self, outer, master):
            self.visible = False
            self.frame = ctk.CTkScrollableFrame(master=master, fg_color=custom_color_scheme["fg_color"])
            self.outer = outer

            # Title Label
            label_input = ctk.CTkLabel(
                master=self.frame,
                text="Choose Method for PDF",
                text_color=custom_color_scheme["text_color"],
                font=("Helvetica", 18, "bold")
            )
            label_input.pack(pady=(40, 20))

            # Preview Button
            button_continue = ctk.CTkButton(
                master=self.frame,
                text='Preview Existing Data',
                command=self.preview,
                fg_color=custom_color_scheme["button_color"],
                font=("Helvetica", 16),
                width=250
            )
            button_continue.pack(pady=12, padx=10)

            # Upload Button
            button_upload = ctk.CTkButton(
                master=self.frame,
                text='Upload Excel Data',
                command=self.upload,
                fg_color=custom_color_scheme["button_color"],
                font=("Helvetica", 16),
                width=250
            )
            button_upload.pack(pady=12, padx=10)

            self.button_back_to_login = ctk.CTkButton(
                master=self.frame,
                text='Back',
                command=self.upload,
                fg_color=custom_color_scheme["button_color"],
                font=("Helvetica", 16),
                width=250
             )


        def appear(self):
            for child in self.outer.children:
                self.outer.children[child].hide()
                    
            if not self.visible:
                self.frame.pack(pady=20, padx=40, fill='both', expand=True)
                self.visible = True
            else:
                print('Already visible')

        def hide(self):
            if self.visible:
                self.frame.pack_forget()
                self.visible = False
            else:
                print('Already hidden')

        def upload(self):
            self.outer.children['fileinput'].appear()

        def preview(self):
            self.outer.children['interface'].appear()
    class Interface():
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

        def appear(self):
            for child in self.outer.children:
                self.outer.children[child].hide()
                
            if not self.visible:
                self.frame.pack(pady=20, padx=40, fill='both', expand=True)
                self.available_data()
                self.visible = True
            else:
                print(' Already visible')

        def hide(self):
            if self.visible:
                self.frame.pack_forget()
                self.visible = False
            else:
                print(' Already hidden')

        def back_to_landing(self):
            self.outer.children['landing'].appear()

        def checkDB(self,event):
            self.available_data()

        def available_data(self):
            data = Database( host="localhost",user="root", password="1234", database="somaiya_salary").showTables().get(self.toggle_institute.get().lower())
            data = data.get(self.toggle_type.get().lower()) if data else None

            if data and len(data)>0:
                self.options = data

                self.entry_monthList.configure(values=data[list(data)[0]])
                self.entry_yearList.configure(values=list(data))

                self.entry_year.set(list(data)[0])
                self.entry_month.set(data[list(data)[0]][0])
                self.prev_type =  self.toggle_type.get()
                self.prev_insti = self.toggle_institute.get()
            else:
                self.toggle_institute.set(self.prev_insti)
                self.toggle_type.set(self.prev_type)
                self.changeType(event=None)
                tkmb.showwarning("Error", "No Data found!")

        def changeMenu(self,event=None):
            year = self.entry_year.get()
            self.entry_monthList.configure(values=[month for month in self.options[year]])
            self.entry_month.set(self.options[year][0])

        def changeType(self,event):
            institute = self.toggle_institute.get()

            self.toggle_type.configure(values = list(self.outer.database[institute]))
            self.toggle_type.set(list(self.outer.database[institute])[0])

            self.available_data()

        def getData(self):
            month = self.entry_month.get()
            year = self.entry_year.get()
            insti = self.toggle_institute.get().lower()
            type = self.toggle_type.get().lower()

            print(month,year,insti,type)
            self.outer.children['DB'].month = month
            self.outer.children['DB'].year = year
            self.outer.children['DB'].insti = insti
            self.outer.children['DB'].type = type
            self.outer.children['DB'].load_database(month,year,insti,type)
            self.outer.children['DB'].label_date.configure(text=f"{insti.capitalize()}-{type.capitalize()}-{month.capitalize()}-{year.upper()}")
            self.outer.children['DB'].appear()


    class FileInput():
        def __init__(self, outer, master):
            self.visible = False
            self.outer = outer
            self.frame = ctk.CTkScrollableFrame(master=master, fg_color=custom_color_scheme["fg_color"])
            self.sheets = []

            self.label_file = ctk.CTkLabel(master=self.frame, text="Select Excel File:", text_color=custom_color_scheme["text_color"], font=("Helvetica", 16))
            self.label_file.grid(row=0, column=0, pady=10, padx=10, sticky="w")

            self.entry_file = ctk.CTkEntry(master=self.frame, width=200, text_color=custom_color_scheme["text_color"], font=("Helvetica", 16))
            self.entry_file.grid(row=0, column=1, pady=5, padx=10, sticky="w")

            self.button_browse = ctk.CTkButton(master=self.frame, text="Browse", command=self.select_file, fg_color=custom_color_scheme["button_color"], font=("Helvetica", 16))
            self.button_browse.grid(row=0, column=2, pady=5, padx=10)

            self.sheet = ctk.StringVar()
            self.sheet.set('')
            self.sheetList = ctk.CTkOptionMenu(master=self.frame, variable=self.sheet, values=[], command=self.changeView, button_color=custom_color_scheme["button_color"], fg_color=custom_color_scheme["button_color"], font=("Helvetica", 16))
            self.sheetList.grid(row=1, column=0, columnspan=3, pady=12, padx=10, sticky="w")

            self.chosen = ctk.StringVar()
            self.chosen.set('Somaiya')
            self.toggle_institute = ctk.CTkOptionMenu(master=self.frame, variable=self.chosen, values=["Somaiya", "SVV"], command=self.changeType, button_color=custom_color_scheme["button_color"], fg_color=custom_color_scheme["button_color"], font=("Helvetica", 16))
            self.toggle_institute.grid(row=2, column=0, columnspan=3, pady=12, padx=10, sticky="w")

            self.type = ctk.StringVar()
            self.type.set('Teaching')
            self.toggle_type = ctk.CTkOptionMenu(master=self.frame, variable=self.type, values=[], button_color=custom_color_scheme["button_color"], fg_color=custom_color_scheme["button_color"], font=("Helvetica", 16))
            self.toggle_type.grid(row=3, column=0, columnspan=3, pady=12, padx=10, sticky="w")

            self.month = ctk.StringVar()
            self.month.set('jan')
            monthList = ctk.CTkOptionMenu(master=self.frame, variable=self.month, values=["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sept", "oct", "nov", "dec"], button_color=custom_color_scheme["button_color"], fg_color=custom_color_scheme["button_color"], font=("Helvetica", 16))
            monthList.grid(row=4, column=0, columnspan=3, pady=12, padx=10, sticky="w")

            self.year_label = ctk.CTkLabel(master=self.frame, text="Enter Year:", text_color=custom_color_scheme["text_color"], font=("Helvetica", 16))
            self.year_label.grid(row=5, column=0, pady=5, padx=10, sticky="w")

            self.year = ctk.CTkEntry(master=self.frame, width=50, text_color=custom_color_scheme["text_color"], font=("Helvetica", 16))
            self.year.grid(row=5, column=1, pady=5, padx=10, sticky="w")

            self.label_id = ctk.CTkLabel(master=self.frame, text="Enter Employee ID:", text_color=custom_color_scheme["text_color"], font=("Helvetica", 16))
            self.label_id.grid(row=6, column=0, pady=5, padx=10, sticky="w")

            self.entry_id = ctk.CTkEntry(master=self.frame, width=50, text_color=custom_color_scheme["text_color"], font=("Helvetica", 16))
            self.entry_id.grid(row=6, column=1, pady=5, padx=10, sticky="w")

            self.button_extract = ctk.CTkButton(master=self.frame, text="Generate PDF", command=self.extract_data, fg_color=custom_color_scheme["button_color"], font=("Helvetica", 16))
            self.button_extract.grid(row=7, column=0, pady=10, padx=10)

            self.button_bulk_print = ctk.CTkButton(master=self.frame, text="Bulk Print PDFs", command=self.bulk_print_pdfs, fg_color=custom_color_scheme["button_color"], font=("Helvetica", 16))
            self.button_bulk_print.grid(row=7, column=1, pady=10, padx=10)

            self.button_copy = ctk.CTkButton(master=self.frame, text="Copy Row to Clipboard", command=self.copy_row_to_clipboard, fg_color=custom_color_scheme["button_color"], font=("Helvetica", 16))
            self.button_copy.grid(row=7, column=2, pady=10, padx=10)

            self.upload_to_db = ctk.CTkButton(master=self.frame, text="Save to DB", command=self.uploadTime, fg_color=custom_color_scheme["button_color"], font=("Helvetica", 16))
            self.upload_to_db.grid(row=8, column=0, pady=10, padx=10)

            self.button_back_to_interface = ctk.CTkButton(master=self.frame, text='Back', command=self.back_to_landing, fg_color=custom_color_scheme["button_color"], font=("Helvetica", 16))
            self.button_back_to_interface.grid(row=8, column=1, pady=10, padx=10)

            self.text_excel = scrolledtext.ScrolledText(master=self.frame, width=90, height=25, bg="black", fg="white", wrap=tk.NONE, font=("Courier", 12))
            self.text_excel.grid(row=9, column=0, columnspan=3, pady=10, padx=10, sticky="nsew")

            x_scrollbar = Scrollbar(self.frame, orient="horizontal", command=self.text_excel.xview)
            y_scrollbar = Scrollbar(self.frame, command=self.text_excel.yview)
            self.text_excel.configure(xscrollcommand=x_scrollbar.set, yscrollcommand=y_scrollbar.set)
            x_scrollbar.grid(row=10, column=0, columnspan=3, sticky='ew')
            y_scrollbar.grid(row=9, column=3, sticky='ns')

            self.frame.grid_rowconfigure(9, weight=1)
            self.frame.grid_columnconfigure(2, weight=1)

        def uploadTime(self):
            self.outer.children['upload'].appear()

        def appear(self):
            for child in self.outer.children:
                self.outer.children[child].hide()

            if not self.visible:
                self.frame.pack(pady=20, padx=40, fill='both', expand=True)
                self.visible = True
            else:
                print('Already visible')

        def hide(self):
            if self.visible:
                self.frame.pack_forget()
                self.visible = False
            else:
                print('Already hidden')

        def extract_data(self):
            employee_id = self.entry_id.get()
            month = self.month.get()
            year = self.year.get()
            type = self.toggle_type.get().lower()
            insti = self.toggle_institute.get().lower()

            search = self.data[self.data['HR_EMP_CODE'] == int(employee_id)]
            print(search, employee_id)
            if search.shape[0]:
                self.generate_pdf(search.values[0], month, year, type, insti)
                tkmb.showinfo("PDF Generated", f"PDF generated: {insti}_{type}_{month}_{year}_employee_{employee_id}.pdf")
            else:
                tkmb.showwarning("Error", "Employee ID not found.")

        def generate_pdf(self,employee_data,month,year,type,insti):
            try:
                pdf_file = f"{insti}_{type}_{month}_{year}_employee_{employee_data[0]}.pdf"
                doc = SimpleDocTemplate(pdf_file, pagesize=letter)
                elements = []

                styles = getSampleStyleSheet()
                style_normal = styles["Normal"]
                style_highlight = styles["BodyText"]

                # Title
                title_data = [
                    ["K.J SOMAIYA INSTITUTE OF ENGINEERING & INFORMATION TECHNOLOGY, SOMAIYA AYURVIHAR EVARAD NAGAR, EASTERN EXPRESS HIGHWAY SION"],
                    [f"PAY SLIP FOR THE MONTH OF {month.captialize()}-{year}     31 DAYS     1"]
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

        def copy_row_to_clipboard(self):
            employee_id = self.entry_id.get()

            search = self.data[self.data['HR_EMP_CODE']==employee_id]

            if search.shape[0]:
                pyperclip.copy(','.join(search.values[0]))
                tkmb.showinfo("Copy Row", "Employee data copied to clipboard.")
            else:
                tkmb.showwarning("Error", "Employee ID not found.")

        def back_to_landing(self):
            self.outer.children['landing'].appear()

        def changeType(self,event):
            institute = self.toggle_institute.get()

            self.toggle_type.configure(values = list(self.outer.database[institute]))
            self.toggle_type.set(list(self.outer.database[institute])[0])

        def view_excel(self):
            self.text_excel.delete(1.0, tk.END)

            data = [[i for i in self.data.columns]]
            for index,row in self.data.iterrows():
                row_data = [str(cell) for cell in row.values]
                data.append(row_data)

            col_widths = [max(len(str(cell)) for cell in col) for col in zip(*data)]
            formatted_data = "\n".join([" "+" | ".join([f"{cell:<{col_widths[i]}}" for i, cell in enumerate(row)]) +" " for row in data])
            
            self.text_excel.insert(tk.END, formatted_data)

        def select_file(self):
            file_path = filedialog.askopenfilename(filetypes=[("Excel Files", ".xlsx;.xls")])
            if file_path:
                self.entry_file.delete(0, tk.END)
                self.entry_file.insert(0, file_path)
                self.sheets = list(pd.read_excel(file_path,sheet_name=None).keys())
                self.sheet.set(self.sheets[0])
                self.changeSheets(event=None)
                self.changeView()

        def bulk_print_pdfs(self):
            for i in self.data['HR_EMP_CODE'].values:
                search = self.data[self.data['HR_EMP_CODE']==i]
                self.generate_pdf(search.values[0],self.month,self.year,self.type,self.insti)

            tkmb.showinfo("Bulk Print", "Bulk PDF generation completed.")

        def changeSheets(self,event=None):
            self.sheetList.configure(values=self.sheets)


        def changeView(self,event=None):
            self.data = pd.read_excel(self.entry_file.get(),sheet_name=self.sheet.get())
            print(self.data)
            dataRefine(self.data)
            print(self.data)
            self.view_excel()

    class DBFetch():
        def __init__(self, outer, master):
                self.visible = False
                self.outer = outer
                self.frame = ctk.CTkScrollableFrame(master=master, fg_color=custom_color_scheme["fg_color"])
                self.month = "None"
                self.year = "None"
                self.type = "None"
                self.insti = "None"
                self.data = []

                self.label_date = ctk.CTkLabel(master=self.frame, text=f"{self.month.capitalize()}-{self.year.upper()}", text_color=custom_color_scheme["text_color"], font=("Helvetica", 16))
                self.label_date.pack(pady=10)

                self.label_id = ctk.CTkLabel(master=self.frame, text="Enter Employee ID:", text_color=custom_color_scheme["text_color"], font=("Helvetica", 16))
                self.label_id.pack(pady=5)

                self.entry_id = ctk.CTkEntry(master=self.frame, text_color=custom_color_scheme["text_color"], font=("Helvetica", 16))
                self.entry_id.pack(pady=5)

                button_frame = ctk.CTkFrame(master=self.frame, fg_color=custom_color_scheme["fg_color"])
                button_frame.pack(pady=10)

                self.button_extract = ctk.CTkButton(master=button_frame, text="Generate PDF", command=self.extract_data, fg_color=custom_color_scheme["button_color"], font=("Helvetica", 16))
                self.button_extract.grid(row=0, column=0, padx=5, pady=5)

                self.button_bulk_print = ctk.CTkButton(master=button_frame, text="Bulk Print PDFs", command=self.bulk_print_pdfs, fg_color=custom_color_scheme["button_color"], font=("Helvetica", 16))
                self.button_bulk_print.grid(row=0, column=1, padx=5, pady=5)

                self.button_copy = ctk.CTkButton(master=button_frame, text="Copy Row to Clipboard", command=self.copy_row_to_clipboard, fg_color=custom_color_scheme["button_color"], font=("Helvetica", 16))
                self.button_copy.grid(row=0, column=2, padx=5, pady=5)

                self.button_back_to_interface = ctk.CTkButton(master=button_frame, text="Back", command=self.back_to_interface, fg_color=custom_color_scheme["button_color"], font=("Helvetica", 16))
                self.button_back_to_interface.grid(row=0, column=3, padx=5, pady=5)

                self.text_excel = scrolledtext.ScrolledText(master=self.frame, width=90, height=25, bg="black", fg="white", wrap=tk.NONE, font=("Courier", 12))
                x_scrollbar = Scrollbar(self.frame, orient="horizontal", command=self.text_excel.xview)
                y_scrollbar = Scrollbar(self.frame, command=self.text_excel.yview)

                x_scrollbar.pack(side='bottom', fill='x')
                y_scrollbar.pack(side='right', fill='y')

                self.text_excel.configure(xscrollcommand=x_scrollbar.set, yscrollcommand=y_scrollbar.set)
                self.text_excel.pack(pady=10, padx=10, fill='both', expand=True)

        def appear(self):
            for child in self.outer.children.values():
                child.hide()
                    
            if not self.visible:
                self.frame.pack(pady=20, padx=40, fill='both', expand=True)
                self.visible = True
            else:
                print('Already visible')

        def hide(self):
            if self.visible:
                self.frame.pack_forget()
                self.visible = False
            else:
                print('Already hidden')

        def back_to_interface(self):
            self.outer.children['interface'].appear()

        def load_database(self, month, year, insti, type):
            db = Database(host="localhost", user="root", password="1234", database="somaiya_salary")
            self.data = db.fetchAll(month, year, insti, type)
            db.endDatabase()
            self.view_excel()

        def bulk_print_pdfs(self):
            for i in self.data['HR_EMP_CODE'].values:
                search = self.data[self.data['HR_EMP_CODE'] == i]
                self.generate_pdf(search.values[0], self.month, self.year, self.type, self.insti)

            tkmb.showinfo("Bulk Print", "Bulk PDF generation completed.")

        def view_excel(self):
            self.text_excel.delete(1.0, tk.END)

            data = [[i for i in self.data.columns]]
            for index, row in self.data.iterrows():
                row_data = [str(cell) for cell in row.values]
                data.append(row_data)

            col_widths = [max(len(str(cell)) for cell in col) for col in zip(*data)]
            formatted_data = "\n".join([" " + " | ".join([f"{cell:<{col_widths[i]}}" for i, cell in enumerate(row)]) + " " for row in data])
            
            self.text_excel.insert(tk.END, formatted_data)

        def extract_data(self):
            employee_id = self.entry_id.get()
            search = self.data[self.data['HR_EMP_CODE'] == int(employee_id)]
            print(search, employee_id)
            if search.shape[0]:
                self.generate_pdf(search.values[0], self.month, self.year, self.type, self.insti)
                tkmb.showinfo("PDF Generated", f"PDF generated: {self.insti}_{self.type}_{self.month}_{self.year}_employee_{employee_id}.pdf")
            else:
                tkmb.showwarning("Error", "Employee ID not found.")

        def generate_pdf(self,employee_data,month,year,type,insti):
            try:
                pdf_file = f"{insti}_{type}_{month}_{year}_employee_{employee_data[0]}.pdf"
                doc = SimpleDocTemplate(pdf_file, pagesize=letter)
                elements = []

                styles = getSampleStyleSheet()
                style_normal = styles["Normal"]
                style_highlight = styles["BodyText"]

                # Title
                title_data = [
                    ["K.J SOMAIYA INSTITUTE OF ENGINEERING & INFORMATION TECHNOLOGY, SOMAIYA AYURVIHAR EVARAD NAGAR, EASTERN EXPRESS HIGHWAY SION"],
                    [f"PAY SLIP FOR THE MONTH OF {month}-{year}     31 DAYS     1"]
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
                #tkmb.showinfo("PDF Generated", f"PDF generated: {pdf_file}")
            except Exception as e:
                tkmb.showerror("Error", f"An error occurred while generating the PDF: {str(e)}")


        def copy_row_to_clipboard(self):
            employee_id = self.entry_id.get()

            search = self.data[self.data['HR_EMP_CODE']==employee_id]

            if search.shape[0]:
                pyperclip.copy(','.join(search.values[0]))
                tkmb.showinfo("Copy Row", "Employee data copied to clipboard.")
            else:
                tkmb.showwarning("Error", "Employee ID not found.")

    class DBUpload():
        def __init__(self, outer, master):
            self.visible = False
            self.outer = outer
            self.frame = ctk.CTkScrollableFrame(master=master, fg_color=custom_color_scheme["fg_color"])
            self.month = "None"
            self.year = "None"
            self.type = "None"
            self.insti = "None"
            self.data = []

            self.create_widgets()

        def create_widgets(self):
            self.label_date = ctk.CTkLabel(master=self.frame, text=f"{self.month.capitalize()}-{self.year.upper()}", text_color=custom_color_scheme["text_color"], font=("Helvetica", 16))
            self.label_date.pack(pady=10)

            self.label_id = ctk.CTkLabel(master=self.frame, text="Enter Employee ID:", text_color=custom_color_scheme["text_color"], font=("Helvetica", 16))
            self.label_id.pack(pady=5)

            self.entry_id = ctk.CTkEntry(master=self.frame, text_color=custom_color_scheme["text_color"], font=("Helvetica", 16))
            self.entry_id.pack(pady=5)

            self.button_extract = ctk.CTkButton(master=self.frame, text="Generate PDF", command=self.extract_data, fg_color=custom_color_scheme["button_color"], font=("Helvetica", 16))
            self.button_extract.pack(pady=10)

            self.button_bulk_print = ctk.CTkButton(master=self.frame, text="Bulk Print PDFs", command=self.bulk_print_pdfs, fg_color=custom_color_scheme["button_color"], font=("Helvetica", 16))
            self.button_bulk_print.pack(pady=10)

            self.button_copy = ctk.CTkButton(master=self.frame, text="Copy Row to Clipboard", command=self.copy_row_to_clipboard, fg_color=custom_color_scheme["button_color"], font=("Helvetica", 16))
            self.button_copy.pack(pady=10)

            self.button_back_to_interface = ctk.CTkButton(master=self.frame, text='Back', command=self.back_to_interface, fg_color=custom_color_scheme["button_color"], font=("Helvetica", 16))
            self.button_back_to_interface.pack(pady=12)

            self.text_excel = scrolledtext.ScrolledText(master=self.frame, width=90, height=25, bg="black", fg="white", wrap=tk.NONE, font=("Courier", 12))
            x_scrollbar = Scrollbar(self.frame, orient="horizontal", command=self.text_excel.xview)
            y_scrollbar = Scrollbar(self.frame, command=self.text_excel.yview)

            x_scrollbar.pack(side='bottom', fill='x')
            y_scrollbar.pack(side='right', fill='y')

            self.text_excel.configure(xscrollcommand=x_scrollbar.set, yscrollcommand=y_scrollbar.set)
            self.text_excel.pack(pady=10, padx=10, fill='both', expand=True)

        def appear(self):
            for child in self.outer.children.values():
                child.hide()

            if not self.visible:
                self.frame.pack(pady=20, padx=40, fill='both', expand=True)
                self.visible = True
            else:
                print('Already visible')

        def hide(self):
            if self.visible:
                self.frame.pack_forget()
                self.visible = False
            else:
                print('Already hidden')

        def back_to_interface(self):
            self.outer.children['interface'].appear()

        def load_database(self, month, year, insti, type):
            db = Database(host="localhost", user="root", password="1234", database="somaiya_salary")
            self.data = db.fetchAll(month, year, insti, type)
            db.endDatabase()
            self.view_excel()

        def bulk_print_pdfs(self):
            for emp_code in self.data['HR_EMP_CODE'].values:
                search = self.data[self.data['HR_EMP_CODE'] == emp_code]
                self.generate_pdf(search.values[0], self.month, self.year, self.type, self.insti)

            tkmb.showinfo("Bulk Print", "Bulk PDF generation completed.")

        def view_excel(self):
            self.text_excel.delete(1.0, tk.END)

            data = [[i for i in self.data.columns]]
            for _, row in self.data.iterrows():
                row_data = [str(cell) for cell in row.values]
                data.append(row_data)

            col_widths = [max(len(str(cell)) for cell in col) for col in zip(*data)]
            formatted_data = "\n".join([" " + " | ".join([f"{cell:<{col_widths[i]}}" for i, cell in enumerate(row)]) + " " for row in data])

            self.text_excel.insert(tk.END, formatted_data)

        def extract_data(self):
            employee_id = self.entry_id.get()
            search = self.data[self.data['HR_EMP_CODE'] == int(employee_id)]

            if search.shape[0]:
                self.generate_pdf(search.values[0], self.month, self.year, self.type, self.insti)
                tkmb.showinfo("PDF Generated", f"PDF generated: {self.insti}{self.type}{self.month}{self.year}_employee{employee_id}.pdf")
            else:
                tkmb.showwarning("Error", "Employee ID not found.")


        def generate_pdf(self,employee_data,month,year,type,insti):
            try:
                pdf_file = f"{insti}_{type}_{month}_{year}_employee_{employee_data[0]}.pdf"
                doc = SimpleDocTemplate(pdf_file, pagesize=letter)
                elements = []

                styles = getSampleStyleSheet()
                style_normal = styles["Normal"]
                style_highlight = styles["BodyText"]

                # Title
                title_data = [
                    ["K.J SOMAIYA INSTITUTE OF ENGINEERING & INFORMATION TECHNOLOGY, SOMAIYA AYURVIHAR EVARAD NAGAR, EASTERN EXPRESS HIGHWAY SION"],
                    [f"PAY SLIP FOR THE MONTH OF {month}-{year}     31 DAYS     1"]
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
                #tkmb.showinfo("PDF Generated", f"PDF generated: {pdf_file}")
            except Exception as e:
                tkmb.showerror("Error", f"An error occurred while generating the PDF: {str(e)}")


        def copy_row_to_clipboard(self):
            employee_id = self.entry_id.get()

            search = self.data[self.data['HR_EMP_CODE']==employee_id]

            if search.shape[0]:
                pyperclip.copy(','.join(search.values[0]))
                tkmb.showinfo("Copy Row", "Employee data copied to clipboard.")
            else:
                tkmb.showwarning("Error", "Employee ID not found.")

# Apply custom colors
custom_color_scheme = {
    "fg_color": "white",
    "button_color": "dark red",
    "text_color": "black",
    "combo_box_color": "white"  # Added for combo box color
}


app = App()

app.app.mainloop()

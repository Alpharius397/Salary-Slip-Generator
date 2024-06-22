import customtkinter as ctk
import tkinter.messagebox as tkmb
import tkinter as tk
from tkinter import filedialog, scrolledtext
from openpyxl import load_workbook
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
import pyperclip
import os

# Set custom appearance and color theme
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")  # The custom color theme will be applied manually

# Initialize main application
app = ctk.CTk()
screen_width = app.winfo_screenwidth()
screen_height = app.winfo_screenheight()
app.geometry(f"{screen_width}x{screen_height}")
app.title("Salary-slip Generator")

def select_file():
    file_path = filedialog.askopenfilename(filetypes=[("Excel Files", "*.xlsx;*.xls")])
    if file_path:
        entry_file.delete(0, tk.END)
        entry_file.insert(0, file_path)
        view_excel(file_path)

def view_excel(file_path):
    text_excel.delete(1.0, tk.END)
    workbook = load_workbook(file_path)
    sheet = workbook.active

    data = []
    for row in sheet.iter_rows():
        row_data = [str(cell.value) if cell.value is not None else "" for cell in row]
        data.append(row_data)

    col_widths = [max(len(str(cell)) for cell in col) for col in zip(*data)]
    formatted_data = "\n".join(" | ".join(f"{cell:<{col_widths[i]}}" for i, cell in enumerate(row)) for row in data)
    
    text_excel.insert(tk.END, formatted_data)

def extract_data():
    file_path = entry_file.get()
    student_id = entry_id.get()
    if not file_path:
        return

    workbook = load_workbook(file_path)
    sheet = workbook.active

    for row in sheet.iter_rows(min_row=2):
        if str(row[0].value) == student_id:
            student_data = [cell.value for cell in row]
            generate_pdf(student_data)
            break
    else:
        tkmb.showwarning("Error", "Employee ID not found.")

def generate_pdf(employee_data):
    pdf_file = f"employee_{employee_data[0]}.pdf"
    doc = SimpleDocTemplate(pdf_file, pagesize=letter)
    elements = []

    styles = getSampleStyleSheet()
    style_normal = styles["Normal"]
    style_highlight = styles["BodyText"]

    # Title
    title_data = [
        ["K.J SOMAIYA INSTITUTE OF TECHNOLOGY, SOMAIYA AYURVIHAR EVARAD NAGAR, EASTERN EXPRESS HIGHWAY SION"],
        [f"PAY SLIP FOR THE MONTH OF May-24     31 DAYS     1"]
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
    employee_info_table = Table(employee_info_data, colWidths=[110, 160, 120, 160])
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
        ["Basic Pay", employee_data[10], "PROF TAX", employee_data[20]],
        ["HRA", employee_data[11], "PF", employee_data[21]],
        ["TA/ Conveyance", employee_data[12], "TDS", employee_data[22]],
        ["SPECIAL ALW", employee_data[13], "LIC", employee_data[23]],
        ["Salary Arrears", employee_data[14], "Principle loan amount PM", employee_data[24]],
        ["Books and Periodicals", employee_data[15], "Interest 6% on bal amount", employee_data[25]],
        ["Telephone", employee_data[16], "Other Deduction", employee_data[26]],
        ["Medical", employee_data[17], "", ""],
        ["LTA", employee_data[18], "", ""],
        ["GROSS SALARY", employee_data[19], "TOTAL DEDUCTION", employee_data[27]],
        ["NET SALARY PAYABLE", employee_data[28], "", ""]
    ]
    earnings_deductions_table = Table(earnings_deductions_data, colWidths=[120, 120, 120, 120])
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
    tkmb.showinfo("PDF Generated", f"PDF generated: {pdf_file}")

def copy_row_to_clipboard():
    file_path = entry_file.get()
    student_id = entry_id.get()
    if not file_path:
        return

    workbook = load_workbook(file_path)
    sheet = workbook.active

    for row in sheet.iter_rows(min_row=2):
        if str(row[0].value) == student_id:
            student_data = [str(cell.value) for cell in row]
            row_data = "\t".join(student_data)
            pyperclip.copy(row_data)
            tkmb.showinfo("Copy Row", "Employee data copied to clipboard.")
            break
    else:
        tkmb.showwarning("Error", "Employee ID not found.")

def bulk_print_pdfs():
    file_path = entry_file.get()
    if not file_path:
        return

    workbook = load_workbook(file_path)
    sheet = workbook.active

    for row in sheet.iter_rows(min_row=2):
        employee_data = [cell.value for cell in row]
        generate_pdf(employee_data)
    
    tkmb.showinfo("Bulk Print", "Bulk PDF generation completed.")

def check_excel_file():
    month = entry_month.get()
    year = entry_year.get()
    institute = toggle_institute.get()
    
    file_name = f"{institute}_{month}_{year}.xlsx"
    if os.path.exists(file_name):
        entry_file.delete(0, tk.END)
        entry_file.insert(0, file_name)
        tkmb.showinfo("File Found", "The specified Excel file is found.")
    else:
        tkmb.showwarning("File Not Found", "The specified Excel file is not found. Please upload the required file.")
    
    show_file_view_page()

def show_file_view_page():
    frame_input.pack_forget()
    frame_view.pack(pady=20, padx=40, fill='both', expand=True)

def show_login_page():
    frame_login.pack(pady=20, padx=40, fill='both', expand=True)

def show_input_page():
    frame_login.pack_forget()
    frame_input.pack(pady=20, padx=40, fill='both', expand=True)

def login():
    username = "admin"
    password = "kjs2024"
    if user_entry.get() == username and user_pass.get() == password:
        tkmb.showinfo(title="Login Successful", message="You have logged in Successfully")
        show_input_page()
    elif user_entry.get() == username and user_pass.get() != password:
        tkmb.showwarning(title='Wrong password', message='Please check your password')
    elif user_entry.get() != username and user_pass.get() == password:
        tkmb.showwarning(title='Wrong username', message='Please check your username')
    else:
        tkmb.showerror(title="Login Failed", message="Invalid Username and password")

# Apply custom colors
custom_color_scheme = {
    "fg_color": "white",
    "button_color": "dark red",
    "text_color": "black"
}

# Login Frame
frame_login = ctk.CTkScrollableFrame(master=app, fg_color=custom_color_scheme["fg_color"])
frame_login.pack(pady=20, padx=40, fill='both', expand=True)

label_login = ctk.CTkLabel(master=frame_login, text='Admin login page', text_color=custom_color_scheme["text_color"], font=("Helvetica", 16))
label_login.pack(pady=20)

user_entry = ctk.CTkEntry(master=frame_login, placeholder_text="Username", text_color=custom_color_scheme["text_color"], font=("Helvetica", 16))
user_entry.pack(pady=12, padx=10)

user_pass = ctk.CTkEntry(master=frame_login, placeholder_text="Password", show="*", text_color=custom_color_scheme["text_color"], font=("Helvetica", 16))
user_pass.pack(pady=12, padx=10)

button_login = ctk.CTkButton(master=frame_login, text='Login', command=login, fg_color=custom_color_scheme["button_color"], font=("Helvetica", 16))
button_login.pack(pady=12, padx=10)

checkbox = ctk.CTkCheckBox(master=frame_login, text='Remember Me', fg_color=custom_color_scheme["button_color"], font=("Helvetica", 16))
checkbox.pack(pady=12, padx=10)

# Input Frame
frame_input = ctk.CTkScrollableFrame(master=app, fg_color=custom_color_scheme["fg_color"])
frame_input.pack_forget()

label_input = ctk.CTkLabel(master=frame_input, text="Enter Details", text_color=custom_color_scheme["text_color"], font=("Helvetica", 16))
label_input.pack(pady=20)

entry_month = ctk.CTkEntry(master=frame_input, placeholder_text="Month (e.g., May)", text_color=custom_color_scheme["text_color"], font=("Helvetica", 16))
entry_month.pack(pady=12, padx=10)

entry_year = ctk.CTkEntry(master=frame_input, placeholder_text="Year (e.g., 2024)", text_color=custom_color_scheme["text_color"], font=("Helvetica", 16))
entry_year.pack(pady=12, padx=10)

toggle_institute = ctk.CTkComboBox(master=frame_input, values=["Somaiya", "SVV"], fg_color=custom_color_scheme["button_color"], font=("Helvetica", 16))
toggle_institute.pack(pady=12, padx=10)

button_continue = ctk.CTkButton(master=frame_input, text='Continue', command=check_excel_file, fg_color=custom_color_scheme["button_color"], font=("Helvetica", 16))
button_continue.pack(pady=12, padx=10)

# File View Frame
frame_view = ctk.CTkScrollableFrame(master=app, fg_color=custom_color_scheme["fg_color"])
frame_view.pack_forget()

label_file = ctk.CTkLabel(master=frame_view, text="Selected Excel File:", text_color=custom_color_scheme["text_color"], font=("Helvetica", 16))
label_file.pack(pady=10)

entry_file = ctk.CTkEntry(master=frame_view, width=50, text_color=custom_color_scheme["text_color"], font=("Helvetica", 16))
entry_file.pack(pady=5)

button_browse = ctk.CTkButton(master=frame_view, text="Browse", command=select_file, fg_color=custom_color_scheme["button_color"], font=("Helvetica", 16))
button_browse.pack(pady=5)

label_id = ctk.CTkLabel(master=frame_view, text="Enter Employee ID:", text_color=custom_color_scheme["text_color"], font=("Helvetica", 16))
label_id.pack()

entry_id = ctk.CTkEntry(master=frame_view, text_color=custom_color_scheme["text_color"], font=("Helvetica", 16))
entry_id.pack(pady=5)

button_extract = ctk.CTkButton(master=frame_view, text="Extract Data", command=extract_data, fg_color=custom_color_scheme["button_color"], font=("Helvetica", 16))
button_extract.pack(pady=10)

button_bulk_print = ctk.CTkButton(master=frame_view, text="Bulk Print PDFs", command=bulk_print_pdfs, fg_color=custom_color_scheme["button_color"], font=("Helvetica", 16))
button_bulk_print.pack(pady=10)

button_copy = ctk.CTkButton(master=frame_view, text="Copy Row to Clipboard", command=copy_row_to_clipboard, fg_color=custom_color_scheme["button_color"], font=("Helvetica", 16))
button_copy.pack(pady=10)

text_excel = scrolledtext.ScrolledText(master=frame_view, width=90, height=25, bg="black", fg="white", wrap=tk.NONE, font=("Courier", 12))
text_excel.pack(pady=10, fill='both', expand=True)

show_login_page()
app.mainloop()

import re
import json
from pathlib import Path
import os
from default import DEFAULT_HTML, DEFAULT_JSON
from logger import Logger

class PDFTemplate:
	VAR_NAME:str = r'[a-zA-Z0-9._+-/%]+'
	TEMPLATE:str = r'{{[a-zA-Z0-9._+-/%]+}}'
    
	def __init__(self,dir_path:Path,log:Logger) -> None:
		self.json_path = os.path.join(dir_path,'json')
		self.html_path = os.path.join(dir_path,'html')
		self.chosen_json:str = None
		self.chosen_html:str = None
		self.log = log

	def load_default(self) -> 'PDFTemplate':
		status, msg = self.make_file(os.path.join(self.json_path,'somaiya.json'),json.dumps(DEFAULT_JSON))
		
		if(status):
			self.log.write_info(msg)

		status, msg = self.make_file(os.path.join(self.html_path,'somaiya.html'),DEFAULT_HTML)

		if(status):
			self.log.write_info(msg)
   
		return self

	def check_json(self) -> list[str]:
		return [i for i in os.listdir(self.json_path) if i[-4:]=="json"]

	def check_html(self) -> list[str]:
		return [i for i in os.listdir(self.html_path) if i[-4:]=="html"]

	def make_file(self, file_name, default:str = '') -> tuple[bool,str]:
		status = False
		msg = f"File Created: {file_name}"
        
		try:
			os.makedirs(os.path.dirname(file_name))
		except Exception as e:
			self.log.write_error(self.log.get_error_info(e))
		
		try:
			if(not os.path.exists(file_name)):
				with open(file_name,'w') as f:
					f.write(default)
					status = True
	
		except Exception as e:
			status = False
			msg = self.log.get_error_info(e)
    
		return status, msg

	def load_html(self, file_name:str) -> str | None:
		return self.load_file(self.html_path,file_name)

	def load_json(self, file_name:str) -> dict:
		try:
			memo = json.loads(self.load_file(self.json_path,file_name))
			return memo

		except Exception as e:
			self.log.write_error(self.log.get_error_info(e))
		
		return {}

	def load_file(self, dir_name:Path, file_name:Path) -> str:
		_path = os.path.join(dir_name,file_name)
		_file:str = None

		if(os.path.exists(_path)):
			try:
				with open(_path,'r') as f:
					_file = f.read()
				return _file

			except Exception as e:
				self.log.write_error(self.log.get_error_info(e))

		return None

	def _parse_html(self, html_file:str) -> tuple[str,dict[str,str]]:

		html_file = html_file.replace('%',f"%%")
		vars = re.findall(self.TEMPLATE,html_file)
		memo = {}


		for i in vars:
			word = re.findall(self.VAR_NAME,i)

			if(word):
				curr = next(iter(word))
				memo[curr] = None
				html_file = html_file.replace(i,f"%({curr})s")

		return html_file, memo

	""" preprocess the keys to escape %"""
	def render_html(self, html_file:str, memo:dict[str,str]) -> str:
		html = self.load_html(html_file)

		memo = {i.replace('%',f"%%"):j for i,j in memo.items()}

		if(html is None):
			self.log.write_error("Error Loading Html file!")
			return None

		html, vars = self._parse_html(html)
		vars.update(memo)
		print(vars)
		return html % vars

# Log = Logger(os.path.dirname(__file__))
# pdf = PDFTemplate(os.path.dirname(__file__),Log)
# html = pdf.check_html()

# with open('def.html','w') as f:
#     f.write(pdf.render_html(html[0],{"hra%":13}))
import re
from json import loads, dumps
from pathlib import Path
import os
from type import *
from default import DEFAULT_HTML, DEFAULT_NON_TEACHING_JSON, DEFAULT_TEACHING_JSON
from logger import Logger


class PDFTemplate:
	TEMPLATE: str = r'{{([a-zA-Z0-9._+-/%]+)}}'
    
	def __init__(self, dir_path: Path, log: Logger) -> None:
		self.json_path =  Path(dir_path, "json")
		self.html_path = Path(dir_path, "html")
		self.chosen_json: Path = None
		self.chosen_html: Path = None
		self.log = log

	def _load_defaults(self, path: Path, fileType: Literal['json', 'html'], **kwargs: str) -> None:
		for filename, data in kwargs.items():
			status, msg = self.make_file(Path(path, f'{filename.replace("_",".").strip(" .")}.{fileType}'), data)
		
			if(status):
				self.log.write_info(msg)
			else:
				self.log.write_error(msg)

	def load_default(self) -> 'PDFTemplate':
		self._load_defaults(
			path = self.json_path, 
			fileType = 'json', 
			teaching = dumps(DEFAULT_TEACHING_JSON), 
			non_teaching = dumps(DEFAULT_NON_TEACHING_JSON)
		)
	
		self._load_defaults(
			path=self.html_path,
			fileType='html',
			teaching = DEFAULT_HTML
		)	

		return self

	def check_json(self) -> list[str]:
		try:
			return [i.name for i in self.json_path.iterdir() if i.suffix ==".json"]
		except Exception as e:
			self.log.write_error(self.log.get_error_info(e))
		return []

	def check_html(self) -> list[str]:
		try:
			return [i.name for i in self.html_path.iterdir() if i.suffix == ".html"]
		except Exception as e:
			self.log.write_error(self.log.get_error_info(e))
		return []


	def make_file(self, file_name: Path, default: Optional[str] = None) -> tuple[bool,str]:
		status = False
		msg = f"File Created: {file_name}"
        
		try:
			if(( path := str(file_name.parent) ) in [str(self.html_path), str(self.json_path)]):
				os.makedirs(path)
			else:
				return status, f"File path must be within these paths only: {str(self.html_path)}, {str(self.json_path)}"
	
		except Exception as e:
			self.log.write_error(self.log.get_error_info(e))
		
		try:
			if(not file_name.exists()):
				file_name.touch()
    
				if(default is not None): file_name.write_text(default)
				status = True
	
		except Exception as e:
			status = False
			msg = self.log.get_error_info(e)
    
		return status, msg

	def load_html(self, file_name:Path) -> tuple[str, dict[str, NullStr]]:
		memo: dict[str, NullStr] = {}
		new_html_file = ""

		try:
			if(not file_name.exists()):
				return new_html_file, memo

			with open(file_name.resolve(), "r") as file:

				while (lines := file.readline()):
					lines = lines.replace("%", f"%%")
		
					varIter = re.finditer(self.TEMPLATE, lines)
			
					for i in varIter:
						try:
							if(i and (curr := i.group(1))):
								memo[curr] = None
								lines = lines.replace(curr, f"%({curr})s")
		
						except Exception as e:
							self.log.write_error(self.log.get_error_info(e))
							

					new_html_file += lines + '\n'
		except Exception as e:
			self.log.write_error(self.log.get_error_info(e))
	
		return new_html_file.strip(" \n"), memo
	

	def load_json(self, file_name:Path) -> dict:
		try:
			if( (text := self.load_file(self.json_path, file_name)) is not None):
				memo = loads(text)
				return memo

		except Exception as e:
			self.log.write_error(self.log.get_error_info(e))
		
		return {}

	def load_file(self, dir_name:Path, file_name:Path) -> NullStr:
		path = Path(dir_name, file_name)

		try:
			if(path.exists()):
				return path.read_text()
		except Exception as e:
			self.log.write_error(self.log.get_error_info(e))
    
		return None

	def render_html(self, html_file: Path, memo:dict[str,str]) -> str:
		
		""" preprocess the keys to escape % """
		memo = {i.replace('%',f"%%"):j for i,j in memo.items()}

		html, vars = self.load_html(html_file)
		vars.update(memo)
	
		return html % vars

import re
from json import loads
from pathlib import Path
import os
from typing import Optional
from src.constants import APP_PATH
from src.dataTypes import NullStr
from src.logger import ERROR_LOG, Logger

class PDFTemplate:
    TEMPLATE: str = r"{{([a-zA-Z0-9._+-/%]+)}}"

    def __init__(self, dir_path: Path, log: Logger) -> None:
        self.json_path = Path(dir_path, "json")
        self.html_path = Path(dir_path, "html")
        self.chosen_json: Optional[Path] = None
        self.chosen_html: Optional[Path] = None
        self.log = log

    def check_json(self) -> list[str]:
        try:
            return [i.name for i in self.json_path.iterdir() if i.suffix == ".json"]
        except Exception as e:
            self.log.write_error(self.log.get_error_info(e), "PARSE")

        return []

    def check_html(self) -> list[str]:
        try:
            return [i.name for i in self.html_path.iterdir() if i.suffix == ".html"]
        except Exception as e:
            self.log.write_error(self.log.get_error_info(e), "PARSE")

        return []

    def make_file(
        self, file_name: Path, data: str
    ) -> tuple[bool, str]:

        try:
            if (path := str(file_name.parent)) in [
                str(self.html_path),
                str(self.json_path),
            ]:
                os.makedirs(path, exist_ok=True)
            else:
                return (
                    False,
                    f"File path must be within these paths only: {str(self.html_path)}, {str(self.json_path)}",
                )

        except Exception as e:
            self.log.write_error(self.log.get_error_info(e), "PARSE")

        try:
            file_name.touch()

            file_name.write_text(data)
                
            return True, f"File Created: {file_name}"

        except Exception as e:
            return False, self.log.get_error_info(e)

    def load_html(self, file_path: Path) -> tuple[str, dict[str, NullStr]]:
        memo: dict[str, NullStr] = {}
        new_html_file = ""

        try:
            file_name = Path(self.html_path, file_path)
            if not file_name.exists():
                return new_html_file, memo

            with open(file_name.resolve(), "r") as file:
                while lines := file.readline():
                    lines = lines.replace("%", "%%")

                    varIter = re.finditer(self.TEMPLATE, lines)

                    for i in varIter:
                        try:
                            if i and (something_cause_me_no_brain := i.group(0, 1)):
                                complete, curr = something_cause_me_no_brain
                                memo[curr] = None
                                lines = lines.replace(complete, f"%({curr})s")

                        except Exception as e:
                            self.log.write_error(self.log.get_error_info(e), "PARSE")

                    new_html_file += lines + "\n"
        except Exception as e:
            self.log.write_error(self.log.get_error_info(e), "PARSE")

        return new_html_file.strip(" \n"), memo

    def load_json(self, file_name: Path) -> dict:
        try:
            if (text := self.load_file(self.json_path, file_name)) is not None:
                memo = loads(text)
                return memo

        except Exception as e:
            self.log.write_error(self.log.get_error_info(e), "PARSE")

        return {}

    def load_file(self, dir_name: Path, file_name: Path) -> NullStr:
        path = Path(dir_name, file_name)

        try:
            if path.exists():
                return path.read_text()
        except Exception as e:
            self.log.write_error(self.log.get_error_info(e), "PARSE")

        return None

    def render_html(self, html_file: Path, memo: dict[str, str]) -> str:
        """preprocess the keys to escape %"""
        memo = {i.replace("%", "%%"): j for i, j in memo.items()}

        html, vars = self.load_html(html_file)
        vars.update(memo)

        return html % vars

PDF_TEMPLATE = PDFTemplate(APP_PATH, ERROR_LOG)

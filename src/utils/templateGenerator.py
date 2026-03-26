import json
from multiprocessing import Queue
from pathlib import Path
import pandas as pd  # type: ignore
from src.constants import TEMPLATE_COLUMN, TEMPLATE_SHEET
from src.default import TEMPLATE
from src.logger import ERROR_LOG
from src.parser import PDF_TEMPLATE
from src.utils.common import mapping, text_clean


class TemplateGenerator:
    counter: int = 0

    @staticmethod
    def make_everything(elems: dict[str, str]) -> tuple[str, dict[int, str]]:
        html_string = ""
        jsonDict: dict[int, str] = {}

        for key, val in elems.items():
            count = TemplateGenerator.counter
            html_string += (
                "<tr><td>{0}:</td>\n<td><span>{{{{{1}}}}}</span></td></tr>\n".format(
                    key, count
                )
            )  # { escapes {
            jsonDict[count] = text_clean(val)
            TemplateGenerator.counter += 1

        return html_string, jsonDict

    @staticmethod
    def make_template(
        file_name: str, data: dict[str, pd.DataFrame], queue: Queue
    ) -> None:
        TemplateGenerator.counter = 0
        memo: dict[str, str] = {}
        jsonDict: dict[int, str] = {}

        for sheet in TEMPLATE_SHEET:
            sheetName = sheet.strip().replace(" ", "_")
            memo[sheetName] = ""

            sheetData = data.get(sheet, pd.DataFrame())

            if not all((i in sheetData.columns) for i in TEMPLATE_COLUMN):
                continue

            _name, _title = TEMPLATE_COLUMN
            columns = sheetData.columns
            column_memo = {j: i for i, j in enumerate(columns)}

            if ((name := mapping(columns, _name)) is not None) and (
                (title := mapping(columns, _title)) is not None
            ):
                row_data = sheetData.to_numpy()

                memo[sheetName], tempDict = TemplateGenerator.make_everything(
                    {
                        row[column_memo[name]]: str(row[column_memo[title]])
                        .replace("\n", "")
                        .strip()
                        for row in row_data
                    }
                )

                jsonDict.update(tempDict)

        html_string = TEMPLATE % memo
        file_name = file_name.replace(" ", "_").strip(" .")

        html_status = PDF_TEMPLATE.make_file(
            PDF_TEMPLATE.html_path.joinpath(f"{file_name}.html"), html_string
        )

        if not html_status:
            queue.put(False)
            return

        json_status = PDF_TEMPLATE.make_file(
            PDF_TEMPLATE.json_path.joinpath(f"{file_name}.json"),
            json.dumps(jsonDict, ensure_ascii=False),
        )

        queue.put(json_status)

    @staticmethod
    def make_excel(
        file_name: Path, data: dict[str, pd.DataFrame], queue: Queue
    ) -> None:
        TemplateGenerator.counter = 0
        columnsList: list[str] = []

        for sheet in TEMPLATE_SHEET:
            sheetData = data.get(sheet, pd.DataFrame())
            if not all((i in sheetData.columns) for i in TEMPLATE_COLUMN):
                continue

            _name, _title = TEMPLATE_COLUMN
            columns = sheetData.columns
            column_memo = {j: i for i, j in enumerate(columns)}

            if ((_ := mapping(columns, _name)) is not None) and (
                (title := mapping(columns, _title)) is not None
            ):
                row_data = sheetData.to_numpy()

                for row in row_data:
                    columnsList.append(row[column_memo[title]])

        try:
            a = pd.DataFrame({}, columns=columnsList)
            a.to_excel(file_name, index=False)

            queue.put((True, "Excel File generated successfully"))
        except Exception as e:
            ERROR_LOG.write_error(ERROR_LOG.get_error_info(e))

            queue.put((False, "Excel File generation failed"))

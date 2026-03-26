from asyncio import gather, run
from multiprocessing import Queue
from pathlib import Path
import types
import pandas as pd  # type: ignore
from src.constants import CODE_COL
from src.dataTypes import MonthList, NullStr
from src.parser import PDFTemplate
from src.utils.common import mapping, text_clean
from src.utils.pdfGenerator import PDFGenerator


class PandaWrapper:
    """Panda wrapper for process"""

    def __init__(
        self,
        servitor: pd.DataFrame,
        identification_rosette: str,
        pdf_template: PDFTemplate,
    ) -> None:
        self.servitor = servitor
        self.identification_rosette = identification_rosette
        self.pdf = pdf_template
        self.columns = {j: i for i, j in enumerate(servitor.columns)}
        self.vars: dict[str, NullStr] = {}
        self.html_file: str = ""
        self.column_auspex: dict[str, NullStr] = {}

    def load_scriptures(self) -> None:
        if self.pdf.chosen_json is not None:
            self.column_auspex = {
                i: mapping(list(self.columns.keys()), j)
                for i, j in self.pdf.load_json(self.pdf.chosen_json).items()
            }
            self.column_auspex[CODE_COL] = self.identification_rosette
            self.column_auspex["branch"] = "Sion"

    def find_by_id(self, queue: Queue, emp_id: str):
        """Finds employee by emp_id in identification_rosette column of Dataframe"""
        search_result = self.servitor[
            self.servitor[self.identification_rosette] == emp_id
        ]
        if not search_result.empty:
            queue.put(self.litany_of_auspex(search_result.iloc[[0]]))
        else:
            queue.put(self.litany_of_failure())

    def litany_of_failure(self):
        """The labyrinth does not bears the knowledge you wish to seek, Tech Adept"""
        return None

    def litany_of_auspex(self, search_result: pd.DataFrame):
        """Praised be the machine spirit of the blessed augurs (Returns data about id, which should exist)"""
        return search_result

    @staticmethod
    async def get_success(tasks: list[types.CoroutineType]) -> tuple[int, int]:
        result = await gather(*tasks)

        success, total = 0, 0

        for i in result:
            status, _ = i
            if status:
                success += 1
            total += 1

        return success, total

    def litany_of_scrolls(
        self, queue: Queue, dropzone: Path, month: MonthList, year: int
    ):
        """Oh holy generator, grants us the sacred ink of thou's blessed blood (BulkPrint Process)"""
        task_completed = 0
        total_task = self.servitor.shape[0]
        tasks = []
        self.load_scriptures()

        for data in self.servitor.itertuples(index=False):
            emp_data = {
                key: (
                    val or "-"
                    if (val not in set(self.columns.keys()))
                    else text_clean(data[self.columns[val]])
                )
                for key, val in self.column_auspex.items()
            }
            emp_data.update({"month": month.capitalize(), "year": str(year)})

            if self.pdf.chosen_html is not None:
                html_content = self.pdf.render_html(self.pdf.chosen_html, emp_data)

                tasks.append(
                    PDFGenerator.generate_many_pdf(
                        emp_data.get(CODE_COL, "none"), html_content, dropzone
                    )
                )

        task_completed, _ = run(PandaWrapper.get_success(tasks)) # type: ignore

        queue.put((task_completed, total_task))

    def litany_of_scroll(
        self, queue: Queue, data_slate_path: Path, month: str, year: int, emp_id: str
    ):
        """Oh holy generator, grants us the sacred ink of thou's blessed blood (SinglePrint Process)"""

        search_result = self.servitor[
            self.servitor[self.identification_rosette] == emp_id
        ]
        self.load_scriptures()

        if not search_result.empty:
            data = search_result.iloc[0].to_numpy()
            emp_data = {
                key: (
                    val or "-"
                    if (val not in set(self.columns.keys()))
                    else text_clean(data[self.columns[val]])
                )
                for key, val in self.column_auspex.items()
            }
            emp_data.update({"month": month.capitalize(), "year": str(year)})

            if self.pdf.chosen_html is not None:
                html_content = self.pdf.render_html(self.pdf.chosen_html, emp_data)

                status, msg = PDFGenerator.generate_one_pdf(
                    emp_data.get(CODE_COL, "none"), html_content, data_slate_path
                )
            else:
                status, msg = None, "Something went wrong"
            queue.put((status, msg))

        else:
            queue.put((None, f"Employee Code '{emp_id}' was not found"))

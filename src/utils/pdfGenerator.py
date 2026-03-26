from asyncio import to_thread
from pathlib import Path
import re
import sys
import os
from typing import Optional
import pdfkit  # type: ignore
from src.logger import ERROR_LOG
from src.constants import FILE_REGEX, IS_EXE
from src.utils.common import file_clean


def find_wkhtmltopdf() -> Optional[pdfkit.pdfkit.Configuration]:
    """Find the bundled wkhtmltopdf binary"""
    WKHTML_PATH = str(getattr(sys, "_MEIPASS")) if IS_EXE else os.path.abspath(".")

    try:
        wkhtmltopdf = str(Path(str(WKHTML_PATH)).joinpath("bin", "wkhtmltopdf.exe"))
        return pdfkit.configuration(wkhtmltopdf=wkhtmltopdf)
    except (IOError, FileNotFoundError) as e:
        ERROR_LOG.write_error(ERROR_LOG.get_error_info(e), "WKHTMLTOPDF")

    return None


class PDFGenerator:
    """Class to handle everything related to PDF Generation"""

    @staticmethod
    def _generate_pdf(pdf_file_path: Path, html_content: str) -> None:
        """Generates the pdf from html"""

        pdfkit.from_string(
            html_content,
            str(pdf_file_path),
            options={
                "page-size": "A4",
                "margin-top": "0.5in",
                "margin-right": "0.5in",
                "margin-bottom": "0.5in",
                "margin-left": "0.5in",
                "no-outline": None,
            },
            configuration=find_wkhtmltopdf(),
        )

    @staticmethod
    def generate_one_pdf(
        name: str, html_content: str, file_path: Path
    ) -> tuple[bool, str]:
        """Wrapper Function to generate one pdf"""

        try:
            where = Path(file_path).parent

            filename = f"employee_{name}.pdf"

            if re.match(FILE_REGEX, filename):
                pdf_file = where.joinpath(filename)
                PDFGenerator._generate_pdf(pdf_file, html_content)
                return (True, "PDF Generation Successful")
            else:
                ERROR_LOG.write_info(
                    f"{filename} does not match pattern '{FILE_REGEX}'"
                )
                return (False, f"{filename} does not match pattern '{FILE_REGEX}'")

        except Exception as e:
            ERROR_LOG.write_error(ERROR_LOG.get_error_info(e))

            return (False, f"An error occurred while generating the PDF: {str(e)}")

    @staticmethod
    async def generate_many_pdf(
        name: str, html_content: str, where: Path
    ) -> tuple[bool, str]:
        """Wrapper Function to generate multiple pdfs"""

        try:
            filename = f"employee_{file_clean(name)}.pdf"
            if re.match(FILE_REGEX, filename):
                pdf_file = where.joinpath(filename)
                await to_thread(PDFGenerator._generate_pdf, pdf_file, html_content)
                return (True, "PDF Generation Successful")
            else:
                ERROR_LOG.write_info(
                    f"{filename} does not match pattern '{FILE_REGEX}'"
                )
                return (False, f"{filename} does not match pattern '{FILE_REGEX}'")

        except Exception as e:
            ERROR_LOG.write_error(ERROR_LOG.get_error_info(e))
            return (False, f"An error occurred while generating the PDF: {str(e)}")

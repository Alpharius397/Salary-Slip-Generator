import io
from multiprocessing import Queue
from pathlib import Path
from typing import Optional
import msoffcrypto  # type: ignore
import pandas as pd  # type: ignore
from src.database import dataRefine
from src.logger import ERROR_LOG


class Decryption:
    """Handles file decryption"""

    @staticmethod
    def is_encrypted(file: io.BufferedReader) -> bool:
        """Checks if file is encrypted"""
        return msoffcrypto.OfficeFile(file).is_encrypted()

    @staticmethod
    def decrypting_file(
        file_path: Path, decrypted: io.BytesIO, password: str
    ) -> tuple[bool, io.BytesIO]:
        """Decrypts the file and extracts content into BytesIO"""

        success = False
        try:
            with open(file_path.resolve(), "rb") as f:
                file = msoffcrypto.OfficeFile(f)
                file.load_key(password=password)
                file.decrypt(decrypted)
                success = True

        except msoffcrypto.exceptions.InvalidKeyError as e:
            ERROR_LOG.write_error(ERROR_LOG.get_error_info(e))

        except msoffcrypto.exceptions.DecryptionError as e:
            ERROR_LOG.write_error(ERROR_LOG.get_error_info(e))

        except Exception as e:
            ERROR_LOG.write_error(ERROR_LOG.get_error_info(e))

        return (success, decrypted)

    @staticmethod
    def is_encrypted_wrapper(queue: Queue, file_path: Path) -> None:
        """Wrapper for is_encrypted"""
        result = None

        try:
            if file_path.exists():
                with open(file_path.resolve(), "rb") as f:
                    result = Decryption.is_encrypted(f)

        except Exception as e:
            ERROR_LOG.write_error(ERROR_LOG.get_error_info(e))
            result = None

        queue.put(result)

    @staticmethod
    def fetch_decrypted_file(queue: Queue, file_path: Path, skip: int = 0) -> None:
        """Fetches file that is not encrypted"""

        result: list[Optional[list[str]] | Optional[dict[str, pd.DataFrame]]] = [
            None,
            None,
        ]

        try:
            data = pd.read_excel(io=file_path.resolve(), sheet_name=None, skiprows=skip)

            if data:
                sheets = list(data.keys())

                for i in sheets:
                    dataRefine(data[i])

                result[0] = sheets
                result[1] = data

        except Exception as e:
            ERROR_LOG.write_error(ERROR_LOG.get_error_info(e))

        queue.put(tuple(result))

    @staticmethod
    def fetch_encrypted_file(
        queue: Queue, file_path: Path, password: str, skip: int = 0
    ) -> None:
        """Fetch content from encrypted file"""

        result: list[Optional[list[str]] | Optional[dict[str, pd.DataFrame]]] = [
            None,
            None,
        ]

        try:
            with io.BytesIO() as decrypted:
                success, file = Decryption.decrypting_file(
                    file_path, decrypted, password
                )

                if success:
                    data = pd.read_excel(
                        io=file, sheet_name=None, skiprows=skip, dtype=str
                    )
                    sheets = list(data.keys())

                    if data:
                        for i in sheets:
                            dataRefine(data[i])

                        result[0] = sheets
                        result[1] = data

        except Exception as e:
            ERROR_LOG.write_error(ERROR_LOG.get_error_info(e))

        queue.put(tuple(result))

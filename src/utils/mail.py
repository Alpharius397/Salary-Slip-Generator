from asyncio import gather, to_thread, run
from copy import deepcopy
from email.mime.multipart import MIMEMultipart
from multiprocessing import Queue
from pathlib import Path
import types
import pandas as pd  #  type: ignore
from src.constants import MAIL_CRED
from src.dataTypes import MonthList
from src.logger import ERROR_LOG
from src.mail import AsyncMailing, Mailing, Message
from src.utils.common import file_clean


class MailingWrapper:
    """Wrapper for Mailing class"""

    month = "jan"
    year = "2024"

    def change_state(self, month: MonthList | str, year: str) -> "MailingWrapper":
        """Set month and year of this class"""
        self.month = month
        self.year = year
        return self

    def attempt_mail_process(
        self, pdf_path: Path, id: str, toAddr: str, queue: Queue
    ) -> None:
        """Updates queue when mailing process is done"""

        ok = (
            Mailing(**MAIL_CRED, error_log=ERROR_LOG)
            .login()
            .addTxtMsg(
                f"Please find attached below the salary slip of {self.month.capitalize()}-{self.year}",
                "plain",
            )
            .addAttach(pdf_path, f"employee_{file_clean(id)}.pdf")
            .addDetails(f"Salary slip of {self.month.capitalize()}-{self.year}")
            .sendMail(toAddr)
            .resetMIME()
            .destroy()
            .status
        )

        queue.put(ok)

    async def _sendMail(
        self, mail: "AsyncMailing", pdf_path: Path, id: str, toAddr: str
    ) -> bool:
        """Wrapper for continuous mail sending"""

        def __make_msg__(mailing: MailingWrapper) -> MIMEMultipart:
            msg = Message(ERROR_LOG)
            msg.addTxtMsg(
                f"Please find attached below the salary slip of {mailing.month.capitalize()}-{mailing.year}",
                "plain",
            )
            msg.addAttach(pdf_path, f"employee_{id}.pdf")
            msg.addDetails(
                f"Salary slip of {mailing.month.capitalize()}-{mailing.year}"
            )
            return msg.get_MIME()

        msg = await to_thread(__make_msg__, self)
        await mail.sendMail(toAddr, msg)
        return mail.status

    @staticmethod
    async def report(tasks: list[types.CoroutineType]) -> int:
        result: list[bool] = await gather(*tasks)

        return len(list(filter(lambda x: x, result)))

    def massMail(
        self,
        data: pd.DataFrame,
        code_column: str,
        email_col: str,
        dir_path: Path,
        queue: Queue,
    ) -> None:
        """Sends email on basis of pdf files present in chosen directory"""

        count, total = 0, 0
        email_server = AsyncMailing(**MAIL_CRED, error_log=ERROR_LOG)
        columns = {j: i for i, j in enumerate(data.columns)}

        async def __dont_know__():
            nonlocal email_server, columns, total, count
            mails = []

            try:
                email_server = await email_server.login()

                for _, row in data.iterrows():
                    try:
                        emp_id = row.values[columns[code_column]]
                        file_name = f"employee_{file_clean(emp_id)}.pdf"

                        pdf_path = dir_path.joinpath(file_name)

                        if not pdf_path.exists():
                            continue

                        total += 1
                        toAddr = row.values[columns[email_col]]
                        mails.append(
                            self._sendMail(
                                email_server,
                                deepcopy(pdf_path),
                                deepcopy(emp_id),
                                deepcopy(toAddr),
                            )
                        )

                    except Exception as e:
                        ERROR_LOG.write_error(ERROR_LOG.get_error_info(e))

                count = await MailingWrapper.report(mails)
                queue.put((count, total))

            except Exception as e:
                ERROR_LOG.write_error(ERROR_LOG.get_error_info(e))

            await email_server.destroy()

        run(__dont_know__())

import os
import smtplib
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email import encoders
from typing import List, Optional, Tuple


class MailService:
    """邮件发送服务，对应 Java MailService.sendSimpleMail。"""

    def __init__(
        self,
        smtp_host: str,
        smtp_username: str,
        smtp_password: str,
        smtp_port: int = 465,
        use_ssl: bool = True,
    ):
        if not smtp_host:
            raise ValueError("smtp_host 未配置，无法初始化 MailService")
        self._host = smtp_host
        self._port = smtp_port
        self._username = smtp_username
        self._password = smtp_password
        self._from = smtp_username
        self._use_ssl = use_ssl

    @classmethod
    def from_env(cls) -> "MailService":
        """从环境变量加载配置：SMTP_HOST, SMTP_USERNAME, SMTP_PASSWORD, SMTP_PORT, SMTP_USE_SSL"""
        return cls(
            smtp_host=os.getenv("SMTP_HOST", ""),
            smtp_username=os.getenv("SMTP_USERNAME", ""),
            smtp_password=os.getenv("SMTP_PASSWORD", ""),
            smtp_port=int(os.getenv("SMTP_PORT", "465")),
            use_ssl=os.getenv("SMTP_USE_SSL", "true").lower() in ("1", "true", "yes"),
        )

    def _send_raw(self, to: str, message: MIMEMultipart) -> None:
        """底层发送逻辑。"""
        if self._use_ssl:
            with smtplib.SMTP_SSL(self._host, self._port) as server:
                server.login(self._username, self._password)
                server.sendmail(self._from, [to], message.as_string())
        else:
            with smtplib.SMTP(self._host, self._port) as server:
                server.starttls()
                server.login(self._username, self._password)
                server.sendmail(self._from, [to], message.as_string())

    def send_simple_mail(self, to: str, subject: str, content: str) -> None:
        """发送纯文本邮件，对应 Java sendSimpleMail。"""
        message = MIMEMultipart()
        message["From"] = self._from
        message["To"] = to
        message["Subject"] = subject
        message.attach(MIMEText(content, "plain", "utf-8"))
        self._send_raw(to, message)

    def send_mail_with_attachments(
        self,
        to: str,
        subject: str,
        content: str,
        attachments: Optional[List[Tuple[str, bytes, str]]] = None,
    ) -> None:
        """
        发送带附件的邮件。

        :param to: 收件人
        :param subject: 主题
        :param content: 邮件正文（纯文本）
        :param attachments: 附件列表，每项为 (文件名, 文件字节数据, MIME类型)，
                            例如 [("report.json", b'...', "application/json")]
        """
        message = MIMEMultipart()
        message["From"] = self._from
        message["To"] = to
        message["Subject"] = subject
        message.attach(MIMEText(content, "plain", "utf-8"))

        if attachments:
            for filename, data, mime_type in attachments:
                part = MIMEBase(*mime_type.split("/", 1))
                part.set_payload(data)
                encoders.encode_base64(part)
                part.add_header(
                    "Content-Disposition",
                    f'attachment; filename="{filename}"',
                )
                message.attach(part)

        self._send_raw(to, message)

from typing import Literal, List, Optional

from pydantic import BaseSettings
import os


class HwkEnviron(BaseSettings):
    hwk_smtp_email_backend: Literal['django.core.mail.backends.smtp.EmailBackend']
    hwk_smtp_email_host: str
    hwk_smtp_email_use_tls: bool
    hwk_smtp_email_port: int
    hwk_smtp_email_use_ssl: bool
    hwk_smtp_email_host_user: str
    hwk_smtp_email_host_password: str

    hwk_celery_broker_url: str

    hwk_sec_django_debug: bool
    hwk_sec_csrf_trusted: List[str]
    hwk_sec_cors_origins: List[str]
    hwk_sec_allowed_hosts: List[str]
    hwk_django_secret_key: str

    hwk_webpush_vapid_public: str
    hwk_webpush_vapid_private: str
    hwk_sec_is_prod: bool

    hwk_db_engine: str
    hwk_db_name: str
    hwk_db_postgres_password: Optional[str]
    hwk_db_postgres_user: Optional[str]
    hwk_db_postgres_host: Optional[str]
    hwk_db_postgres_port: Optional[int]

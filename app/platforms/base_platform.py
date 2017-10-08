import email
import pickle
from abc import abstractmethod
from imaplib import IMAP4_SSL

from pandas import DataFrame
from rq import get_current_job

from appcore.services import Bootstrap, Factory


# noinspection PyUnresolvedReferences
class BasePlatform(object):
    @abstractmethod
    def API_URL(self):
        """
        Base URL for platform
        """

    def __init__(self):
        super().__init__()

    # noinspection PyAttributeOutsideInit
    def run(self):
        """
        Entry point for processing
        """
        app = Bootstrap()
        self.__dict__.update(app.__dict__)
        self._job = get_current_job()
        self._run()

    @abstractmethod
    def _run(self):
        """
        Entry point to be realized in the platform class
        """

    def update(self, procedure: str, message: str):
        self.logger.debug(':'.join([procedure, message]))
        if self._job:
            self._job.meta[procedure] = message
            self._job.save_meta()

    def get_conversion_map(self, map_type: str, fallback=''):
        conversion_map = pickle.loads(Factory().get_storage_client('redis').get('maps', map_type))
        return lambda value: conversion_map.get(value.lower(), fallback)

    def _regex(self, column, pattern: str, fallback: str = ''):
        """
        :type column: pandas.Series
        :rtype: pandas.Series
        """
        return column.str.replace(pattern, lambda value: value.group(1) if value else fallback)

    def _store_mysql(self, data: DataFrame, storage_settings: dict):
        from platforms.helpers.mysql_connection import MysqlConnection
        with MysqlConnection(**storage_settings) as connection:
            connection.store(data, self.update)

        return True

    def _send_mail(self, data: DataFrame, storage_settings: dict):
        raise NotImplementedError

    # TODO: Move mailbox methods to a closing object like MysqlConnection
    def _get_mailbox(self) -> IMAP4_SSL:
        self.update('login', 'accessing')
        mailbox = IMAP4_SSL(host=self.MAIL_CONFIG['host'])

        self.update('login', 'authenticating')
        mailbox.login(self.MAIL_CONFIG['user'], self.MAIL_CONFIG['password'])
        mailbox.select('inbox')

        self.update('login', 'completed')
        return mailbox

    def _search_mailbox(self, mailbox: IMAP4_SSL, subject: str = None) -> list:
        date = self.date.strftime('%d-%b-%Y')
        sender = self.MAIL_CONFIG['sender']
        if not subject:
            subject = self.MAIL_CONFIG['subject']

        self.update('mailbox', 'searching')
        response = mailbox.uid('SEARCH', None, f'(SENTON {date} HEADER FROM "{sender}" SUBJECT "{subject}")')
        return [int(uid) for uid in response[1][0].decode().split(' ')]

    def _get_message(self, mailbox: IMAP4_SSL, uid: int) -> email.message.Message:
        self.update('mailbox', 'retrieving mail')
        return email.message_from_bytes(mailbox.uid('FETCH', str(uid), '(RFC822)')[1][0][1])

    def _find_attachment(self, attachment_name: str, mailbox: IMAP4_SSL, search_group: list):
        """
        I know, i'm sorry. At least it's fast
        """
        extractor = lambda uid: mailbox.uid(
            'FETCH', str(uid), '(BODYSTRUCTURE)'
        )[1][0].decode().split('"NAME" "')[1].split('"')[0]

        return [uid for uid in search_group if extractor(uid).lower() == attachment_name.lower()]

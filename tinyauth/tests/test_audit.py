import datetime
import importlib
import json
import logging

from tinyauth.audit import logger, setup_audit_log

from .base import TestCase


class TestAudit(TestCase):

    def setUp(self):
        super().setUp()

        # FIXME: Refactor class hierarchy so this isn't needed
        self.stack.close()

        self.app.config['AUDIT_LOG_FILENAME'] = '/tmp/tinyauth/audit.log'

        self.addCleanup(importlib.reload, logging)
        self.addCleanup(logging.shutdown)

        self.rfh = self.patch('logging.handlers.RotatingFileHandler')
        self.rfh.return_value.level = logging.INFO

        setup_audit_log(self.app)

        # Grab the AuditFormatter that setup_audit_log made
        self.fmt = self.rfh.return_value.setFormatter.call_args_list[0][0][0]

        # Grab the handle() method of the RotatingFileHandler
        self.handle = self.rfh.return_value.handle

        # Patch logging module so we get a consistent and comparible event logged
        self.patch('logging.os.getpid').return_value = 8888
        self.patch('logging.threading.get_ident').return_value = 9999
        self.patch('logging.threading.current_thread').return_value.name = 'MainThread-test'
        self.patch('logging.time.time').return_value = 1
        logging._startTime = 0

    def event(self, event_tag, extra=None):
        logger.info(event_tag, extra=extra or {})

        log_record = self.handle.call_args_list[0][0][0]
        json_string = self.fmt.format(log_record)
        assert json_string.endswith('}')
        return json.loads(json_string)

    def test_simple_event(self):
        assert self.event('event-tag') == {
            'event': 'event-tag',
            'created': '1970-01-01T00:00:01',
            'levelname': 'INFO',
            'process': 8888,
            'relativeCreated': 1000,
            'thread': 9999,
            'threadName': 'MainThread-test',
        }

    def test_event_with_extra(self):
        extra = {
            'timestamp': datetime.datetime.utcfromtimestamp(2),
            'string': 'a string',
            'number': 1,
            'bool': True,
        }

        assert self.event('event-tag', extra) == {
            'event': 'event-tag',
            'created': '1970-01-01T00:00:01',
            'levelname': 'INFO',
            'process': 8888,
            'relativeCreated': 1000,
            'thread': 9999,
            'threadName': 'MainThread-test',
            'timestamp': '1970-01-01T00:00:02',
            'string': 'a string',
            'number': 1,
            'bool': True,
        }

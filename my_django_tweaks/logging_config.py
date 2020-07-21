from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

import logging
import logging.config
import logging.handlers
import os
import sys

__author__ = 'ricard'
_watchdog_configured = False


def configure_logging(log_name, LOG_CONFIG_PATH, LOG_PATH, DEFAULT_LOG_FORMAT, RUNNING_UNITTEST):
    if not os.path.exists(LOG_PATH):
        os.makedirs(LOG_PATH)

    if RUNNING_UNITTEST and not logging.Logger.manager.loggerDict:
        # HACK to avoid logs due to DEBUG level forced by pyreadline's logger module
        try:
            import pyreadline  # noqa: F401
        #    except ImportError, ex:
        except Exception as ex:     # noqa: F841
            # print >> sys.stderr, "IMPORT ERROR with pyreadline:", ex.message
            pass
        # logger = logging.getLogger()
        logging.basicConfig(level=logging.CRITICAL, format=DEFAULT_LOG_FORMAT)
        # logging.basicConfig(level=logging.DEBUG, format=DEFAULT_LOG_FORMAT)
        # logger.setLevel(logging.CRITICAL)
        # logger.setLevel(logging.DEBUG)
        return

    if not RUNNING_UNITTEST:
        handler = LoggingConfigEventHandler(log_name, LOG_CONFIG_PATH, LOG_PATH, DEFAULT_LOG_FORMAT)
        handler.do_reconfigure_logging()

        if os.path.exists(LOG_CONFIG_PATH):
            observer = Observer()
            # observer.schedule(LoggingEventHandler(), LOG_CONFIG_PATH, recursive=False)
            observer.schedule(handler, LOG_CONFIG_PATH, recursive=False)
            print("log watcher to '%s'" % LOG_CONFIG_PATH, file=sys.stderr)
            observer.daemon = True  # should not block the program ending
            observer.start()


class LoggingConfigEventHandler(FileSystemEventHandler):
    """Check for logging config changes."""
    def __init__(self, log_name, LOG_CONFIG_PATH, LOG_PATH, DEFAULT_LOG_FORMAT):
        self.log_name = log_name
        self.config_path = LOG_CONFIG_PATH
        self.log_path = LOG_PATH
        self.default_log_format = DEFAULT_LOG_FORMAT
        self.base_filename = 'logging-%s' % self.log_name

    def on_any_event(self, event):
        print("Event %s" % repr(event), file=sys.stderr)
        logging.debug("Event %s", event)
        if not event.is_directory:
            filename = os.path.basename(event.src_path)
            if filename.startswith(self.base_filename):
                logging.info("Logging config change detected. Reloading configuration...")
                self.do_reconfigure_logging()

    def do_reconfigure_logging(self):
        log_ok = False
        logconfig_fullpath = os.path.join(self.config_path, 'logging-%s.py' % self.log_name)
        if not os.path.exists(logconfig_fullpath):
            logconfig_fullpath = os.path.splitext(logconfig_fullpath)[0] + '.ini'
        if not os.path.exists(logconfig_fullpath):
            logconfig_fullpath = os.path.splitext(logconfig_fullpath)[0] + '.default.py'
        if os.path.exists(logconfig_fullpath):
            logging.info("Loading log config from %s", logconfig_fullpath)
            try:
                if logconfig_fullpath.endswith(".py"):
                    from importlib.machinery import SourceFileLoader
                    log_config = SourceFileLoader("log_config", logconfig_fullpath).load_module()
                    # import imp
                    # log_config = imp.load_source('log_config', logconfig_fullpath)
                    logging.config.dictConfig(log_config.LOGGING)
                else:
                    logging.config.fileConfig(logconfig_fullpath)

                log_ok = True
            except Exception:
                import traceback

                traceback.print_exc()

        if not log_ok:
            print("Loading log config not found or badly formated, loading default config.", file=sys.stderr)

            log_level = logging.INFO
            formatter = logging.Formatter(self.default_log_format)
            logging.basicConfig(level=log_level, format=self.default_log_format)
            logFile = logging.handlers.RotatingFileHandler(os.path.join(self.log_path, os.path.basename(self.log_name) + '.log'),
                                                           maxBytes=1 * 1024 * 1024, backupCount=10)
            logFile.setLevel(log_level)
            logFile.setFormatter(formatter)
            logging.getLogger().addHandler(logFile)
            logging.getLogger().propagate = False

#!/usr/bin/env python
#

import argparse
import logging
import signal
import sys

import daemon

import config
from server import Server


config.init('config.json')
logger = logging.getLogger('root')

server = Server()

def parse_args():
   parser = argparse.ArgumentParser(
      description=config.program_description
   )
   parser.add_argument('-d', '--daemonize',
      action='store_true',
      help='To daemonize or not to daemonize'
   )
   parser.add_argument('-v', '--verbose',
      action='store_true',
      help='Enable verbose ouptut at the daemon/core')

   args = parser.parse_args()
   return args

def setup_logger():
   if args.verbose:
      log_level = logging.DEBUG
   else:
      log_level = logging.INFO

   logger.setLevel(log_level)
   formatter = logging.Formatter(
      fmt='%(levelname)s [%(asctime)s] %(name)s.%(module)s.%(funcName)s(): %(message)s')

   # If not daemonizing, log to stdout; if daemonizing, log to file
   if args.daemonize:
      fh = logging.FileHandler(config.logfile)
      fh.setFormatter(formatter)
      logger.addHandler(fh)
   else:
      sh = logging.StreamHandler()
      sh.setFormatter(formatter)
      logger.addHandler(sh)

   # Assume config has a "log_levels" section containing module / log levels
   # NOTSET = 0; DEBUG = 10; INFO = 20; WARN = 30; ERROR = 40; CRITICAL = 50
   for module, logger_level in config.log_levels.items():
      logging.getLogger(module).setLevel(logger_level)

   # List all modules and their log levels
   loggers = [str(logging.getLogger(name))
      for name in logging.root.manager.loggerDict]
   logger.debug('list of available loggers:\n * ' + '\n * '.join(loggers))

def terminate(signum, frame):
   '''called on exit; can be used to cleanup the server'''
   server.close()
   sys.exit(0)

def main():
   logger.info('starting')

   context = daemon.DaemonContext(
      working_directory=config.working_directory,
      stdout=sys.stdout,
      stderr=sys.stderr
   )
   context.signal_map = {
      signal.SIGTERM: terminate,
      signal.SIGHUP: terminate
   }

   server.init()

   if args.daemonize:
      logger.info('daemonizing')
      context.stdout=None
      context.stderr=None
      with context:
         server.main()
   else:
      signal.signal(signal.SIGTERM, terminate)
      signal.signal(signal.SIGINT, terminate)
      server.main()

if __name__ == '__main__':
   args = parse_args()
   setup_logger()
   main()

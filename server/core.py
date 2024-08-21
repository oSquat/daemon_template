'''An example server that runs forever until terminated'''

import logging
import time

import config

from . import logger


class Server:
   def __init__(self):
      pass

   def init(self):
      # borrow this application init method from Flask extensions
      logger.info('module setup')

   def close(self):
      logger.info('terminating')

   def main(self):
      while True:
         time.sleep(1)
         logger.info('executing')
         logger.debug('DEBUG')

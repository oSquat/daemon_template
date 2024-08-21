import logging

# share a logger among any code in this package
# logging looks better, outputting server.core.main()
logger = logging.getLogger('server')

from .core import Server

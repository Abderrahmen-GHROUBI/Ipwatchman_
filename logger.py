import logging
from config import config

config = config()

log_file = config['logger']['log_file']
log_level = getattr(logging, config['logger']['level'])

logging.basicConfig(filename=log_file, level=log_level,
                    format='%(asctime)s - %(levelname)s - %(message)s')


logger = logging.getLogger()
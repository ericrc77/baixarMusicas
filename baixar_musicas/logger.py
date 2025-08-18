import logging
from .config import LOG_FILE

LOG_FORMAT = '%(asctime)s [%(levelname)s] %(name)s: %(message)s'

def setup_logging():
	logging.basicConfig(
		level=logging.INFO,
		format=LOG_FORMAT,
		handlers=[
			logging.FileHandler(LOG_FILE, encoding='utf-8'),
			logging.StreamHandler()
		]
	)

def get_logger(name: str) -> logging.Logger:
	return logging.getLogger(name)

setup_logging()

class LoggerWidget:
	def __init__(self, log_area=None):
		self.log_area = log_area

	def set_log_area(self, log_area):
		self.log_area = log_area

	def log(self, msg):
		if self.log_area:
			self.log_area.append(msg)
		print(msg)


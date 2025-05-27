import logging

logger = logging.getLogger("llm-gamebook")
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter("%(name)s %(levelname)s: %(message)s"))
logger.addHandler(handler)

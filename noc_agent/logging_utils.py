import logging, uuid

def logger():
    log = logging.getLogger("noc")
    if not log.handlers:
        log.setLevel(logging.INFO)
        h = logging.StreamHandler()
        h.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
        log.addHandler(h)
    return log

def cid():
    return uuid.uuid4().hex[:8]

import logging

bot_token = 'YOUR_BOT_TOKEN'
database = 'check_build_users.db'

logger = logging.getLogger('check_build')
logging.getLogger("requests").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter(u'[%(asctime)s] - %(filename)s[LINE:%(lineno)d]# %(levelname)-8s %(message)s')
sh = logging.StreamHandler()
sh.setLevel(logging.DEBUG)
sh.setFormatter(formatter)
log = open('./logs/check_build.log', "a", encoding="utf-8")
ch = logging.StreamHandler(log)
ch.setLevel(logging.DEBUG)
ch.setFormatter(formatter)
logger.addHandler(ch)
logger.addHandler(sh)

# coding=utf-8

class MyLogger(object):
    log = None
    _instance = None
    '''
    def info(self, msg, *args, **kwargs):
        self.log.info(msg, *args, **kwargs)

    def debug(self, msg, *args, **kwargs):
        self.log.debug(msg, *args, **kwargs)

    def error(self, msg, *args, **kwargs):
        self.log.error(msg, *args, **kwargs)
    '''

    @classmethod
    def _init_logger(cls):
        import logging
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.DEBUG)
        # 再创建一个handler，用于输出到控制台
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)
        # 定义handler的输出格式
        formatter = logging.Formatter(
            '[%(asctime)s] %(funcName)s [%(levelname)s] %(message)s'
        )
        ch.setFormatter(formatter)
        # 给logger添加handle
        logger.addHandler(ch)
        cls.log = logger

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(MyLogger, cls).__new__(cls)
            cls._init_logger()
        return cls._instance


logger = MyLogger()

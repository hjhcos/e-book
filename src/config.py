# -*- coding: utf-8 -*-
import sys
import os
import logging
from configparser import ConfigParser
# sys.path.append(os.path.split(__file__)[0])


class Log(object):
    """record run log

    if __name__ == '__main__':
        conf = Log()
        logger = conf.getLog()
        logger.info('error!')
    level: debug info warning error critical
    """
    def __init__(self):

        self.logger = logging.getLogger('config')
        self.logger.setLevel(logging.DEBUG)

        fh = logging.FileHandler('LOG.log', encoding='utf-8')
        fh.setLevel(logging.DEBUG)

        sh = logging.StreamHandler()
        sh.setLevel(logging.DEBUG)

        formatter = logging.Formatter('%(asctime)s - %(name)s - %(filename)s - %(levelname)s - %(message)s')
        fh.setFormatter(formatter)
        sh.setFormatter(formatter)

        self.logger.addHandler(fh)
        self.logger.addHandler(sh)

    def getLog(self):
        return self.logger


class Config(object):
    """config file process

    cf = Config("../config.cfg")
    section = "admin"
    option = "save"
    value = True
    cf.add(section, option, value)
    cf.get()
    cf.get(section)
    cf.get(section, option)
    cf.updata(section, option, value)
    cf.remove(section, option)
    cf.save()
    """

    def __init__(self, filename="config.ini"):
        """
        :param filename: config file
        """
        self.filename = filename
        self.config = ConfigParser()
        self.config.read(self.filename, encoding="utf-8")

    def detection(self, section, option, value):
        section = section.lower() if section else None
        option = option.lower() if option else None
        try:
            return self.config.getboolean(section, option)
        except:
            return value

    def get(self, section=None, option=None):
        """to get all value in the config

        :param section: config's section
        :param option: section's option
        :return: section or option value
        """
        section = section.lower() if section else None
        option = option.lower() if option else None
        if not section:
            return self.config.sections()
        elif not option:
            return [option[0] for option in self.config.items(section)]
        else:
            try:
                value = eval(self.config.get(section, option))
            except:
                return self.detection(section, option, self.config.get(section, option))
            return value

    def updata(self, section, option=None, value=None):
        """ revise option's value to the section

        :param section: config's section
        :param option: section's option
        :param value: option's value
        :return: section option value --> dict()
        """
        section = section.lower() if section else None
        option = option.lower() if option else None
        if not option:
            raise ValueError("option is None.")
        if not str(value):
            raise ValueError("option's value is None.")
        self.config.set(section, option, str(value))
        return eval("{section: {option: value}}")

    def add(self, section, option=None, value=None):
        """ add option to the section

        :param section: config's section
        :param option: section's option
        :param value: option's value
        :return: section option value --> dict()
        """
        section = section.lower() if section else None
        option = option.lower() if option else None
        if not section in self.config.sections():
            self.config.add_section(section)
            # raise ValueError("config have not the section: {} ".format(section))
        elif option:
            return self.updata(section, option, value)
        return self.updata(section, option, value)

    def remove(self, section, option=None):
        """ remove section's option in the config.

        :param section: config's section
        :param option: section's option
        :return: remove option
        """
        section = section.lower() if section else None
        option = option.lower() if option else None
        if not section in self.config.sections():
            raise ValueError("config have not the section: {} ".format(section))

        if option:
            return self.config.remove_option(section, option)
        else:
            raise ValueError("{} have not {}.".format(section, option))

    def save(self, path="config.cfg"):
        """ save temp data to the file

        :param path: file path
        :return: filename
        """
        with open(path, "w", encoding="utf-8") as file:
            self.config.write(file)
        return os.path.split(path)[1]


if __name__ == '__main__':

    log = Log()
    # logger = log.getLog()
    # logger.info("info.")

    cf = Config("config.ini")
    # section = "admin"
    # option = "save"
    # value = True
    # print(cf.add(section, option, value))
    # print(cf.get())
    # print(cf.get(section))
    # print(cf.get(section, option))
    # print(cf.updata(section, option, value))
    # # print(cf.remove(section, option))
    # print(cf.save())
    pass

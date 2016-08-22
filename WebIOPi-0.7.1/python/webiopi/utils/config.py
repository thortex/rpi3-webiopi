from webiopi.utils.version import PYTHON_MAJOR

if PYTHON_MAJOR >= 3:
    import configparser as parser
else:
    import ConfigParser as parser

class Config():
    
    def __init__(self, configfile=None):
        config = parser.ConfigParser()
        config.optionxform = str
        if configfile != None:
            config.read(configfile)
        self.config = config

    def get(self, section, key, default):
        if self.config.has_option(section, key):
            return self.config.get(section, key)
        return default

    def getboolean(self, section, key, default):
        if self.config.has_option(section, key):
            return self.config.getboolean(section, key)
        return default
    
    def getint(self, section, key, default):
        if self.config.has_option(section, key):
            return self.config.getint(section, key)
        return default
    
    def items(self, section):
        if self.config.has_section(section):
            return self.config.items(section)
        return {}

class ConfigException(Exception):

    def __init__(self):
        msg = "Please specify your valid config."
        super(ConfigException, self).__init__(msg)


class MysteriousException(Exception):

    def __init__(self):
        msg = "Mysterious !!!"
        super(ConfigException, self).__init__(msg)

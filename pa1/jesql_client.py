"""This module handles all of the user interaction functionality
"""
import configparser

class Interface(object):
    """Class docstring"""
    def __init__(self, config_file=None):
        if not config_file:
            config_file = 'settings.conf'

        self.read_config_file(config_file)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        pass

    def accept_user_input(self):
        """Begins accepting user input until the ExitCommand is
        encountered"""
        while True:
            try:
                read_input = input()
            except EOFError:
                return self.__exit__ # This might need arguments xd

            if not read_input.startswith(self.default_config['CommentPrefix']):
                print('You said: ' + read_input.strip())
            if read_input.strip() == self.default_config['ExitCommand']:
                break

    def read_config_file(self, filename):
        """Reads in a specified config file. Currently it will only
        read in settings under the DEFAULT heading. Should prolly
        fix"""
        config = configparser.ConfigParser()
        config.read(filename)
        self.default_config = config['DEFAULT']

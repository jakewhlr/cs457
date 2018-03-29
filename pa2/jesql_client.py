"""This module handles all of the user interaction functionality
"""
import configparser
import sys
import tokenizer
import jesql_parser

class Interface(object):
    """Class docstring"""
    def __init__(self, args, config_file=None):
        self.args = args
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
                if self.args.silent:
                    read_input = input()
                else:
                    read_input = input('jesql> ')
            except EOFError:
                return self.__exit__ # This might need arguments xd

            if self.parse_input(read_input.strip()) == 255:
                return self.__exit__

    def read_config_file(self, filename):
        """Reads in a specified config file."""
        config = configparser.ConfigParser()
        config.read(filename)
        self.default_config = config['DEFAULT']
        self.commands_config = config['COMMANDS']
        self.create_options = config['CREATE_OPTS']

    def parse_input(self, read_input):
        if not read_input:
            return 0
        elif read_input.startswith(self.default_config['CommentPrefix']):
            return 0
        elif read_input == self.commands_config['ExitCommand']:
            return 255

        if read_input.endswith(self.default_config['CommandSuffix']):
            read_input = read_input[:-1]
        else:
            print('ERROR: command was not ended with' +
                  self.default_config['CommandSuffix'], file=sys.stderr) # stderr
            return 1

        tokens = tokenizer.tokenize(read_input)
        jesql_parser.parse(tokens)

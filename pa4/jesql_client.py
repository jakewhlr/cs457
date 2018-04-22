"""This module handles all of the user interaction functionality
"""
import configparser
import sys
import tokenizer
import jesql_parser
import re

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
        read_input = ''
        while read_input.strip().lower() != self.commands_config['ExitCommand'].lower():
            if not self.args.silent:
                print('jesql> ', end='')
                sys.stdout.flush()

            read_input += ' ' + sys.stdin.readline()

            if read_input.strip().startswith(self.default_config['CommentPrefix']):
                read_input = ''
            elif read_input.strip().endswith(';'):
                read_input = ''.join(read_input.splitlines()).strip()
                tokens = tokenizer.tokenize(read_input[:-1])
                tokens = tokenizer.encapsulate_values(tokens)
                jesql_parser.parse(tokens)
                read_input = ''
            elif not read_input.strip(' '):
                return self.__exit__
            elif read_input == ' \n': # just pressing enter returns <space><newline>
                read_input = ''


    def read_config_file(self, filename):
        """Reads in a specified config file."""
        config = configparser.ConfigParser()
        config.read(filename)
        self.default_config = config['DEFAULT']
        self.commands_config = config['COMMANDS']
        self.create_options = config['CREATE_OPTS']

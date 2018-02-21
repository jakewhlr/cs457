"""This module handles all of the user interaction functionality
"""
import configparser
import os
import sys

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

            split_input = read_input.split(" ")

            if split_input[0].startswith(self.default_config['CommentPrefix']):
                print('Comment: ' + read_input)

            if read_input.strip() == self.default_config['ExitCommand']:
                break

            if split_input[0].strip() == self.default_config['CreateCommand']:
                if not split_input[1] in self.create_commands: # if command doesn't exist
                    print("INVALID OPTION: " + split_input[1], file=sys.stderr) # stderr

                if len(split_input) < 3: # if no 3rd option
                    print("\"CREATE " + self.create_commands['database'] + "\" Requires a name.", file=sys.stderr) # stderr

                elif split_input[1] == self.create_commands['database']: # if option is database
                    self.create_db(split_input[2])


    def read_config_file(self, filename):
        """Reads in a specified config file. Currently it will only
        read in settings under the DEFAULT heading. Should prolly
        fix"""
        config = configparser.ConfigParser()
        config.read(filename)
        self.default_config = config['DEFAULT']
        self.create_commands = config['CREATE']

    def create_db(self, name):
        """Creates database as directory"""
        current_dir = os.getcwd()
        database_dir = os.path.join(current_dir, "databases")

        if not os.path.exists(database_dir): # if databases dir doesn't exist
            os.makedirs(database_dir) # create it

        if os.path.exists(database_dir + "/" + name):
            print("Database \"" + name + "\" exists.", file=sys.stderr) # stderr?
        else:
            os.makedirs(database_dir + "/" + name)

    def create_table(self, name):
        """Creates table as file"""

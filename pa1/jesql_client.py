"""This module handles all of the user interaction functionality
"""
import configparser
import os
import sys
import shutil

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

            if read_input.strip() == self.commands_config['ExitCommand']:
                break

            if not split_input[0] in self.commands_config:
                print("ERROR: " + split_input[0] + ": Command not found.", file=sys.stderr)

            # CREATE
            if split_input[0].strip() == self.commands_config['CreateCommand']:
                if len(split_input) < 2:
                    print("ERROR: " + split_input[0] + ": No option specified.", file=sys.stderr) # stderr

                elif not split_input[1] in self.create_options: # if command doesn't exist
                    print("ERROR: " + split_input[0] + ": Invalid type: " + split_input[1], file=sys.stderr) # stderr

                # Create database
                elif split_input[1] == self.create_options['database']: # if option is database
                    if len(split_input) < 3: # if no 3rd option
                        print("ERROR: CREATE " + self.create_options['database'] + ": Option requires a name.", file=sys.stderr) # stderr
                    else:
                        self.create_db(split_input[2])

                # create table
                if split_input[0].strip() == self.commands_config['CreateCommand']:
                    if  split_input[1] == self.create_options['table']:
                #        self.create_table(split_input[2])
                        print ("split_input[2]: ", split_input[2])
                        print ("split_input[3]: ", split_input[3])
                        print ("split_input[4]: ", split_input[4])
                        print ("split_input[5]: ", split_input[5])
                        print ("split_input[6]: ", split_input[6])


            # DROP
            if split_input[0].strip() == self.commands_config['DeleteCommand']:
                # delete database
                if split_input[1] == self.create_options['database']:
                    self.delete_db(split_input[2])

                # delete table
                elif  split_input[1] == self.create_options['table']:
                    self.delete_table(split_input[2])

            # USE
            if split_input[0].strip() == self.commands_config['UseCommand']:
                self.use_db(split_input[1])


    def read_config_file(self, filename):python ignore parentheses
        """Reads in a specified config file. Currently it will only
        read in settings under the DEFAULT heading. Should prolly
        fix"""
        config = configparser.ConfigParser()
        config.read(filename)
        self.default_config = config['DEFAULT']
        self.commands_config = config['COMMANDS']
        self.create_options = config['CREATE_OPTS']


    def create_db(self, name):
        """Creates database as directory"""
        current_dir = os.getcwd()
        database_dir = os.path.join(current_dir, "databases")

        if not os.path.exists(database_dir): # if databases dir doesn't exist
            os.makedirs(database_dir) # create it

        if os.path.exists(database_dir + "/" + name):
            print("ERROR: Database \"" + name + "\" exists.", file=sys.stderr) # stderr?
        else:
            os.makedirs(database_dir + "/" + name)

    def create_table(self, name):
        """Creates table as file"""


    def delete_db(self, name):
        """Delete database as directory"""
        current_dir = os.getcwd()
        database_dir = os.path.join(current_dir, "databases")

        # check if databse exist
        if os.path.exists(database_dir + "/" + name):
            # delete the entire dir & files inside
            shutil.rmtree(database_dir + "/" + name)
        else:
            print ("!Failed to delete",name,"because it does not exist.")

    # delete table
    def delete_table(self, name):
        """Delete database as directory"""
        current_dir = os.getcwd()
        database_dir = os.path.join(current_dir, "databases")

        # check if table exist
        if os.path.exists(database_dir + "/" + name):
            # remove file only
            os.remove(database_dir + "/" + name)
        else:
            print ("!Failed to delete",name,"because it does not exist.")

    # USE FOR db
    def use_db(self, name):
        """use named database"""
        current_dir = os.getcwd()
        database_dir = os.path.join(current_dir, "databases")

        # check if databse exist
        if os.path.isdir(database_dir + "/" + name):
            os.chdir(database_dir + "/" + name)
        else:
            print ("!Failed to delete",name,"because it does not exist.")


    # SELECT for table

    # ALTER for update

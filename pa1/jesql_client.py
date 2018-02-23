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
                read_input = input('jesql> ')
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

            # SELECT
            if split_input[0].strip() == self.commands_config['SelectCommand']:
                if len(split_input) < 4:
                    print("Expected 4 arguments.", file=sys.stderr) # stderr
                    break

                if split_input[2] == 'FROM':
                    self.select(split_input[1].strip(), split_input[3].strip())

            # ALTER
            if split_input[0].strip() == self.commands_config['AlterCommand']:
                if  split_input[1] == self.create_options['table']:
                    self.alter(split_input[2],split_input[4],split_input[5])


    def read_config_file(self, filename):
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
        database_dir = os.path.join(sys.path[0], "databases")

        if not os.path.exists(database_dir): # if databases dir doesn't exist
            os.makedirs(database_dir) # create it

        if os.path.exists(database_dir + "/" + name):
            print("!Failed to create database", name, "because it already exists.")
        else:
            os.makedirs(database_dir + "/" + name)
            print("Database", name, "created.")

    def create_table(self, name):
        """Creates table as file"""


    def delete_db(self, name):
        """Delete database as directory"""
        database_dir = os.path.join(sys.path[0], "databases")

        # check if databse exist
        if os.path.exists(database_dir + "/" + name):
            # delete the entire dir & files inside
            shutil.rmtree(database_dir + "/" + name)
        else:
            print ("!Failed to delete", name, "because it does not exist.")

    def delete_table(self, name):
        """Delete database as directory"""
        database_dir = os.path.join(sys.path[0], "databases")

        # check if table exist
        if os.path.exists(database_dir + "/" + name):
            # remove file only
            os.remove(database_dir + "/" + name)
        else:
            print ("!Failed to delete", name, "because it does not exist.")


    # USE FOR db
    def use_db(self, name):
        """use named database"""
        database_dir = os.path.join(sys.path[0], "databases")

        # check if databse exist
        if os.path.isdir(database_dir + "/" + name):
            os.chdir(database_dir + "/" + name)
            print("Using Database", name + ".")
        else:
            print ("!Failed to use", name, "because it does not exist.")

    # SELECT for table
    def select(self, cols ,table):
        """Selects columns from given table, prints output"""
        table_path = os.path.join(os.getcwd(), table)
        col_indexes = []
        if not os.path.exists(table_path):
            print ("!Failed to query table", table, "because it does not exist.")
            return

        with open(table_path) as input_file:
            lines = input_file.readlines()

        for index, line in enumerate(lines):
            lines[index] = line.split('|')
            for col_index, col in enumerate(lines[index]):
                lines[index][col_index] = col.strip()

        for header_index, header in enumerate(lines[0]):
            lines[0][header_index] = header.split(' ')
            if lines[0][header_index][0] == cols: # if col matches, note index
                col_indexes.append(header_index)

        if cols is '*': # '*' selects all columns
            col_indexes = range(0, len(lines[0]))

        for row_index, row in enumerate(lines):
            for col in col_indexes:
                print(*row[col], sep=" ", end='')
                if col is not col_indexes[len(col_indexes)-1]:
                    print(" | ", end='')
            print('')

    # ALTER for update
    def alter(self, tbName, indexName, input_type):
        table_path = os.path.join(os.getcwd(), tbName)

        if not os.path.exists(table_path):
            print ("!Failed to query table", tbName, "because it does not exist.")
            return

        org_file = open(table_path, 'r')

        # read file into list formatt
        read_file = org_file.read().splitlines()

        converted_to_string = ''.join(read_file)

        with open(table_path, "w") as alterFile:
            alterFile.write(converted_to_string + ' ' + '|' + ' ' + indexName + ' ' + input_type )

        print("Table" + tbName+" modified.")

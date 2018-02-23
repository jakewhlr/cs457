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

            if self.parse_input(read_input.strip()) == 255:
                return self.__exit__

    def read_config_file(self, filename):
        """Reads in a specified config file. Currently it will only
        read in settings under the DEFAULT heading. Should prolly
        fix"""
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
            print("All done.")
            return 255

        if read_input.endswith(self.default_config['CommandSuffix']):
            read_input = read_input[:-1]
        else:
            print('ERROR: command was not ended with' +
                  self.default_config['CommandSuffix'], file=sys.stderr) # stderr
            return 1

        split_input = read_input.split(' ');

        for (key, value) in self.commands_config.items():
            if split_input[0].lower() == value.lower():
                try:
                    return getattr(self, value.lower())(split_input[1:])
                except AttributeError:
                    print('ERROR: ' + split_input[0] + ' was included but not defined',
                          file=sys.stderr)
                    raise

        print('ERROR: ' + split_input[0] + ': Command not found.', file=sys.stderr)

    def create(self, args):
        if len(args) < 2:
            print('ERROR: CREATE: invalid number of options specified.', file=sys.stderr) # stderr
            return 1
        elif not args[0] in self.create_options: # if command doesn't exist
            print('ERROR: CREATE: Invalid type: ' + args[0], file=sys.stderr) # stderr
            return 1

        if args[0].lower() == self.create_options['database'].lower(): # if option is database
            return self.create_db(args[1])
        elif args[0].lower() == self.create_options['table'].lower():
            return self.create_table(args[1:])

    def drop(self, args):
        if len(args) != 2:
            print('ERROR: DROP: invalid number of options specified.', file=sys.stderr) # stderr
            return 1
        elif not args[0] in self.create_options: # if command doesn't exist
            print('ERROR: DROP: Invalid type: ' + args[0], file=sys.stderr) # stderr
            return 1

        if args[0].lower() == self.create_options['database'].lower():
            self.delete_db(args[1])
        elif args[0].lower() == self.create_options['table'].lower():
            self.delete_table(args[1])


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

    def create_table(self, args):
        """Creates table as file"""
        try:
            self.current_db
        except:
            print("!Failed to create table, no database selected.")
            return 1
        else:
            database_dir = os.path.join(sys.path[0], "databases" + "/" + self.current_db)
            name = args[0]
            table = database_dir + "/" + name

        if not os.path.exists(database_dir + "/" + name):
            file = open(table, 'w') # create it
            output_string = " ".join(args[1:])
            output_string = output_string[1:-1]
            output_string = output_string.replace(',', ' |')
            file.write(output_string)
            print("Table", name, "created.")
        else:
            print("!Failed to create table", name, "because it already exists.")

    def delete_db(self, name):
        """Delete database as directory"""
        database_dir = os.path.join(sys.path[0], "databases")

        # check if databse exist
        if os.path.exists(database_dir + "/" + name):
            # delete the entire dir & files inside
            shutil.rmtree(database_dir + "/" + name)
            print('Database ' + name + ' deleted.')
        else:
            print ("!Failed to delete", name, "because it does not exist.")

    def delete_table(self, name):
        """Delete database as directory"""
        database_dir = os.getcwd()
        # check if table exist
        if os.path.exists(database_dir + "/" + name):
            # remove file only
            os.remove(database_dir + "/" + name)
            print('Table', name, 'deleted.')
        else:
            print ("!Failed to delete", name, "because it does not exist.")


    # USE FOR db
    def use(self, args):
        """use named database"""
        database_dir = os.path.join(sys.path[0], "databases")

        name = args[0]
        # check if databse exist
        if os.path.isdir(database_dir + "/" + name):
            os.chdir(database_dir + "/" + name)
            self.current_db = name
            print("Using Database", name + ".")
        else:
            print ("!Failed to use", name, "because it does not exist.")

    # SELECT for table
    def select(self, args):
        """Selects columns from given table, prints output"""
        if len(args) != 3:
            print("Expected 4 arguments.", file=sys.stderr)
            return 1
        else:
            cols = args[0].strip()
            table = args[2].strip()

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
    def alter(self, args):
        tbName = args[1]
        indexName = args[3]
        input_type = args[4]
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

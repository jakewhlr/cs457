"""Does stuff"""
import os
import sys
import shutil
import re
import operator

def create():
    pass

def drop():
    pass

def create_db(name):
    """Creates database as directory"""
    database_dir = os.path.join(sys.path[0], "databases")

    if not os.path.exists(database_dir): # if databases dir doesn't exist
        os.makedirs(database_dir) # create it

    if os.path.exists(database_dir + "/" + name):
        print("!Failed to create database", name, "because it already exists.")
    else:
        os.makedirs(database_dir + "/" + name)
        print("Database", name, "created.")

def create_table(name, values):
    """Creates table as file"""
    if 'databases' not in os.getcwd():
        print("!Failed to create table, no database selected.")
        return 1

    if not os.path.exists(os.getcwd() + "/" + name):
        file = open(name, 'w') # create it
        for index, value in enumerate(values):
            file.write(value)
            if index < len(values) - 1:
                file.write(' | ')
            else:
                file.write('\n')

        print("Table", name, "created.")
    else:
        print("!Failed to create table", name, "because it already exists.")

def drop_db(name):
    """Delete database as directory"""
    database_dir = os.path.join(sys.path[0], "databases")

    # check if database exists and remove the directory
    if os.path.exists(database_dir + "/" + name):
        shutil.rmtree(database_dir + "/" + name)
    else:
        print ("!Failed to delete", name, "because it does not exist.")

def drop_table(name):
    """Delete database as directory"""
    database_dir = os.path.join(sys.path[0], "databases")

    # check if table exists and remove the file
    if os.path.exists(database_dir + "/" + name):
        os.remove(database_dir + "/" + name)
    else:
        print ("!Failed to delete", name, "because it does not exist.")


def use(name):
    """use named database"""
    database_dir = os.path.join(sys.path[0], "databases")

    # check if databse exist
    if os.path.isdir(database_dir + "/" + name):
        os.chdir(database_dir + "/" + name)
        print("Using Database", name + ".")
    else:
        print ("!Failed to use", name, "because it does not exist.")

def select(args):
    """Selects columns from given table, prints output"""

    cols = None # Columns to select
    tables = None # Tables to select from
    left_test = None # Left thing to test
    conditional = None # Conditional function
    right_test = None # Right thing to test
    subquery = False # Bool to determine if where is used
    output_lines = []
    output_line = ''
    output_dict = {}
    output_dict_list = []
    col_header_list = []
    header_list = []

    opers = { "<": operator.lt, # dict of valid comparison operators
              "<=": operator.le,
              "=": operator.eq,
              "!=": operator.ne,
              ">": operator.gt,
              ">=": operator.ge,
          }
    data_types = { "int": int, # dict of valid types and their respective cast functions
                   "float": float,
                   "varchar": str,
          }

    for index, arg in enumerate(args):
        if index is 0:
            cols = arg
        elif arg[0] is 'from':
            tables = arg[1:]
        elif arg[0] is 'where':
            subquery = True
            left_test = arg[1][0]
            conditional = arg[1][1]
            right_test = arg[1][2]

    if len(tables) is 1:
        table = tables[0][0]
        table_path = os.path.join(os.getcwd(), table.lower())
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
            col_header_list.append(header.split(' ', 1))
            lines[0][header_index] = header.split(' ')
            if lines[0][header_index][0] in cols: # if col matches, note index
                col_indexes.append(header_index)
            if subquery and lines[0][header_index][0] == left_test:
                test_index = header_index
                test_type = data_types[lines[0][header_index][1].split("(")[0].strip()]

        for outer_index, outer_item in enumerate(col_header_list):
            for inner_index, inner_item in enumerate(outer_item):
                col_header_list[outer_index][inner_index] = re.sub(' ', '', inner_item)
        output_dict_list.append(col_header_list)
        col_header_list = []

        if '*' in cols: # '*' selects all columns
            col_indexes = range(0, len(lines[0]))

        for row_index, row in enumerate(lines):
            if row_index is 0:
                continue
            if subquery:
                if opers[conditional](test_type(re.sub('\'|\"', '', row[test_index])), test_type(re.sub('\'|\"', '', right_test))):
                    for col in col_indexes:
                        output_dict[output_dict_list[0][col][0]] = re.sub('\'|\"', '', row[col])
            else:
                for col in col_indexes:
                    output_dict[output_dict_list[0][col][0]] = re.sub('\'|\"', '', row[col])

            if output_dict:
                output_dict_list.append(output_dict)
                output_dict = {}
    else: # default JOIN
        table_selects = {}
        for index, table in enumerate(tables):
            table_args = []
            table_args.append(cols)
            table_args.append(['from', [table[0]]])
            table_selects[table[1]] = select(table_args)
        left_split = left_test.split('.')
        left_test_name = left_split[0]
        left_test_var = left_split[1]

        right_split = right_test.split('.')
        right_test_name = right_split[0]
        right_test_var = right_split[1]

        conditional_function = opers[conditional]
        output_dict_list.append(table_selects[left_test_name][0] + table_selects[right_test_name][0])
        for right_index, right_item in enumerate(table_selects[right_test_name]):
            if right_index is 0:
                continue
            for left_index, left_item in enumerate(table_selects[left_test_name]):
                if left_index is 0:
                    continue
                if conditional_function(left_item[left_test_var], right_item[right_test_var]):
                    output_dict = {**left_item, **right_item}
            output_dict_list.append(output_dict)
    return output_dict_list

def alter(tbName, indexName, input_type):
    table_path = os.path.join(os.getcwd(), tbName)

    if not os.path.exists(table_path):
        print ("!Failed to query table", tbName, "because it does not exist.")
        return

    org_file = open(table_path, 'r')

    # read file into list formatt
    read_file = org_file.read().splitlines()

    converted_to_string = ''.join(read_file)

    with open(table_path, "w") as alterFile:
        alterFile.write(converted_to_string + ' ' + '|' + ' ' + indexName +
                        ' ' + input_type + '\n')

    print("Table" + tbName+" modified.")

def insert(tbname, values):
    table_path = os.path.join(os.getcwd(), tbname)

    # check if table exist
    if os.path.exists(table_path):
        with open(tbname, "a") as table_file:
            for index, value in enumerate(values):
                table_file.write(value)
                if index < len(values) - 1:
                    table_file.write(' | ')
                else:
                    table_file.write('\n')
        print('1 new record inserted.')
    else:
    	print ("!Failed to insert", tbname, "because it does not exist.")

### DELETE:
# DELETE FROM [table name]
# WHERE [attribute name] {condition}
def delete(tbname, conditional, where_attr, where_val):
    if 'databases' not in os.getcwd():
        print("!Failed to read table, no database selected.")
        return 1

    opers = { "<": operator.lt, # dict of valid comparison operators
              "<=": operator.le,
              "=": operator.eq,
              "!=": operator.ne,
              ">": operator.gt,
              ">=": operator.ge,
            }

    data_types = { "int": int,
                   "float": float,
                   "varchar": str,
                 }

    records_deleted = 0
    table_path = os.path.join(os.getcwd(), tbname)
    jesql_reader = Reader(table_path)
    header = jesql_reader.read_header()
    for header_col in header:
        if header_col['name'] == where_attr:
            var_type = data_types[header_col['type']]

    for index, row in jesql_reader:
        if opers[conditional](var_type(row[where_attr]), var_type(where_val)):
            jesql_reader.delete_row(index)
            records_deleted += 1
    jesql_reader.write_file()

    print(records_deleted, 'records deleted')

def update(tbname, conditional, set_attr, set_val, where_attr, where_val):
    if 'databases' not in os.getcwd():
        print("!Failed to read table, no database selected.")
        return 1

    opers = { "<": operator.lt, # dict of valid comparison operators
              "<=": operator.le,
              "=": operator.eq,
              "!=": operator.ne,
              ">": operator.gt,
              ">=": operator.ge,
            }

    data_types = { "int": int,
                   "float": float,
                   "varchar": str,
                 }


    try:
        table_path = os.path.join(os.getcwd(), tbname)
        jesql_reader = Reader(table_path)
        header = jesql_reader.read_header()

        for header_col in header:
            if header_col['name'] == where_attr:
                var_type = data_types[header_col['type']]

        records_updated = 0
        for index, row in jesql_reader:
            if opers[conditional](var_type(row[where_attr]), var_type(where_val)):
                row[set_attr] = set_val
                jesql_reader.update_row(index, row)
                records_updated += 1
        jesql_reader.write_file()
        print(records_updated, 'records modified.')
    except FileNotFoundError:
        print('ERROR: Invalid table name')

class Reader(object):
    def __init__(self, filename, delimiter='|'):
        self.filename = filename
        self.delimiter = delimiter
        self.columns = []
        self.rows = []
        self.line_num = 0

        self.read_file()

    def __enter__(self):
        pass

    def __exit__(self):
        if self.file:
            self.file.close()

    def __iter__(self):
        return self

    def __next__(self):
        if self.line_num >= len(self.rows):
            raise StopIteration
        else:
            line = self.rows[self.line_num]
            row = {}
            for index, row_vals in enumerate(line.split(self.delimiter)):
                row_vals = row_vals.strip()
                row[self.columns[index]['name']] = row_vals

            self.line_num += 1
            return self.line_num - 1, row

    def read_header(self):
        header = self.rows[0]
        for column in header.split(self.delimiter):
            column = column.strip()
            column_vals = column.split(' ')
            self.columns.append({'name': column_vals[0], 'type': column_vals[1]})
        self.line_num += 1

        return self.columns

    def read_file(self):
        with open(self.filename, 'r') as file:
            self.rows = file.readlines()

    def update_row(self, index, row):
        raw_row = ''
        for key, value in row.items():
            raw_row += value + ' | '
        raw_row = raw_row[:-2]
        raw_row += '\n'
        self.rows[index] = raw_row

    def delete_row(self, index):
        del self.rows[index]

    def write_file(self):
        with open(self.filename, 'w') as file:
            file.writelines(self.rows)

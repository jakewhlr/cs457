"""Does stuff"""
import os
import sys
import shutil
import re
import operator
import jesql_utils

# dict of valid comparison operators
opers = { "<": operator.lt,
          "<=": operator.le,
          "=": operator.eq,
          "!=": operator.ne,
          ">": operator.gt,
          ">=": operator.ge,
        }

# dict of valid data types
data_types = { "int": int,
               "float": float,
               "varchar": str,
             }

transaction_in_progress = False
jesql_reader = None
header = None

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
        file.close()
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

    # check if table exists and remove the file
    if not os.path.exists(os.path.join(os.getcwd(), name)):
        print ("!Failed to delete", name, "because it does not exist.")
        return

    # TODO error message
    if os.path.exists(os.path.join(os.getcwd(), "." + name + "_lock")):
        print("Error: Table", name, "is locked!")
        if transaction_in_progress:
            transaction_in_progress = False # abort
            print("Transaction abort.")
        return

    os.remove(os.path.join(os.getcwd(), name))
    print("deleted", name)

def use(name):
    """use named database"""
    database_dir = os.path.join(sys.path[0], "databases")

    # check if databse exist
    if os.path.isdir(database_dir + "/" + name):
        os.chdir(database_dir + "/" + name)
        print("Using Database", name + ".")
    else:
        print ("!Failed to use", name, "because it does not exist.")

def select(stmt):
    table_paths = []
    jesql_readers = []
    headers = []
    rc_tables = []
    final_table = []

    # begin pre-processing
    for table, alias in stmt.subquery:
        new_table_path = os.path.join(os.getcwd(), table)
        if os.path.exists(new_table_path):
            table_paths.append(new_table_path)
            jesql_readers.append(jesql_utils.Reader(new_table_path, is_file=True, alias=alias))
            headers.append(jesql_readers[-1].read_header())

            # If the result column still contains a '*'
            for rc_table, rc_column in stmt.result_column:
                if rc_column == '*':
                    if rc_table:
                        stmt.result_column.evaluate_splat(rc_table)
                    else:
                        stmt.result_column.evaluate_splat(table)
        else:
            print ("!Failed to query table", table, "because it does not exist.")
            return

    # Check once more if * was evaluated and pop it off if necessary
    if stmt.result_column.column_names[0] == '*':
        stmt.result_column.pop()

    # Generate the final header for later
    final_header = ''
    stmt.result_column.insert_alias(stmt.subquery)
    for header in headers:
        for header_col in header:
            for column in stmt.result_column.column_names:
                if header_col['name'] == column:
                    final_header += header_col['name'] + ' ' + header_col['type'] + ' | '
    final_table.append(final_header[:-3])

    # read in all data specified in result column
    output_row = ''
    for jesql_reader in jesql_readers: # iterate over each table
        current_output = []
        current_output.append(jesql_reader.rows[0])
        for index, row in jesql_reader: # iterate over each row in table
            for key, value in row.items(): # iterate over each col in row
                for table_name, column_name in stmt.result_column: # iterate over statement result column
                    if key == column_name:
                        output_row += value + ' | '
            current_output.append(output_row[:-3])
            output_row = ''
        rc_tables.append(current_output)

    # prune data specified by where clause
    if stmt.expression:
        where_table = []
        # assign a reader to right and left table
        for table in rc_tables:
            table_reader = jesql_utils.Reader(table)
            table_header = table_reader.read_header()

            for column in table_header:
                if stmt.expression.left_value == column['name']:
                    left_reader = table_reader
                    left_header = table_header
                if stmt.expression.right_value == column['name']:
                    right_reader = table_reader
                    right_header = table_header

        l_inserted = []
        for l_index, l_row in left_reader:
            match_found = False
            for r_index, r_row in right_reader:
                formatted_row = ''
                if stmt.expression.oper(l_row[stmt.expression.left_value], r_row[stmt.expression.right_value]):
                    for l_val in list(l_row.values()):
                        formatted_row += l_val.strip("'") + ' | '
                    for r_val in list(r_row.values()):
                        formatted_row += r_val.strip("'") + ' | '
                    match_found = True
                    where_table.append(formatted_row[:-3])
                l_inserted.append(match_found)
        final_table += where_table

        if stmt.join_clause:
            if stmt.join_clause.join_modifier == 'left':
                for (index, row), result in zip(left_reader, l_inserted):
                    if not result:
                        formatted_row = ''
                        for key, value in row.items():
                            formatted_row += value.strip("'") + ' | '
                        final_table.append(formatted_row + ' | ')

    # prune data specified by join clause
    if stmt.join_clause:
        if stmt.join_clause.join_type == 'inner':
            # put inner code here
            pass
        else: # outer
            if stmt.join_clause.join_modifier == 'left':
                pass
            else: # right
                # put right code here
                pass

    # if neither other clause was run, generate the final table
    if not stmt.join_clause and not stmt.expression:
        final_table_tup = zip(*rc_tables)
        for row in final_table_tup:
            final_table.append(' | '.join(map(str, row)))
        del final_table[1]

    return final_table

def alter(tbName, indexName, input_type):
    global jesql_reader
    global transaction_in_progress
    global header

    table_path = os.path.join(os.getcwd(), tbName)

    if not os.path.exists(table_path):
        print ("!Failed to query table", tbName, "because it does not exist.")
        return

    # TODO error message
    if os.path.exists(os.path.join(os.getcwd(), "." + tbName + "_lock")):
        print("Error: Table", tbName, "is locked!")
        if transaction_in_progress:
            transaction_in_progress = False # abort
            print("Transaction abort.")
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
    global jesql_reader
    global transaction_in_progress
    global header


    table_path = os.path.join(os.getcwd(), tbname)

    # TODO error message
    if os.path.exists(os.path.join(os.getcwd(), "." + tbname + "_lock")):
        print("Error: Table", tbname, "is locked!")
        if transaction_in_progress:
            transaction_in_progress = False # abort
            print("Transaction abort.")
        return
    else:
        if transaction_in_progress:
            open(os.path.join(os.getcwd(), "." + tbname + "_lock"), 'w').close # create it


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

def delete(tbname, conditional, where_attr, where_val):
    global jesql_reader
    global transaction_in_progress
    global header


    if 'databases' not in os.getcwd():
        print("!Failed to read table, no database selected.")
        return 1

    # TODO error message
    if os.path.exists(os.path.join(os.getcwd(), "." + tbname + "_lock")):
        print("Error: Table", tbname, "is locked!")
        if transaction_in_progress:
            transaction_in_progress = False # abort
            print("Transaction abort.")
        return

    records_deleted = 0
    table_path = os.path.join(os.getcwd(), tbname)
    if not jesql_reader:
        jesql_reader = jesql_utils.Reader(table_path, is_file=True)
        header = jesql_reader.read_header()

    for header_col in header:
        if header_col['name'] == where_attr:
            var_type = data_types[header_col['type']]

    for index, row in jesql_reader:
        if opers[conditional](var_type(row[where_attr]), var_type(where_val)):
            jesql_reader.delete_row(index)
            records_deleted += 1
    if not transaction_in_progress:
        jesql_reader.write_file()

    print(records_deleted, 'records deleted')

def update(tbname, conditional, set_attr, set_val, where_attr, where_val):
    global jesql_reader
    global transaction_in_progress
    global header


    if 'databases' not in os.getcwd():
        print("!Failed to read table, no database selected.")
        return 1

    # TODO error message
    if os.path.exists(os.path.join(os.getcwd(), "." + tbname + "_lock")):
        print("Error: Table", tbname, "is locked!")
        if transaction_in_progress:
            transaction_in_progress = False # abort
            print("Transaction abort.")
        return
    else:
        if transaction_in_progress:
            open(os.path.join(os.getcwd(), "." + tbname + "_lock"), 'w').close # create it

    try:
        table_path = os.path.join(os.getcwd(), tbname)

        if not jesql_reader:
            jesql_reader = jesql_utils.Reader(table_path, is_file=True)
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
        if not transaction_in_progress:
            jesql_reader.write_file()
        print(records_updated, 'records modified.')
    except FileNotFoundError as e:
        print('ERROR: Invalid table name', e)

def begin_transaction():
    global transaction_in_progress
    transaction_in_progress = True
    return

def commit():
    global jesql_reader

    if jesql_reader:
        jesql_reader.write_file()
        transaction_in_progress = False
        path = jesql_reader.table.split('/')
        path[-1] = "." + path[-1] + "_lock"
        lock_path = "/".join(path)
        os.remove(lock_path)

    return

import jesql_commands
import sys
import tokenizer
import jesql_select
import jesql_utils

def parse(tokens):
    # check to make sure that actual data was passed in
    if tokens:
        sub_parser = 'parse_' + tokens[0].lower()
        if sub_parser not in dir(sys.modules[__name__]):
            print('ERROR: near "' + tokens[0] + '": syntax error', file=sys.stderr)
        else:
            globals()[sub_parser](tokens[1:])

def parse_create(tokens):
    if tokens[0].lower() == 'database':
        if len(tokens[1:]) == 1:
            jesql_commands.create_db(tokens[1])
        else:
            print('ERROR: near "' + tokens[-1] + '": syntax error', file=sys.stderr)

    elif tokens[0].lower() == 'table':
        if len(tokens[1:]) == 2:
            value_list = tokenizer.decapsulate_values(tokens[2])
            value_list = [value.strip() for value in value_list]
            jesql_commands.create_table(tokens[1], value_list)
        else:
            print('ERROR: near "' + tokens[-1] + '": syntax error', file=sys.stderr)

    else:
        print('ERROR: near "' + tokens[0] + '": syntax error', file=sys.stderr)

def parse_drop(tokens):
    if tokens[0].lower() == 'database':
        if len(tokens[1:]) == 1:
            jesql_commands.drop_db(tokens[1].lower())
        else:
            print('ERROR: near "' + tokens[-1] + '": syntax error', file=sys.stderr)

    elif tokens[0].lower() == 'table':
        if len(tokens[1:]) == 1:
            jesql_commands.drop_table(tokens[1].lower())
        else:
            print('ERROR: near "' + tokens[-1] + '": syntax error', file=sys.stderr)

    else:
        print('ERROR: near "' + tokens[0] + '": syntax error', file=sys.stderr)

def parse_use(tokens):
    if len(tokens) == 1:
        jesql_commands.use(tokens[0])
    else:
        print('ERROR: near "' + tokens[-1] + '": syntax error', file=sys.stderr)

# TODO
def parse_select(tokens):
    stmt = jesql_select.Statement(tokens)
    output = jesql_commands.select(stmt)
    if output:
        for row in output:
            print(row)
    else:
        print('select returned no results')

def parse_alter(tokens):
    if tokens[0].lower() == 'table':
        if len(tokens[1:]) == 4:
            jesql_commands.alter(tokens[1].lower(), tokens[3], tokens[4])
        else:
            print('ERROR: near "' + tokens[-1] + '": syntax error', file=sys.stderr)

    else:
        print('ERROR: near "' + tokens[0] + '": syntax error', file=sys.stderr)

def parse_insert(tokens):
    if tokens[0].lower() == 'into':
        if len(tokens[1:]) == 3:
            value_list = tokenizer.decapsulate_values(tokens[3])
            value_list = [value.strip() for value in value_list]

            jesql_commands.insert(tokens[1], value_list)
        else:
            print('ERROR: near "' + tokens[-1] + '": syntax error', file=sys.stderr)

    else:
        print('ERROR: near "' + tokens[0] + '": syntax error', file=sys.stderr)

def parse_delete(tokens):
    try:
        if tokens[0].lower() == 'from':
            if tokens[2].lower() == 'where':
                jesql_commands.delete(tokens[1].lower(), tokens[4], tokens[3], tokens[5])
            else:
                print('ERROR: near "' + tokens[2] + '": syntax error', file=sys.stderr)
        else:
            print('ERROR: near "' + tokens[0] + '": syntax error', file=sys.stderr)
    except IndexError as e:
        print('ERROR: expected arguments missing')

def parse_update(tokens):
    try:
        if tokens[1].lower() == 'set':
            if tokens[3] == '=' and tokens[7] == '=':
                if tokens[5].lower() == 'where':
                    jesql_commands.update(tokens[0].lower(), tokens[3], tokens[2], tokens[4], tokens[6], tokens[8])
                else:
                    print('ERROR: near "' + tokens[5] + '": syntax error', file=sys.stderr)
            else:
                print('ERROR: near "' + tokens[3] + '": syntax error', file=sys.stderr)
        else:
            print('ERROR: near "' + tokens[1] + '": syntax error', file=sys.stderr)
    except IndexError as e:
        print('ERROR: expected arguments missing')

def parse_begin(tokens):
    try:
        if tokens[0].lower() == 'transaction':
            jesql_commands.begin_transaction();
        else:
            print('ERROR: near "' + tokens[0] + '": syntax error', file=sys.stderr)
    except IndexError as e:
        print('ERROR: expected arguments missing')

def parse_commit(tokens):
    if not tokens:
        jesql_commands.commit():
    else:
        print('ERROR: near "' + tokens[0] + '": syntax error', file=sys.stderr)

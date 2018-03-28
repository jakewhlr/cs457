import jesql_commands
import sys
import tokenizer

def parse(tokens):
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
            jesql_commands.drop_db(tokens[1])
        else:
            print('ERROR: near "' + tokens[-1] + '": syntax error', file=sys.stderr)

    elif tokens[0].lower() == 'table':
        if len(tokens[1:]) == 1:
            jesql_commands.drop_table(tokens[1])
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
    jesql_commands.select(tokens)

def parse_alter(tokens):
    if tokens[0].lower() == 'table':
        if len(tokens[1:]) == 4:
            jesql_commands.alter(tokens[1], tokens[3], tokens[4])
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

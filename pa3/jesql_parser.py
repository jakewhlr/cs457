import jesql_commands
import sys
import tokenizer

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
            jesql_commands.create_db(tokens[1].lower())
        else:
            print('ERROR: near "' + tokens[-1] + '": syntax error', file=sys.stderr)

    elif tokens[0].lower() == 'table':
        if len(tokens[1:]) == 2:
            value_list = tokenizer.decapsulate_values(tokens[2])
            value_list = [value.strip() for value in value_list]
            jesql_commands.create_table(tokens[1].lower(), value_list)
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
        jesql_commands.use(tokens[0].lower())
    else:
        print('ERROR: near "' + tokens[-1] + '": syntax error', file=sys.stderr)

# TODO
def parse_select(tokens):
    # parse columns, place into sublists
    list_arg = []
    newargs = []
    for index, arg in enumerate(tokens):
        if arg.strip().lower() == 'from':
            from_index = index
            break
        list_arg.append(arg)
    for index in range(0, len(list_arg)):
        del tokens[0]
    for index, item in enumerate(list_arg):
        list_arg[index] = item.replace(',', '')
    tokens.insert(0, list_arg)

    # parse tables list, place into sublists
    list_item = []
    list_arg = []
    where_index = len(tokens)
    for index, arg in enumerate(tokens):
        if index < 2:
            continue
        if arg.strip().lower() == 'where':
            where_index = index
            break
        list_item.append(arg)
        if arg.endswith(','):
            for list_index, item in enumerate(list_item):
                list_item[list_index] = item.replace(',', '')
            list_arg.append(list_item)
            list_item = []
    if list_item:
        list_arg.append(list_item)
    for index in range (1, where_index):
        del tokens[1]
    list_arg.insert(0, 'from')
    tokens.insert(1, list_arg)

    # parse where list, place into sublists
    list_item = []
    list_arg = []
    for index, arg in enumerate(tokens):
        if index < 3:
            continue
        list_item.append(arg)

    for index in range (2, len(tokens)):
        del tokens[2]
    if list_item:
        list_arg.append('where')
        list_arg.append(list_item)
        tokens.append(list_arg)

    output = jesql_commands.select(tokens)
    print_select(output)

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

            jesql_commands.insert(tokens[1].lower(), value_list)
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

def print_select(select_list):
    for index, item in enumerate(select_list):
        if index is 0:
            for header_index, header_item in enumerate(item):
                print(' '.join(header_item), end='')
                if header_index is len(item) - 1:
                    print('')
                else:
                    print('|', end='')
        else:
            print('|'.join(item.values()))

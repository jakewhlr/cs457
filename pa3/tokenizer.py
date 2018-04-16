import sys
import re

def tokenize(raw_input):
    # split the input by ' ' & '(' & ')' while preserving the delimeters
    tokens = list(filter(None, re.split(r"( |\)|\()", raw_input)))
    # delete the stored ' ' delemiters from the list
    tokens[:] = (value for value in tokens if value != ' ')
    # remove any hidden tab characters
    tokens = [token.replace('\t', '') for token in tokens]

    return tokens

def encapsulate_values(input_list):
    start_index = -1
    end_index = -1
    open_parenthesis = 0
    close_parenthesis = 0
    for index, token in enumerate(input_list):
        if token.startswith('('):
            if start_index == -1:
                start_index = index
            open_parenthesis += 1
        if token.endswith(')'):
            if open_parenthesis == close_parenthesis + 1:
                end_index = index
            close_parenthesis += 1

    if start_index == -1 and end_index == -1:
        return input_list

    if open_parenthesis > close_parenthesis:
        print('ERROR: near "(": syntax error', file=sys.stderr)
    elif close_parenthesis > open_parenthesis:
        print('ERROR: near ")": syntax error', file=sys.stderr)
    else:
        values = [' '.join(input_list[start_index:end_index + 1])]
        updated_tokens = input_list[:start_index] + values + input_list[end_index + 1:]

        return updated_tokens

def decapsulate_values(values):
    values = values[1:-1]
    value_list = values.split(',')

    return value_list

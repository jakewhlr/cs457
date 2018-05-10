import jesql_utils
import operator
import sys
import os

class Statement(object):
    """class docstring"""
    def __init__(self, tokens):
        self.tokens = tokens
        self.result_column = None
        self.subquery = None
        self.join_clause = None
        self.expression = None

        self.evaluate_tokens()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        pass


    def __str__(self):
        return 'result_column: {}\nsubquery: {}\njoin_clause: {}\nexpression: {}'.format(self.result_column, self.subquery, self.join_clause, self.expression)

    def evaluate_tokens(self):
        if self.tokens:
            remaining_tokens, rc = self.evaluate_clause(self.tokens, 'from')
            remaining_tokens, sq = self.evaluate_clause(remaining_tokens[1:], 'where', 'inner', 'left')
            self.result_column = ResultColumn(rc)
            self.subquery = Subquery(sq)

            if not remaining_tokens:
                return
            elif remaining_tokens[0] == 'where':
                self.expression = Expression(remaining_tokens[1:])
            else:
                remaining_tokens, jc = self.evaluate_clause(remaining_tokens, 'join', include_delimiter=True)
                self.join_clause = JoinClause(jc)
                remaining_tokens, jtable = self.evaluate_clause(remaining_tokens[1:], 'on')
                self.subquery.insert(jtable)
                self.expression = Expression(remaining_tokens[1:])

    def evaluate_clause(self, tokens, *delimiters, include_delimiter=False):
        if delimiters:
            delimiter_index = -1
            expression = []

            for index, token in enumerate(tokens):
                for delimiter in delimiters:
                    if token.lower() == delimiter.lower():
                        delimiter_index = index
                        if include_delimiter:
                            expression.append(token)
                        break
                if delimiter_index == -1:
                    expression.append(token)

            if delimiter_index != -1:
                return tokens[delimiter_index:], expression
            else:
                return None, expression

        else:
            print('ERROR: evaluate_clause: no delimiters specified', file=sys.stderr)


class ResultColumn(object):
    def __init__(self, tokens):
        self.tokens = tokens
        self.table_names = []
        self.column_names = []

        self.parse_result_column()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        pass

    def __eq__(self, other):
        for index, table in enumerate(self.table_names):
            try:
                if table != other.table_names[index]:
                    return False
            except IndexError:
                return False

        for index, column in enumerate(self.column_names):
            try:
                if column != other.column_names[index]:
                    return False
            except IndexError:
                return False

        return True

    def __str__(self):
        output_string = ''
        for table, column in zip(self.table_names, self.column_names):
            output_string += '{{table_name: "{}", column_name: "{}"}},'.format(table, column)
        output_string = output_string[:-1]

        return '[{}]'.format(output_string)

    def __iter__(self):
        self.result_index = 0
        return self

    def __next__(self):
        if self.result_index >= len(self.table_names):
            raise StopIteration
        else:
            table_name = self.table_names[self.result_index]
            column_name = self.column_names[self.result_index]

            self.result_index += 1
            return table_name, column_name

    def parse_result_column(self):
        table_count = 0
        column_count = 0
        for token in self.tokens:
            if '.' in token:
                split_token = token.split('.')

                if split_token[1] == '*':
                    self.evaluate_splat(split_token[0])
                else:
                    self.table_names.append(split_token[0])
                    self.column_names.append(split_token[1].replace(',', ''))
                    table_count += 1
                    column_count += 1
            else:
                self.table_names.append(None)
                self.column_names.append(token)
                column_count += 1

        if table_count != column_count and table_count != 0:
            print('ERROR: parse_result_column: expected "." missing', file=sys.stderr)

    def evaluate_splat(self, table):
        table_path = os.path.join(os.getcwd(), table)

        jesql_reader = jesql_utils.Reader(table_path, is_file=True)
        header = jesql_reader.read_header()
        for header_col in header:
            self.table_names.append(table)
            self.column_names.append(header_col['name'])

    def insert_alias(self, subquery):
        for index, (table, column) in enumerate(zip(self.table_names, self.column_names)):
            for sq_table, sq_alias in zip(subquery.tables, subquery.aliases):
                if table == sq_table:
                    if sq_alias:
                        self.column_names[index] = sq_alias + '.' + column

    def pop(self):
        self.table_names.pop(0)
        self.column_names.pop(0)


class Subquery(object):
    """class docstring"""
    def __init__(self, tokens):
        self.tokens = tokens
        self.tables = []
        self.aliases = []

        self.parse_subquery()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        pass

    def __eq__(self, other):
        for index, table in enumerate(self.tables):
            try:
                if table != other.tables[index]:
                    return False
            except IndexError:
                return False

        for index, alias in enumerate(self.aliases):
            try:
                if alias != other.aliases[index]:
                    return False
            except IndexError:
                return False

        return True

    def __str__(self):
        output_string = ''
        for table, alias in zip(self.tables, self.aliases):
            output_string += '{{table_name: "{}", alias: "{}"}},'.format(table, alias)
        output_string = output_string[:-1]

        return '[{}]'.format(output_string)

    def __iter__(self):
        self.query_index = 0
        return self

    def __next__(self):
        if self.query_index >= len(self.tables):
            raise StopIteration
        else:
            table = self.tables[self.query_index]

            try:
                alias = self.aliases[self.query_index]
            except IndexError:
                alias = None

            self.query_index += 1
            return table, alias

    def parse_subquery(self):
        # if the subquery was just a table
        token_string = ' '.join(self.tokens)
        new_tokens = token_string.split(',')

        for token in new_tokens:
            split_tokens = token.strip().split(' ')
            if len(split_tokens) == 2:
                self.tables.append(split_tokens[0])
                self.aliases.append(split_tokens[1])
            else:
                self.tables.append(split_tokens[0])
                self.aliases.append(None)

    def insert(self, tokens):
        if len(tokens) == 1:
            self.tables.append(tokens[0])
            self.aliases.append(None)
        if len(tokens) == 2:
            self.tables.append(tokens[0])
            self.aliases.append(tokens[1])
        else:
            print('ERROR: insert: invalid number of arguments supplie', file=sys.stderr)

class JoinClause(object):
    def __init__(self, tokens):
        self.tokens = tokens
        self.join_type = None
        self.join_modifier = None

        self.parse_join()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        pass

    def __str__(self):
        return '{{join_type: "{}", join_modifier: "{}"}}'.format(self.join_type, self.join_modifier)


    def parse_join(self):
        if self.tokens[0] == 'join' or self.tokens[0] == 'inner':
            self.join_type = 'inner'
        elif self.tokens[0] == 'left':
            self.join_type = 'outer'
            self.join_modifier = 'left'
        elif self.tokens[0] == 'right':
            self.join_type = 'outer'
            self.join_modifier = 'right'
        else:
            print('ERROR: parse_join: invalid join type specified', file=sys.stderr)


class Expression(object):
    """class docstring"""
    opers = { "<": operator.lt,
              "<=": operator.le,
              "=": operator.eq,
              "!=": operator.ne,
              ">": operator.gt,
              ">=": operator.ge,
            }

    def __init__(self, tokens):
        self.tokens = tokens
        self.left_value = None
        self.oper = None
        self.right_value = None

        self.parse_expression()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        pass

    def __eq__(self, other):
        if self.left_value != other.left_value:
            print('1')
            return False
        elif self.oper != other.oper:
            print('2')
            return False
        elif self.right_value != other.right_value:
            print('3')
            return False
        else:
            return True

    def __str__(self):
        return '{{left_value: "{}", oper: {}, right_value: "{}"}}'.format(self.left_value, self.oper, self.right_value)

    def parse_expression(self):
        if len(self.tokens) == 3:
            for key, value in self.opers.items():
                if self.tokens[1] == key:
                    self.oper = value

            if self.oper == None:
                print('ERROR: parse_expression:', self.tokens[1], 'is not a valid operator', file=sys.stderr)
                return

            self.left_value = self.tokens[0]
            self.right_value = self.tokens[2]
        else:
            print('ERROR: parse_expression: malformed expression supplied', file=sys.stderr)

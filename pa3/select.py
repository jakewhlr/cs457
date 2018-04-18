import sys
import operator

# select *
# from Employee E, Sales S
# where E.id = S.employeeID;

# select *
# from Employee E inner join Sales S
# on E.id = S.employeeID;

# select *
# from Employee E left outer join Sales S
# on E.id = S.employeeID;

class Statement(object):
    """class docstring"""
    def __init__(self, tokens):
        self.tokens = tokens
        self.result_columns = []
        self.subquery = None
        self.expression = None

        self.evaluate_tokens()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        pass

    def evaluate_tokens(self):
        if self.tokens:
            remaining_tokens, self.result_columns = self.evaluate_clause(self.tokens, 'from')
            remaining_tokens, sq = self.evaluate_clause(remaining_tokens[1:], 'where', 'inner', 'left')
            self.subquery = Subquery(sq)

            if not remaining_tokens:
                return
            elif remaining_tokens[0] == 'where':
                self.expression = Expression(remaining_tokens[1:])
            elif remaining_tokens[0] == 'inner':
                pass
            elif remaining_tokens[0] == 'left':
                pass
            else:
                print('ERROR: evaluate_tokens: unexpected token encountered "' +
                      tokens[0] + '"', file=sys.stderr)

        # self.evaluate_subquery(subquery)
        # if tokens[next_index] == 'where'

    def evaluate_clause(self, tokens, *delimiters):
        if delimiters:
            delimiter_index = -1
            expression = []

            for index, token in enumerate(tokens):
                for delimiter in delimiters:
                    if token.lower() == delimiter.lower():
                        delimiter_index = index
                        break
                if delimiter_index == -1:
                    expression.append(token)

            if delimiter_index != -1:
                return tokens[delimiter_index:], expression
            else:
                return None, expression

        else:
            print('ERROR: evaluate_clause: no delimiters specified', file=sys.stderr)


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
        if len(self.tokens) == 1:
            self.tables.append(self.tokens[0])
        else:
            self.tables = self.tokens[0::2]
            self.aliases = self.tokens[1::2]

            for index, alias in enumerate(self.aliases):
                self.aliases[index] = alias.replace(',', '')

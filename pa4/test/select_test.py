import unittest
import select
import operator

class TestStatement(unittest.TestCase):
    def test_where(self):
        query = ['*', 'from', 'Employee', 'E,', 'Sales', 'S', 'where', 'E.id', '=', 'S.employeeID']
        expected_result_columns = ['*']
        expected_subquery = select.Subquery(['Employee', 'E,', 'Sales', 'S'])
        expected_expression = select.Expression(['E.id', '=', 'S.employeeID'])

        stmt = select.Statement(query)

        self.assertEqual(stmt.result_columns, expected_result_columns)
        self.assertTrue(stmt.subquery == expected_subquery)
        self.assertTrue(stmt.expression == expected_expression)


class TestExpression(unittest.TestCase):
    def test_constructor(self):
        ex = select.Expression(['salary', '=', 'id'])
        self.assertEqual(ex.left_value, 'salary')
        self.assertEqual(ex.oper, operator.eq)
        self.assertEqual(ex.right_value, 'id')


class TestSubquery(unittest.TestCase):
    def test_subquery_alias(self):
        sq = select.Subquery(['Employee', 'E,', 'Sales', 'S'])

        self.assertEqual(sq.tables[0], 'Employee')
        self.assertEqual(sq.tables[1], 'Sales')

        self.assertEqual(sq.aliases[0], 'E')
        self.assertEqual(sq.aliases[1], 'S')

    def test_subquery_no_alias(self):
        sq = select.Subquery(['Employee'])

        self.assertEqual(sq.tables[0], 'Employee')

        with self.assertRaises(IndexError):
            sq.aliases[0]

    def test_subquery_iter(self):
        sq = select.Subquery(['Employee', 'E,', 'Sales', 'S'])

        index = 0
        for table, alias in sq:
            self.assertEqual(table, sq.tables[index])
            self.assertEqual(alias, sq.aliases[index])
            index += 1

        sq_no_alias = select.Subquery(['Employee'])
        sq_no_alias.parse_subquery()

        index = 0
        for table, alias in sq_no_alias:
            self.assertEqual(table, sq_no_alias.tables[index])
            self.assertEqual(alias, None)

"""module description"""

class Reader(object):
    def __init__(self, table_name, delimiter='|', is_file=False, alias=None):
        self.table = table_name
        self.delimiter = delimiter
        self.columns = []
        self.rows = table_name
        self.line_num = 0
        self.alias = alias

        if is_file:
            self.read_file()

    def __enter__(self):
        pass

    def __exit__(self):
        if self.file:
            self.file.close()

    def __iter__(self):
        if self.line_num != 1:
            self.line_num = 0
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

            if self.alias:
                formatted_header = {'name': self.alias + '.' + column_vals[0], 'type': column_vals[1]}
            else:
                formatted_header = {'name': column_vals[0], 'type': column_vals[1]}

            self.columns.append(formatted_header)

        self.line_num += 1
        self.update_header()

        return self.columns

    def read_file(self):
        with open(self.table, 'r') as file:
            self.rows = file.readlines()

    def update_row(self, index, row):
        raw_row = ''
        for key, value in row.items():
            raw_row += value + ' | '
        raw_row = raw_row[:-2]
        raw_row += '\n'
        self.rows[index] = raw_row

    def update_header(self):
        raw_row = ''
        for column in self.columns:
            for key, value in column.items():
                raw_row += value + ' '
            raw_row += '| '

        self.rows[0] = raw_row[:-3]

    def delete_row(self, index):
        del self.rows[index]

    def write_file(self):
        with open(self.table, 'w') as file:
            file.writelines(self.rows)

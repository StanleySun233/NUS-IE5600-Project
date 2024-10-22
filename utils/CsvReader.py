class CSVReader:
    def __init__(self, filename, delimiter=','):
        self.filename = filename
        self.delimiter = delimiter
        self.data = self.read()

    def read(self):
        data = []
        try:
            with open(self.filename, 'r', encoding='utf-8') as file:
                # 读取文件的每一行
                lines = file.readlines()
                for line in lines:
                    # 去除行末的换行符，并使用指定的分隔符分割字段
                    row = line.strip().split(self.delimiter)
                    data.append(row)
            return data
        except FileNotFoundError:
            print(f"Error: File '{self.filename}' not found.")
            return None

    def get_headers(self):
        if self.data:
            return self.data[0]  # 假设第一行是表头
        return None

    def get_row(self, row_num):
        if self.data and row_num < len(self.data):
            return self.data[row_num]  # 获取指定行
        return None

    def get_column(self, col_num):
        if self.data and col_num < len(self.data[0]):
            return [row[col_num] for row in self.data]  # 获取指定列
        return None

    def get_rows_by_value(self,col,val):
        _index = self.get_headers().index(col)
        sheet = []
        for i in self.data:
            if i[_index] == val:
                sheet.append(i)
        return sheet



if __name__ == "__main__":
    csv_reader = CSVReader('../data/ais.csv')
    data = csv_reader.read()  # 读取整个CSV文件
    headers = csv_reader.get_headers()  # 获取表头
    first_row = csv_reader.get_row(1)  # 获取第1行
    # first_column = csv_reader.get_column(0)  # 获取第1列

    # 输出示例
    print("表头:", headers)
    print("第1行数据:", first_row)
    # print("第1列数据:", first_column)
    print(csv_reader.get_rows_by_value("mmsi",'414350530'))
from pymysql import cursors


pymysqlConfig = {
    'host': 'localhost',
    'port': 3306,
    'user': 'moon',
    'password': 'wylj',
    'db': 'amazon',
    'charset': 'utf8mb4',
    'cursorclass': cursors.Cursor
}

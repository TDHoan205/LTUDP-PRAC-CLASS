import pymysql.cursors
connection= pymysql.connect(
    host='127.0.0.1',
    user='root',
    password='',
    db='dbbanhang',
    cursorclass=pymysql.cursors.DictCursor
)
try:
    with connection.cursor() as cursor:
        sql = "SELECT * FROM mathang"
        cursor.execute(sql)
        result = cursor.fetchall()
        print("Danh sách mặt hàng:")
        for item in result:
            print(f"Mã mặt hàng: {item['MaMatHang']}, Tên mặt hàng: {item['TenMatHang']}, Giá: {item['Gia']}")
finally:    connection.close()
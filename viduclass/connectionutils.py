import pymysql.cursors

# Có thể thay đổi các thông số kết nối.
def getConnection():
    try:
        conn = pymysql.connect(
            host='127.0.0.1',
            user='root',
            password='',
            db='dbbanhang',
            cursorclass=pymysql.cursors.DictCursor,
            charset='utf8mb4',
            autocommit=True,
            connect_timeout=5
        )
        print("✅ Connection established successfully!")
        return conn
    except pymysql.Error as e:
        print(f"❌ Database connection failed: {e}")
        return None
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return None
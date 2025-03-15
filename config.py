import pymysql



def connect_db():
    try:
        connection = pymysql.connect(
            host="localhost",
            user="root",
            password="",
            database="cua_hang_thu_cung",  # Đổi tên database của bạn
            port=3306  # Kiểm tra cổng kết nối MySQL
        )
        return connection
    except pymysql.MySQLError as e:
        print(f"Lỗi kết nối MySQL: {e}")
        return None  # Trả về None nếu kết nối thất bại

import sys
import pymysql.cursors
from PyQt6 import uic
from PyQt6.QtWidgets import QApplication, QMainWindow, QMessageBox
from config import connect_db
from dangnhap import LoginWindow  # Import cửa sổ đăng nhập

class RegisterWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Load giao diện từ file UI
        uic.loadUi('views/dangky.ui', self)

        # Kết nối sự kiện cho nút đăng ký
        self.register_button.clicked.connect(self.register)
    
    def register(self):
        """ Xử lý đăng ký tài khoản mới """
        name = self.hovaten_input.text().strip()
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()
        role = self.role_input.currentText()

        # Kiểm tra nếu có trường nào bị bỏ trống
        if not name or not username or not password:
            QMessageBox.warning(self, 'Lỗi', 'Vui lòng điền đầy đủ thông tin!')
            return

        connection = connect_db()  # Kết nối CSDL
        try:
            with connection.cursor(pymysql.cursors.DictCursor) as cursor:
                # Kiểm tra xem tài khoản đã tồn tại chưa
                check_sql = "SELECT TaiKhoan FROM NhanVien WHERE TaiKhoan=%s"
                cursor.execute(check_sql, (username,))
                if cursor.fetchone():
                    QMessageBox.warning(self, 'Lỗi', 'Tài khoản đã tồn tại!')
                    return
                
                # Thêm tài khoản mới vào CSDL
                sql = "INSERT INTO NhanVien (HoTen, TaiKhoan, MatKhau, PhanQuyen) VALUES (%s, %s, %s, %s)"
                cursor.execute(sql, (name, username, password, role))
                connection.commit()
                
                QMessageBox.information(self, 'Thành công', 'Đăng ký thành công!')
                self.open_login_window()
        except pymysql.MySQLError as e:
            QMessageBox.critical(self, 'Lỗi', f'Lỗi MySQL: {e}')
        finally:
            connection.close()

    def open_login_window(self):
        """ Chuyển về màn hình đăng nhập sau khi đăng ký thành công """
        self.login_window = LoginWindow()
        self.login_window.show()
        self.close()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = RegisterWindow()
    window.show()
    sys.exit(app.exec())

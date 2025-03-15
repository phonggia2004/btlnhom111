import sys
from PyQt6 import uic
from PyQt6.QtWidgets import QApplication, QMainWindow, QMessageBox
import pymysql.cursors
from config import connect_db
# from register import RegisterWindow

class LoginWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Load the UI
        uic.loadUi('views/login1.ui', self)

        # Connect buttons to functions
        self.login_button.clicked.connect(self.login)
        self.register_button.clicked.connect(self.open_register_window)
    
    def login(self):
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()

        if not username or not password:
            QMessageBox.warning(self, 'Lỗi', 'Vui lòng nhập đầy đủ tài khoản và mật khẩu!')
            return
        
        connection = connect_db()
        try:
            with connection.cursor(pymysql.cursors.DictCursor) as cursor: 
                sql = "SELECT TaiKhoan, PhanQuyen FROM NhanVien WHERE TaiKhoan=%s AND MatKhau=%s"
                cursor.execute(sql, (username, password))
                result = cursor.fetchone()

                if result:
                    username = result['TaiKhoan']
                    chuc_vu = result['PhanQuyen']
                    QMessageBox.information(self, 'Thành công', 'Đăng nhập thành công!')
                    self.open_trangchu_window(username, chuc_vu)
                else:
                    QMessageBox.warning(self, 'Lỗi', 'Sai tài khoản hoặc mật khẩu!')
        except pymysql.MySQLError as e:
            QMessageBox.critical(self, 'Lỗi kết nối', f'Lỗi MySQL: {str(e)}')
        finally:
            connection.close()

    def open_register_window(self):
        from register import RegisterWindow
        self.register_window = RegisterWindow()
        self.register_window.show()
        self.hide()
        
    def open_trangchu_window(self, username, chuc_vu):
        from home import MainWindow
        self.trangchu_window = MainWindow(username, chuc_vu)
        self.trangchu_window.show()
        self.hide()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LoginWindow()
    window.show()
    sys.exit(app.exec())

import sys
import pymysql
import re
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLineEdit, QPushButton,
    QTableWidget, QTableWidgetItem, QMessageBox, QFormLayout, QLabel
)
from config import connect_db

# ====== KẾT NỐI CƠ SỞ DỮ LIỆU ======

# ====== CHỨC NĂNG QUẢN LÝ KHÁCH HÀNG ======
def danh_sach_khach_hang():
    conn = connect_db()
    if not conn:
        return []
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM khachhang")
    result = cursor.fetchall()
    conn.close()
    return result

# ====== HÀM KIỂM TRA DỮ LIỆU ======
def kiem_tra_so_dien_thoai(so_dien_thoai):
    """Kiểm tra số điện thoại: 10 chữ số, bắt đầu bằng 0"""
    pattern = r'^0\d{9}$'
    if not re.match(pattern, so_dien_thoai):
        return False, "Số điện thoại phải có 10 chữ số và bắt đầu bằng 0!"
    return True, ""

def kiem_tra_email(email):
    """Kiểm tra định dạng email"""
    if not email:
        return True, ""  # Email không bắt buộc
    pattern = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    if not re.match(pattern, email):
        return False, "Email không hợp lệ!"
    return True, ""

def kiem_tra_do_dai(chuoi, ten_truong, do_dai_toi_da):
    """Kiểm tra độ dài của chuỗi"""
    if len(chuoi) > do_dai_toi_da:
        return False, f"{ten_truong} không được vượt quá {do_dai_toi_da} ký tự!"
    return True, ""

class QuanLyKhachHang(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Quản lý Khách Hàng")
        self.setGeometry(100, 100, 600, 500)

        self.layout = QVBoxLayout()

        # Form nhập dữ liệu
        self.form_layout = QFormLayout()
        self.input_ho_ten = QLineEdit()
        self.input_so_dien_thoai = QLineEdit()
        self.input_email = QLineEdit()
        self.input_dia_chi = QLineEdit()

        self.form_layout.addRow("Họ Tên:", self.input_ho_ten)
        self.form_layout.addRow("Số ĐT:", self.input_so_dien_thoai)
        self.form_layout.addRow("Email:", self.input_email)
        self.form_layout.addRow("Địa chỉ:", self.input_dia_chi)
        self.layout.addLayout(self.form_layout)

        # Nút thêm khách hàng
        self.button_them = QPushButton("Thêm khách hàng")
        self.button_them.clicked.connect(self.xu_ly_them_khach_hang)
        self.layout.addWidget(self.button_them)

        # Bảng danh sách khách hàng
        self.bang = QTableWidget(self)
        self.bang.setColumnCount(5)
        self.bang.setHorizontalHeaderLabels(["Mã KH", "Họ Tên", "Số ĐT", "Email", "Địa chỉ"])
        self.layout.addWidget(self.bang)

        # Nút cập nhật
        self.button_cap_nhat = QPushButton("Cập nhật khách hàng")
        self.button_cap_nhat.clicked.connect(self.xu_ly_cap_nhat_khach_hang)
        self.layout.addWidget(self.button_cap_nhat)

        # Nút xóa khách hàng
        self.button_xoa = QPushButton("Xóa khách hàng")
        self.button_xoa.clicked.connect(self.xu_ly_xoa_khach_hang)
        self.layout.addWidget(self.button_xoa)

        self.setLayout(self.layout)
        self.hien_thi_danh_sach_khach_hang()
    
    def hien_thi_danh_sach_khach_hang(self):
        """Hiển thị danh sách khách hàng trong bảng"""
        self.bang.clearContents()
        khach_hang = danh_sach_khach_hang()
        self.bang.setRowCount(len(khach_hang))

        for row, khach in enumerate(khach_hang):
            for col, data in enumerate(khach):
                self.bang.setItem(row, col, QTableWidgetItem(str(data)))
        self.bang.resizeColumnsToContents()

    def kiem_tra_du_lieu(self, ho_ten, so_dien_thoai, email, dia_chi):
        """Kiểm tra toàn bộ dữ liệu đầu vào"""
        # Kiểm tra trường bắt buộc
        if not ho_ten or not so_dien_thoai:
            return False, "Vui lòng nhập đầy đủ họ tên và số điện thoại!"

        # Kiểm tra độ dài
        checks = [
            kiem_tra_do_dai(ho_ten, "Họ Tên", 50),
            kiem_tra_do_dai(so_dien_thoai, "Số ĐT", 10),
            kiem_tra_do_dai(email, "Email", 100),
            kiem_tra_do_dai(dia_chi, "Địa chỉ", 200),
        ]
        for valid, message in checks:
            if not valid:
                return False, message

        # Kiểm tra định dạng
        valid_sdt, msg_sdt = kiem_tra_so_dien_thoai(so_dien_thoai)
        if not valid_sdt:
            return False, msg_sdt

        valid_email, msg_email = kiem_tra_email(email)
        if not valid_email:
            return False, msg_email

        return True, ""

    def xu_ly_them_khach_hang(self):
        ho_ten = self.input_ho_ten.text().strip()
        so_dien_thoai = self.input_so_dien_thoai.text().strip()
        email = self.input_email.text().strip()
        dia_chi = self.input_dia_chi.text().strip()

        # Kiểm tra dữ liệu
        valid, message = self.kiem_tra_du_lieu(ho_ten, so_dien_thoai, email, dia_chi)
        if not valid:
            QMessageBox.warning(self, "Lỗi", message)
            return

        conn = connect_db()
        if not conn:
            return
        cursor = conn.cursor()

        # Kiểm tra trùng số điện thoại
        cursor.execute("SELECT COUNT(*) FROM khachhang WHERE SoDienThoai = %s", (so_dien_thoai,))
        if cursor.fetchone()[0] > 0:
            QMessageBox.warning(self, "Lỗi", "Số điện thoại đã tồn tại!")
            conn.close()
            return

        try:
            query = "INSERT INTO khachhang (HoTen, SoDienThoai, Email, DiaChi) VALUES (%s, %s, %s, %s)"
            cursor.execute(query, (ho_ten, so_dien_thoai, email, dia_chi))
            conn.commit()
            QMessageBox.information(self, "Thành công", "Thêm khách hàng thành công!")
        except pymysql.err.IntegrityError:
            QMessageBox.warning(self, "Lỗi", "Số điện thoại đã tồn tại!")
        finally:
            conn.close()
        self.hien_thi_danh_sach_khach_hang()

    def xu_ly_cap_nhat_khach_hang(self):
        selected_items = self.bang.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Lỗi", "Vui lòng chọn khách hàng để cập nhật!")
            return

        ma_khach_hang = selected_items[0].text()
        ho_ten = self.input_ho_ten.text().strip()
        so_dien_thoai = self.input_so_dien_thoai.text().strip()
        email = self.input_email.text().strip()
        dia_chi = self.input_dia_chi.text().strip()

        # Kiểm tra dữ liệu
        valid, message = self.kiem_tra_du_lieu(ho_ten, so_dien_thoai, email, dia_chi)
        if not valid:
            QMessageBox.warning(self, "Lỗi", message)
            return

        conn = connect_db()
        if not conn:
            return
        cursor = conn.cursor()

        # Kiểm tra trùng số điện thoại (trừ chính khách hàng đang cập nhật)
        cursor.execute("SELECT COUNT(*) FROM khachhang WHERE SoDienThoai = %s AND MaKhachHang != %s", 
                       (so_dien_thoai, ma_khach_hang))
        if cursor.fetchone()[0] > 0:
            QMessageBox.warning(self, "Lỗi", "Số điện thoại đã tồn tại ở khách hàng khác!")
            conn.close()
            return

        try:
            query = "UPDATE khachhang SET HoTen=%s, SoDienThoai=%s, Email=%s, DiaChi=%s WHERE MaKhachHang=%s"
            cursor.execute(query, (ho_ten, so_dien_thoai, email, dia_chi, ma_khach_hang))
            conn.commit()
            QMessageBox.information(self, "Thành công", "Cập nhật khách hàng thành công!")
        except pymysql.err.IntegrityError:
            QMessageBox.warning(self, "Lỗi", "Số điện thoại đã tồn tại!")
        finally:
            conn.close()
        self.hien_thi_danh_sach_khach_hang()

    def xu_ly_xoa_khach_hang(self):
        selected_items = self.bang.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Lỗi", "Vui lòng chọn khách hàng để xóa!")
            return

        ma_khach_hang = selected_items[0].text()
        confirmation = QMessageBox.question(
            self, "Xác nhận xóa", "Bạn có chắc chắn muốn xóa khách hàng này?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, 
            QMessageBox.StandardButton.No
        )
        
        if confirmation == QMessageBox.StandardButton.Yes:
            conn = connect_db()
            if not conn:
                return
            cursor = conn.cursor()
            try:
                query = "DELETE FROM khachhang WHERE MaKhachHang=%s"
                cursor.execute(query, (ma_khach_hang,))
                conn.commit()
                QMessageBox.information(self, "Thành công", "Xóa khách hàng thành công!")
            except pymysql.MySQLError as e:
                QMessageBox.critical(self, "Lỗi", f"Không thể xóa: {str(e)}")
            finally:
                conn.close()
            self.hien_thi_danh_sach_khach_hang()

# ====== CHẠY ỨNG DỤNG ======
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = QuanLyKhachHang()
    window.show()
    sys.exit(app.exec())
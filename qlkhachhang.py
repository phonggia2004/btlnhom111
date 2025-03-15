import sys
import pymysql
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLineEdit, QPushButton,
    QTableWidget, QTableWidgetItem, QMessageBox, QFormLayout, QLabel
)

# ====== KẾT NỐI CƠ SỞ DỮ LIỆU ======
def ket_noi_db():
    try:
        conn = pymysql.connect(
            host="localhost",
            user="root",         # Thay bằng user MySQL của bạn
            password="",         # Thay bằng password MySQL của bạn
            database="cua_hang_thu_cung"
        )
        return conn
    except pymysql.MySQLError as err:
        QMessageBox.critical(None, "Lỗi CSDL", f"Không thể kết nối: {err}")
        return None

# ====== CHỨC NĂNG QUẢN LÝ KHÁCH HÀNG ======
def danh_sach_khach_hang():
    conn = ket_noi_db()
    if not conn:
        return []
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM khachhang")
    result = cursor.fetchall()
    conn.close()
    return result

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

    def xu_ly_them_khach_hang(self):
        ho_ten = self.input_ho_ten.text()
        so_dien_thoai = self.input_so_dien_thoai.text()
        email = self.input_email.text()
        dia_chi = self.input_dia_chi.text()
        if not ho_ten or not so_dien_thoai:
            QMessageBox.warning(self, "Lỗi", "Vui lòng nhập đầy đủ thông tin!")
            return

        conn = ket_noi_db()
        if not conn:
            return
        cursor = conn.cursor()
        query = "INSERT INTO khachhang (HoTen, SoDienThoai, Email, DiaChi) VALUES (%s, %s, %s, %s)"
        cursor.execute(query, (ho_ten, so_dien_thoai, email, dia_chi))
        conn.commit()
        conn.close()
        self.hien_thi_danh_sach_khach_hang()

    def xu_ly_cap_nhat_khach_hang(self):
        selected_items = self.bang.selectedItems()
        if selected_items:
            ma_khach_hang = selected_items[0].text()
            ho_ten = self.input_ho_ten.text()
            so_dien_thoai = self.input_so_dien_thoai.text()
            email = self.input_email.text()
            dia_chi = self.input_dia_chi.text()
            
            conn = ket_noi_db()
            if not conn:
                return
            cursor = conn.cursor()
            query = "UPDATE khachhang SET HoTen=%s, SoDienThoai=%s, Email=%s, DiaChi=%s WHERE MaKhachHang=%s"
            cursor.execute(query, (ho_ten, so_dien_thoai, email, dia_chi, ma_khach_hang))
            conn.commit()
            conn.close()
            self.hien_thi_danh_sach_khach_hang()

    def xu_ly_xoa_khach_hang(self):
        selected_items = self.bang.selectedItems()
        if selected_items:
            ma_khach_hang = selected_items[0].text()

            confirmation = QMessageBox.question(
                self, "Xác nhận xóa", "Bạn có chắc chắn muốn xóa khách hàng này?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, 
                QMessageBox.StandardButton.No
            )
            
            if confirmation == QMessageBox.StandardButton.Yes:
                conn = ket_noi_db()
                if not conn:
                    return
                cursor = conn.cursor()
                query = "DELETE FROM khachhang WHERE MaKhachHang=%s"
                cursor.execute(query, (ma_khach_hang,))
                conn.commit()
                conn.close()
                self.hien_thi_danh_sach_khach_hang()

# ====== CHẠY ỨNG DỤNG ======
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = QuanLyKhachHang()
    window.show()
    sys.exit(app.exec())
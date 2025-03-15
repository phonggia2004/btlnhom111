import sys
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLineEdit, QPushButton,
    QTableWidget, QTableWidgetItem, QMessageBox, QFormLayout, QLabel, QComboBox
)
from config import connect_db  # Thay import mysql.connector bằng import từ config

# ====== KẾT NỐI CƠ SỞ DỮ LIỆU ======
def ket_noi_db():
    try:
        conn = connect_db()  # Sử dụng hàm connect_db từ config.py
        if conn is None:
            raise Exception("Không thể kết nối đến cơ sở dữ liệu!")
        return conn
    except Exception as err:
        QMessageBox.critical(None, "Lỗi CSDL", f"Không thể kết nối: {err}")
        return None

# ====== CHỨC NĂNG QUẢN LÝ NHÂN VIÊN ======
def danh_sach_nhan_vien():
    conn = ket_noi_db()
    if not conn:
        return []
    cursor = conn.cursor()  # Sử dụng cursor của pymysql
    cursor.execute("SELECT * FROM nhanvien")
    result = cursor.fetchall()
    conn.close()  # Đóng kết nối sau khi lấy dữ liệu
    return result

class QuanLyNhanVien(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Quản lý Nhân Viên")
        self.setGeometry(100, 100, 600, 500)

        self.layout = QVBoxLayout()

        # Form nhập dữ liệu
        self.form_layout = QFormLayout()
        self.input_ho_ten = QLineEdit()
        self.input_tai_khoan = QLineEdit()
        self.input_mat_khau = QLineEdit()
        self.input_phan_quyen = QComboBox()  # Dùng QComboBox để chọn phân quyền
        self.input_phan_quyen.addItems(["Quản lý", "Nhân viên bán hàng"])  # Các lựa chọn phân quyền

        self.form_layout.addRow("Họ Tên:", self.input_ho_ten)
        self.form_layout.addRow("Tài Khoản:", self.input_tai_khoan)
        self.form_layout.addRow("Mật Khẩu:", self.input_mat_khau)
        self.form_layout.addRow("Phân Quyền:", self.input_phan_quyen)
        self.layout.addLayout(self.form_layout)

        # Nút thêm nhân viên
        self.button_them = QPushButton("Đăng ký nhân viên")
        self.button_them.clicked.connect(self.xu_ly_them_nhan_vien)
        self.layout.addWidget(self.button_them)

        # Bảng danh sách nhân viên
        self.bang = QTableWidget(self)
        self.bang.setColumnCount(5)
        self.bang.setHorizontalHeaderLabels(["Mã NV", "Họ Tên", "Tài Khoản", "Mật Khẩu", "Phân Quyền"])
        self.layout.addWidget(self.bang)

        # Nút cập nhật
        self.button_cap_nhat = QPushButton("Cập nhật thông tin nhân viên")
        self.button_cap_nhat.clicked.connect(self.xu_ly_cap_nhat_nhan_vien)
        self.layout.addWidget(self.button_cap_nhat)

        # Nút xóa nhân viên
        self.button_xoa = QPushButton("Xóa nhân viên")
        self.button_xoa.clicked.connect(self.xu_ly_xoa_nhan_vien)
        self.layout.addWidget(self.button_xoa)

        # Nút tìm kiếm nhân viên
        self.form_tim_kiem = QFormLayout()
        self.input_tim_kiem = QLineEdit()
        self.form_tim_kiem.addRow("Tìm kiếm nhân viên (Mã hoặc Tên):", self.input_tim_kiem)
        self.button_tim_kiem = QPushButton("Tìm kiếm")
        self.button_tim_kiem.clicked.connect(self.xu_ly_tim_kiem_nhan_vien)
        self.layout.addLayout(self.form_tim_kiem)
        self.layout.addWidget(self.button_tim_kiem)

        self.setLayout(self.layout)
        self.hien_thi_danh_sach_nhan_vien()

    def hien_thi_danh_sach_nhan_vien(self):
        self.bang.clearContents()
        nhan_vien = danh_sach_nhan_vien()
        print(f"Danh sách nhân viên: {nhan_vien}")  # Debug để kiểm tra dữ liệu
        self.bang.setRowCount(len(nhan_vien))

        for row, nv in enumerate(nhan_vien):
            for col, data in enumerate(nv):
                self.bang.setItem(row, col, QTableWidgetItem(str(data)))
        self.bang.resizeColumnsToContents()

    def xu_ly_them_nhan_vien(self):
        ho_ten = self.input_ho_ten.text()
        tai_khoan = self.input_tai_khoan.text()
        mat_khau = self.input_mat_khau.text()
        phan_quyen = self.input_phan_quyen.currentText()  # Lấy phân quyền từ ComboBox

        if not ho_ten or not tai_khoan or not mat_khau or not phan_quyen:
            QMessageBox.warning(self, "Lỗi", "Vui lòng nhập đầy đủ thông tin!")
            return

        conn = ket_noi_db()
        if not conn:
            return
        cursor = conn.cursor()  # Sử dụng cursor của pymysql
        query = "INSERT INTO nhanvien (HoTen, TaiKhoan, MatKhau, PhanQuyen) VALUES (%s, %s, %s, %s)"
        cursor.execute(query, (ho_ten, tai_khoan, mat_khau, phan_quyen))
        conn.commit()
        conn.close()
        self.hien_thi_danh_sach_nhan_vien()

    def xu_ly_cap_nhat_nhan_vien(self):
        selected_items = self.bang.selectedItems()
        if selected_items:
            ma_nhan_vien = selected_items[0].text()
            ho_ten = self.input_ho_ten.text()
            tai_khoan = self.input_tai_khoan.text()
            mat_khau = self.input_mat_khau.text()
            phan_quyen = self.input_phan_quyen.currentText()  # Lấy phân quyền từ ComboBox

            conn = ket_noi_db()
            if not conn:
                return
            cursor = conn.cursor()  # Sử dụng cursor của pymysql
            query = "UPDATE nhanvien SET HoTen=%s, TaiKhoan=%s, MatKhau=%s, PhanQuyen=%s WHERE MaNhanVien=%s"
            cursor.execute(query, (ho_ten, tai_khoan, mat_khau, phan_quyen, ma_nhan_vien))
            conn.commit()
            conn.close()
            self.hien_thi_danh_sach_nhan_vien()

    def xu_ly_xoa_nhan_vien(self):
        selected_items = self.bang.selectedItems()
        if selected_items:
            ma_nhan_vien = selected_items[0].text()

            confirmation = QMessageBox.question(
                self, "Xác nhận xóa", "Bạn có chắc chắn muốn xóa nhân viên này?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, 
                QMessageBox.StandardButton.No
            )
            
            if confirmation == QMessageBox.StandardButton.Yes:
                conn = ket_noi_db()
                if not conn:
                    return
                cursor = conn.cursor()  # Sử dụng cursor của pymysql
                query = "DELETE FROM nhanvien WHERE MaNhanVien=%s"
                cursor.execute(query, (ma_nhan_vien,))
                conn.commit()
                conn.close()
                self.hien_thi_danh_sach_nhan_vien()

    def xu_ly_tim_kiem_nhan_vien(self):
        tim_kiem = self.input_tim_kiem.text()
        if not tim_kiem:
            QMessageBox.warning(self, "Lỗi", "Vui lòng nhập mã nhân viên hoặc tên để tìm kiếm!")
            return

        conn = ket_noi_db()
        if not conn:
            return
        cursor = conn.cursor()  # Sử dụng cursor của pymysql
        query = "SELECT * FROM nhanvien WHERE MaNhanVien LIKE %s OR HoTen LIKE %s"
        cursor.execute(query, (f"%{tim_kiem}%", f"%{tim_kiem}%"))
        result = cursor.fetchall()
        conn.close()

        if result:
            self.bang.clearContents()
            self.bang.setRowCount(len(result))

            for row, nv in enumerate(result):
                for col, data in enumerate(nv):
                    self.bang.setItem(row, col, QTableWidgetItem(str(data)))
            self.bang.resizeColumnsToContents()
        else:
            QMessageBox.information(self, "Thông báo", "Không tìm thấy nhân viên nào!")

# ====== CHẠY ỨNG DỤNG ======
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = QuanLyNhanVien()
    window.show()
    sys.exit(app.exec())
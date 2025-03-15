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
            user="root",
            password="",
            database="cua_hang_thu_cung",
            cursorclass=pymysql.cursors.DictCursor
        )
        return conn
    except pymysql.MySQLError as err:
        QMessageBox.critical(None, "Lỗi CSDL", f"Không thể kết nối: {err}")
        return None

# ====== CHỨC NĂNG QUẢN LÝ SẢN PHẨM ======
def danh_sach_san_pham():
    conn = ket_noi_db()
    if not conn:
        return []
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM sanpham")
    result = cursor.fetchall()
    conn.close()
    return result

class QuanLySanPham(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Quản lý Sản Phẩm")
        self.setGeometry(100, 100, 700, 500)

        self.layout = QVBoxLayout()

        # Form nhập dữ liệu
        self.form_layout = QFormLayout()
        self.input_ten = QLineEdit()
        self.input_danh_muc = QLineEdit()
        self.input_gia = QLineEdit()
        self.input_so_luong = QLineEdit()
        self.input_mo_ta = QLineEdit()

        self.form_layout.addRow("Tên sản phẩm:", self.input_ten)
        self.form_layout.addRow("Danh mục:", self.input_danh_muc)
        self.form_layout.addRow("Giá:", self.input_gia)
        self.form_layout.addRow("Số lượng:", self.input_so_luong)
        self.form_layout.addRow("Mô tả:", self.input_mo_ta)
        self.layout.addLayout(self.form_layout)

        # Nút thêm sản phẩm
        self.button_them = QPushButton("Thêm sản phẩm")
        self.button_them.clicked.connect(self.xu_ly_them_san_pham)
        self.layout.addWidget(self.button_them)

        # Bảng danh sách sản phẩm
        self.bang = QTableWidget(self)
        self.bang.setColumnCount(6)
        self.bang.setHorizontalHeaderLabels(["Mã SP", "Tên", "Danh mục", "Giá", "Số lượng", "Mô tả"])
        self.layout.addWidget(self.bang)

        # Nút cập nhật
        self.button_cap_nhat = QPushButton("Cập nhật sản phẩm")
        self.button_cap_nhat.clicked.connect(self.xu_ly_cap_nhat_san_pham)
        self.layout.addWidget(self.button_cap_nhat)

        # Nút xóa sản phẩm
        self.button_xoa = QPushButton("Xóa sản phẩm")
        self.button_xoa.clicked.connect(self.xu_ly_xoa_san_pham)
        self.layout.addWidget(self.button_xoa)

        self.setLayout(self.layout)
        self.hien_thi_danh_sach_san_pham()

    def hien_thi_danh_sach_san_pham(self):
        self.bang.clearContents()
        san_pham = danh_sach_san_pham()
        self.bang.setRowCount(len(san_pham))

        for row, sp in enumerate(san_pham):
            for col, key in enumerate(["MaSanPham", "Ten", "DanhMuc", "Gia", "SoLuongTonKho", "MoTa"]):
                self.bang.setItem(row, col, QTableWidgetItem(str(sp[key])))
        self.bang.resizeColumnsToContents()

    def xu_ly_them_san_pham(self):
        ten = self.input_ten.text()
        danh_muc = self.input_danh_muc.text()
        gia = self.input_gia.text()
        so_luong = self.input_so_luong.text()
        mo_ta = self.input_mo_ta.text()
        
        if not ten or not danh_muc or not gia or not so_luong:
            QMessageBox.warning(self, "Lỗi", "Vui lòng nhập đầy đủ thông tin!")
            return

        conn = ket_noi_db()
        if not conn:
            return
        cursor = conn.cursor()
        query = "INSERT INTO sanpham (Ten, DanhMuc, Gia, SoLuongTonKho, MoTa) VALUES (%s, %s, %s, %s, %s)"
        cursor.execute(query, (ten, danh_muc, gia, so_luong, mo_ta))
        conn.commit()
        conn.close()
        self.hien_thi_danh_sach_san_pham()

    def xu_ly_cap_nhat_san_pham(self):
        selected_items = self.bang.selectedItems()
        if selected_items:
            ma_san_pham = selected_items[0].text()
            ten = self.input_ten.text()
            danh_muc = self.input_danh_muc.text()
            gia = self.input_gia.text()
            so_luong = self.input_so_luong.text()
            mo_ta = self.input_mo_ta.text()
            
            conn = ket_noi_db()
            if not conn:
                return
            cursor = conn.cursor()
            query = "UPDATE sanpham SET Ten=%s, DanhMuc=%s, Gia=%s, SoLuongTonKho=%s, MoTa=%s WHERE MaSanPham=%s"
            cursor.execute(query, (ten, danh_muc, gia, so_luong, mo_ta, ma_san_pham))
            conn.commit()
            conn.close()
            self.hien_thi_danh_sach_san_pham()

    def xu_ly_xoa_san_pham(self):
        selected_items = self.bang.selectedItems()
        if selected_items:
            ma_san_pham = selected_items[0].text()
            confirmation = QMessageBox.question(
                self, "Xác nhận xóa", "Bạn có chắc chắn muốn xóa sản phẩm này?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, 
                QMessageBox.StandardButton.No
            )
            
            if confirmation == QMessageBox.StandardButton.Yes:
                conn = ket_noi_db()
                if not conn:
                    return
                cursor = conn.cursor()
                query = "DELETE FROM sanpham WHERE MaSanPham=%s"
                cursor.execute(query, (ma_san_pham,))
                conn.commit()
                conn.close()
                self.hien_thi_danh_sach_san_pham()

# ====== CHẠY ỨNG DỤNG ======
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = QuanLySanPham()
    window.show()
    sys.exit(app.exec())

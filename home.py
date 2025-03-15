import sys
from PyQt6 import QtWidgets, uic
from PyQt6.QtWidgets import QWidget, QMessageBox
from PyQt6.QtCore import Qt
# from product import ProductApp
from hoadon import OrderManagement  # ✅ Import giao diện Quản lý Sản phẩm
from themdonhang import AddOrderForm
from baocaothongke import BaoCaoThongKeWidget  # ✅ Import giao diện Báo cáo thống kê
from config import connect_db 
from qlkhachhang_1 import QuanLyKhachHang
from QuanLyThuCung import QuanLyThuCung
from qlsanpham import QuanLySanPham
from qlnhanvien import QuanLyNhanVien # Import giao diện thêm đơn hàng

class MainWindow(QWidget):
    def __init__(self, username, chuc_vu):
        super().__init__()
        uic.loadUi("views/trangchu1.ui", self)

        # Hiển thị thông tin người dùng
        self.username = username
        self.chuc_vu = chuc_vu.lower()  # Chuyển về chữ thường để kiểm tra dễ dàng
        self.userName.setText(f"Người dùng: {self.username}")
        self.Role.setText(f"Chức vụ: {self.chuc_vu.capitalize()}")

        # Quản lý trang hiển thị
        self.trangHienTai = None
        self.danhSachTrang = {}

        # Ẩn/hiện các nút dựa trên quyền hạn
        self.setup_permissions()

        # Kết nối sự kiện các nút
        self.thietLapKetNoi()

        # Hiển thị trang chủ mặc định
        self.hienThiTrangChu()

    def setup_permissions(self):
        """Cấu hình hiển thị các nút dựa trên quyền hạn của người dùng"""
        if self.chuc_vu == "quản lý" or self.chuc_vu == "admin":
            # Hiển thị tất cả các nút cho admin/quản lý
            self.btnProductManagement.setVisible(True)
            self.btnInvoiceManagement.setVisible(True)
            self.btnCustomerManagement.setVisible(True)
            self.btnAddOrder.setVisible(True)
            self.btnReportManagement.setVisible(True)
            self.btnEmployeeManagement.setVisible(True)
            self.btnPetManagement.setVisible(True) # Giả định có nút này
        else:  # Nhân viên
            self.btnProductManagement.setVisible(False)
            self.btnInvoiceManagement.setVisible(False)
            self.btnCustomerManagement.setVisible(True)
            self.btnReportManagement.setVisible(False)
            self.btnPetManagement.setVisible(False)
            self.btnEmployeeManagement.setVisible(False) # Ẩn nút báo cáo nếu có
            self.btnAddOrder.setVisible(True)

    def thietLapKetNoi(self):
        """Kết nối các nút với chức năng tương ứng"""
        if self.chuc_vu == "quản lý" or self.chuc_vu == "admin":
            self.btnProductManagement.clicked.connect(lambda: self.hienThiTrang("sanPham"))
            self.btnInvoiceManagement.clicked.connect(lambda: self.hienThiTrang("hoaDon"))
            self.btnReportManagement.clicked.connect(lambda: self.hienThiTrang("baoCao"))
            self.btnPetManagement.clicked.connect(lambda: self.hienThiTrang("thuCung"))
            self.btnEmployeeManagement.clicked.connect(lambda: self.hienThiTrang("nhanVien"))
        self.btnAddOrder.clicked.connect(lambda: self.open_add_order_form())
        self.btnCustomerManagement.clicked.connect(lambda: self.hienThiTrang("khachHang"))
        self.logoutButton.clicked.connect(self.dangXuat)

    def hienThiTrangChu(self):
        """Hiển thị giao diện trang chủ"""
        self.mainContent.setCurrentIndex(0)
        self.trangHienTai = "trangChu"

    def hienThiTrang(self, tenTrang):
        """Chuyển đổi hiển thị giữa các trang"""
        if tenTrang not in self.danhSachTrang:
            if tenTrang == "sanPham":
                self.danhSachTrang[tenTrang] = QuanLySanPham()
            elif tenTrang == "hoaDon":
                self.danhSachTrang[tenTrang] = OrderManagement()
            elif tenTrang == "baoCao":
                self.danhSachTrang[tenTrang] = BaoCaoThongKeWidget()
            elif tenTrang == "khachHang":
                self.danhSachTrang[tenTrang] = QuanLyKhachHang()
            elif tenTrang == "thuCung":
                self.danhSachTrang[tenTrang] = QuanLyThuCung()
            elif tenTrang == "nhanVien":
                self.danhSachTrang[tenTrang] = QuanLyNhanVien()

            # Thêm trang vào `mainContent`
            self.mainContent.addWidget(self.danhSachTrang[tenTrang])
        
        if tenTrang == "sanPham":
            self.danhSachTrang[tenTrang].hien_thi_danh_sach_san_pham()  # Gọi hàm tải lại sản phẩm
        elif tenTrang == "hoaDon":
            self.danhSachTrang[tenTrang].load_orders()
        elif tenTrang == "khachHang":
            self.danhSachTrang[tenTrang].hien_thi_danh_sach_khach_hang() 
        elif tenTrang == "nhanVien":
            self.danhSachTrang[tenTrang].hien_thi_danh_sach_nhan_vien()

        # Chuyển đến trang đã chọn (chỉ cho admin/quản lý)
        if self.chuc_vu == "quản lý" or self.chuc_vu == "admin" or tenTrang == "trangChu" or tenTrang == "khachHang":
            self.mainContent.setCurrentWidget(self.danhSachTrang.get(tenTrang, None))
            self.trangHienTai = tenTrang

    def open_add_order_form(self):
        """Mở form thêm đơn hàng và truyền thông tin nhân viên"""
        # Lấy MaNhanVien từ username (giả định username là TaiKhoan trong bảng nhanvien)
        ma_nhan_vien = self.get_ma_nhan_vien_from_username(self.username)
        if ma_nhan_vien:
            order_form = AddOrderForm(self, ma_nhan_vien)
            order_form.exec()
        else:
            QMessageBox.warning(self, "Lỗi", "Không thể xác định mã nhân viên từ username!")

    def get_ma_nhan_vien_from_username(self, username):
        """Lấy MaNhanVien từ username (giả định username là TaiKhoan trong bảng nhanvien)"""
        conn = connect_db()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute("SELECT MaNhanVien FROM nhanvien WHERE TaiKhoan = %s", (username,))
                result = cursor.fetchone()
                conn.close()
                return result[0] if result else None
            except Exception as e:
                print(f"Lỗi: {str(e)}")
                conn.close()
                return None
        return None

    def dangXuat(self):
        """Xử lý đăng xuất và quay về giao diện đăng nhập"""
        from dangnhap import LoginWindow
        self.cuaSoDangNhap = LoginWindow()
        self.cuaSoDangNhap.show()
        self.close()

def main():
    """Chạy ứng dụng"""
    try:
        app = QtWidgets.QApplication(sys.argv)
        # Ví dụ: Đăng nhập với username "admin" (Quản lý) hoặc "nvc" (Nhân viên)
        cuaSo = MainWindow("admin", "Admin")  # Hoặc MainWindow("nvc", "nhan vien")
        cuaSo.show()
        sys.exit(app.exec())
    except Exception as e:
        print(f"Lỗi: {str(e)}")

if __name__ == "__main__":
    main()
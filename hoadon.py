import sys
import os
from PyQt6 import QtWidgets, uic
from PyQt6.QtWidgets import QApplication, QWidget, QMessageBox, QTableWidgetItem
from PyQt6.QtCore import Qt
from suahoadon import EditInvoiceDialog
from config import connect_db  # Import hàm connect_db từ file config

class OrderManagement(QWidget):
    def __init__(self):
        super().__init__()

        # Load UI file từ thư mục hiện tại
        uic.loadUi('views/hoadon1.ui', self)

        # Cấu hình bảng
        self.setup_order_table()
        self.setup_detail_table()

        # Kết nối các sự kiện
        self.addButton.clicked.connect(self.add_order)
        self.editButton.clicked.connect(self.show_edit_dialog)
        self.deleteButton.clicked.connect(self.delete_order)
        self.searchButton.clicked.connect(self.search_orders)
        self.orderTable.itemClicked.connect(self.show_order_details)
        self.refreshButton.clicked.connect(self.load_orders)

        # Kết nối tới cơ sở dữ liệu
        self.db = connect_db()
        self.cursor = self.db.cursor() if self.db else None

        # Load dữ liệu ban đầu
        self.load_orders()

    def setup_order_table(self):
        """Cấu hình bảng thông tin hóa đơn"""
        headers = ["Mã hóa đơn", "Mã Khách Hàng", "Ngày Lập", "Tổng Tiền"]
        self.orderTable.setColumnCount(len(headers))
        self.orderTable.setHorizontalHeaderLabels(headers)
        self.orderTable.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers)  # Không cho chỉnh sửa trực tiếp

    def setup_detail_table(self):
        """Cấu hình bảng chi tiết hóa đơn"""
        headers = ["Mã Chi Tiết", "Mã Hóa đơn", "Mã Thú Cưng", "Mã Sản phẩm", "Số lượng", "Giá"]
        self.orderDetailTable.setColumnCount(len(headers))
        self.orderDetailTable.setHorizontalHeaderLabels(headers)
        self.orderDetailTable.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers)  # Không cho chỉnh sửa trực tiếp

    def load_orders(self):
        if not self.db or self.db.close:  # Kiểm tra kết nối có mở không
            self.db = connect_db()
            if not self.db:
                QMessageBox.critical(self, "Lỗi", "Không thể kết nối đến cơ sở dữ liệu!")
                return
            self.cursor = self.db.cursor()
        
        try:
            self.cursor.execute("""
                SELECT h.MaHoaDon, h.MaKhachHang, h.NgayLap, COALESCE(SUM(c.SoLuong * c.Gia), 0) AS TongTien
                FROM HoaDon h
                LEFT JOIN ChiTietHoaDon c ON h.MaHoaDon = c.MaHoaDon
                GROUP BY h.MaHoaDon, h.MaKhachHang, h.NgayLap
                ORDER BY h.MaHoaDon;
            """)
            orders = self.cursor.fetchall()
            print("Số hóa đơn:", len(orders))  # Debug: kiểm tra số lượng hóa đơn
            self.orderTable.setRowCount(len(orders))
            for row, order in enumerate(orders):
                for col, value in enumerate(order):
                    item = QTableWidgetItem(str(value) if value is not None else "")
                    if col == 3:  # Cột Tổng Tiền
                        item.setText(f"{value:,.0f} VNĐ" if value is not None else "0 VNĐ")
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    self.orderTable.setItem(row, col, item)
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Không thể tải danh sách hóa đơn: {str(e)}")

    def show_order_details(self, item):
        """Hiển thị chi tiết hóa đơn khi chọn một hàng trong bảng hóa đơn"""
        if not item or not isinstance(item, QTableWidgetItem):
            return

        mahoadon = item.text()
        if not self.db or not self.db.open:
            QMessageBox.critical(self, "Lỗi", "Không thể kết nối đến cơ sở dữ liệu!")
            return

        try:
            # Sử dụng LEFT JOIN để lấy thêm thông tin tên sản phẩm/thú cưng
            self.cursor.execute("""
            SELECT 
                ct.MaChiTiet, 
                ct.MaHoaDon,
                COALESCE(tc.Ten, '') as TenThuCung,
                COALESCE(sp.Ten, '') as TenSanPham,
                ct.SoLuong,
                ct.Gia,
                ct.SoLuong * ct.Gia as ThanhTien
            FROM chitiethoadon ct
            LEFT JOIN thucung tc ON ct.MaThuCung = tc.MaThuCung
            LEFT JOIN sanpham sp ON ct.MaSanPham = sp.MaSanPham
            WHERE ct.MaHoaDon = %s
            ORDER BY ct.MaChiTiet
            """, (mahoadon,))
            details = self.cursor.fetchall()

            # Cập nhật headers cho chi tiết
            headers = ["Mã Chi Tiết", "Mã Hóa Đơn", "Tên Thú Cưng", "Tên Sản Phẩm", 
                  "Số Lượng", "Đơn Giá", "Thành Tiền"]
            self.orderDetailTable.setHorizontalHeaderLabels(headers)

            self.orderDetailTable.setRowCount(len(details))
            for row, detail in enumerate(details):
                for col, value in enumerate(detail):
                    item = QTableWidgetItem(str(value) if value is not None else "")
                    if col in [5, 6]:  # Format giá và thành tiền
                        item.setText(f"{value:,.0f} VNĐ" if value else "0 VNĐ")
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    self.orderDetailTable.setItem(row, col, item)

        except Exception as e:
            print(f"Error: {str(e)}")
            QMessageBox.critical(self, "Lỗi", f"Không thể tải chi tiết hóa đơn: {str(e)}")

    def search_orders(self):
        """Tìm kiếm hóa đơn dựa trên MaHoaDon hoặc MaKhachHang"""
        search_text = self.searchBox.text().strip()
        if not search_text:
            self.load_orders()
            return

        if not self.db or not self.db.open:
            QMessageBox.critical(self, "Lỗi", "Không thể kết nối đến cơ sở dữ liệu!")
            return

        try:
            self.cursor.execute("""
                SELECT MaHoaDon, MaKhachHang, NgayLap, TongTien 
                FROM hoadon
                WHERE MaHoaDon LIKE %s OR MaKhachHang LIKE %s 
                ORDER BY MaHoaDon
            """, (f"%{search_text}%", f"%{search_text}%"))
            orders = self.cursor.fetchall()

            self.orderTable.setRowCount(len(orders))
            for row, order in enumerate(orders):
                for col, value in enumerate(order):
                    item = QTableWidgetItem(str(value) if value is not None else "")
                    if col == 3:  # Định format tổng tiền
                        item.setText(f"{value:,.0f} VNĐ" if value else "0 VNĐ")
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    self.orderTable.setItem(row, col, item)

            # Load chi tiết cho hóa đơn đầu tiên (nếu có)
            if orders:
                self.show_order_details(self.orderTable.item(0, 0))
            else:
                self.orderDetailTable.setRowCount(0)
        except Exception as e:
            print(f"Error: {str(e)}")
            QMessageBox.critical(self, "Lỗi", f"Không thể tìm kiếm hóa đơn: {str(e)}")

    def add_order(self):
        from themdonhang import AddOrderForm  # Ensure the import is correct
        order_form = AddOrderForm(self)  # Truyền self làm parent
        if order_form.exec() == QtWidgets.QDialog.DialogCode.Accepted:  # Kiểm tra kết quả dialog
            self.load_orders()

    def show_edit_dialog(self):
        selected_item = self.orderTable.currentItem()
        if not selected_item:
            QMessageBox.warning(self, "Cảnh báo", "Vui lòng chọn một hóa đơn để sửa!")
            return

        row = selected_item.row()
        invoice_data = {
            'MaHoaDon': self.orderTable.item(row, 0).text(),
            'MaKhachHang': self.orderTable.item(row, 1).text(),
            'NgayLap': self.orderTable.item(row, 2).text()
        }

        dialog = EditInvoiceDialog(self, invoice_data)
        if dialog.exec() == QtWidgets.QDialog.DialogCode.Accepted:
            self.load_orders()

            # Chọn lại hóa đơn đã chỉnh sửa
            mahoadon = invoice_data["MaHoaDon"]
            for i in range(self.orderTable.rowCount()):
                if self.orderTable.item(i, 0).text() == mahoadon:
                    self.orderTable.selectRow(i)
                    self.show_order_details(self.orderTable.item(i, 0))
                    break

    def delete_order(self):
        """Xóa hóa đơn và chi tiết liên quan"""
        selected_item = self.orderTable.currentItem()
        if not selected_item:
            QMessageBox.warning(self, "Cảnh báo", "Vui lòng chọn một hóa đơn để xóa!")
            return

        mahoadon = self.orderTable.item(selected_item.row(), 0).text()
        reply = QMessageBox.question(
            self, "Xác nhận", f"Bạn có chắc muốn xóa hóa đơn {mahoadon}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            if not self.db or not self.db.open:
                QMessageBox.critical(self, "Lỗi", "Không thể kết nối đến cơ sở dữ liệu!")
                return

            try:
                # Xóa chi tiết hóa đơn trước
                self.cursor.execute("DELETE FROM chitiethoadon WHERE MaHoaDon=%s", (mahoadon,))
                # Xóa hóa đơn
                self.cursor.execute("DELETE FROM hoadon WHERE MaHoaDon=%s", (mahoadon,))
                self.db.commit()
                QMessageBox.information(self, "Thành công", "Đã xóa hóa đơn thành công!")
                self.load_orders()
                self.orderDetailTable.setRowCount(0)  # Xóa chi tiết khi xóa hóa đơn
            except Exception as e:
                print(f"Error: {str(e)}")
                QMessageBox.critical(self, "Lỗi", f"Không thể xóa hóa đơn: {str(e)}")
                self.db.rollback()

    def update_total_amount(self, mahoadon):
        """Cập nhật tổng tiền hóa đơn dựa trên chi tiết"""
        if not self.db or not self.db.open:
            QMessageBox.critical(self, "Lỗi", "Không thể kết nối đến cơ sở dữ liệu!")
            return

        try:
            self.cursor.execute("""
            SELECT SUM(SoLuong * Gia) FROM chitiethoadon WHERE MaHoaDon=%s
            """, (mahoadon,))
            total = self.cursor.fetchone()[0] or 0
            self.cursor.execute("UPDATE hoadon SET TongTien=%s WHERE MaHoaDon=%s", (total, mahoadon))
            self.db.commit()
            self.load_orders()

            # Thêm dòng này để cập nhật bảng chi tiết
            item = self.orderTable.findItems(mahoadon, Qt.MatchFlag.MatchExactly)
            if item:
                self.show_order_details(item[0])

        except Exception as e:
            print(f"Error: {str(e)}")
            QMessageBox.critical(self, "Lỗi", f"Không thể cập nhật tổng tiền: {str(e)}")
            self.db.rollback()

    def closeEvent(self, event):
        """Đóng kết nối cơ sở dữ liệu khi đóng cửa sổ"""
        if hasattr(self, 'db') and self.db and self.db.open:
            self.db.close()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = OrderManagement()
    window.show()
    sys.exit(app.exec())
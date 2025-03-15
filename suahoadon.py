from PyQt6 import QtWidgets, uic
from PyQt6.QtWidgets import QDialog, QMessageBox, QTableWidgetItem, QInputDialog
from PyQt6.QtCore import Qt, QDate
from config import connect_db

class EditInvoiceDialog(QDialog):
    def __init__(self, parent=None, invoice_data=None):
        super().__init__(parent)
        uic.loadUi('views/suahoadon.ui', self)
        
        self.db = connect_db()
        self.cursor = self.db.cursor() if self.db else None
        self.invoice_data = invoice_data
        
        # Setup tables
        self.setup_product_table()
        self.setup_detail_table()
        
        # Connect signals
        self.categoryCombo.currentIndexChanged.connect(self.load_products)
        self.productTable.itemSelectionChanged.connect(self.check_stock)
        self.addToInvoiceButton.clicked.connect(self.add_to_invoice)
        self.saveButton.clicked.connect(self.save_changes)
        self.cancelButton.clicked.connect(self.reject)
        self.editDetailButton.clicked.connect(self.edit_detail)
        self.deleteDetailButton.clicked.connect(self.delete_detail)
        
        # Load data
        if invoice_data:
            self.load_invoice_data()
            self.load_detail_data()
            
        # Load initial products and employees
        self.load_products()
        self.load_employees()  # Thêm chức năng load danh sách nhân viên
        
        # Make invoice ID read-only
        self.invoiceId.setReadOnly(True)

        # Khởi tạo trạng thái ban đầu
        self.quantitySpinBox.setEnabled(False)
        self.addToInvoiceButton.setEnabled(False)

    def setup_product_table(self):
        """Cấu hình bảng sản phẩm/thú cưng"""
        self.product_headers = {
            "Thú cưng": ["Mã", "Tên", "Giá", "Số lượng"],
            "Sản phẩm": ["Mã", "Tên", "Giá", "Số lượng tồn kho"]
        }
        headers = self.product_headers["Thú cưng"]
        self.productTable.setColumnCount(len(headers))
        self.productTable.setHorizontalHeaderLabels(headers)
        self.productTable.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows)

    def setup_detail_table(self):
        """Cấu hình bảng chi tiết hóa đơn"""
        headers = ["Mã Chi Tiết", "Mã Hóa Đơn", "Mã Thú Cưng", "Mã Sản Phẩm", "Số Lượng", "Giá", "Thành Tiền"]
        self.detailTable.setColumnCount(len(headers))
        self.detailTable.setHorizontalHeaderLabels(headers)
        self.detailTable.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows)

    def load_invoice_data(self):
        """Load thông tin hóa đơn"""
        self.invoiceId.setText(self.invoice_data['MaHoaDon'])
        self.customerId.setText(self.invoice_data['MaKhachHang'])
        self.invoiceDate.setDate(QDate.fromString(self.invoice_data['NgayLap'], "yyyy-MM-dd"))
        if 'MaNhanVien' in self.invoice_data:  # Nếu hóa đơn có thông tin nhân viên
            self.employeeCombo.setCurrentText(str(self.invoice_data['MaNhanVien']) + " - " + 
                                            NhanVien.get_name(self.invoice_data['MaNhanVien']))

    def load_products(self):
        """Load danh sách sản phẩm hoặc thú cưng"""
        try:
            category = self.categoryCombo.currentText()
            headers = self.product_headers[category]
            self.productTable.setHorizontalHeaderLabels(headers)

            self.quantitySpinBox.setEnabled(False)
            self.addToInvoiceButton.setEnabled(False)

            if category == "Thú cưng":
                self.cursor.execute("""
                    SELECT MaThuCung, Ten, GiaBan, SoLuong 
                    FROM thucung 
                """)
            else:
                self.cursor.execute("""
                    SELECT MaSanPham, Ten, Gia, SoLuongTonKho 
                    FROM sanpham
                """)
            
            products = self.cursor.fetchall()
            self.productTable.setRowCount(len(products))
        
            for row, product in enumerate(products):
                for col, value in enumerate(product):
                    item = QTableWidgetItem(str(value))
                    if col == 2:  # Format price
                        item.setText(f"{value:,.0f} VNĐ")
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    self.productTable.setItem(row, col, item)
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Không thể tải danh sách: {str(e)}")

    def load_employees(self):
        """Load danh sách nhân viên vào combo box"""
        try:
            employees = NhanVien.get_all()
            self.employeeCombo.clear()  # Xóa các mục cũ
            for emp in employees:
                self.employeeCombo.addItem(f"{emp[0]} - {emp[1]}")  # Hiển thị "MaNhanVien - HoTen"
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Không thể tải danh sách nhân viên: {str(e)}")

    def check_stock(self):
        """Kiểm tra số lượng tồn kho khi chọn sản phẩm/thú cưng"""
        selected_row = self.productTable.currentRow()
        if selected_row < 0:
            self.quantitySpinBox.setEnabled(False)
            self.addToInvoiceButton.setEnabled(False)
            return

        soluong_ton = int(self.productTable.item(selected_row, 3).text())
        if soluong_ton > 0:
            self.quantitySpinBox.setEnabled(True)
            self.quantitySpinBox.setMaximum(soluong_ton)
            self.addToInvoiceButton.setEnabled(True)
        else:
            self.quantitySpinBox.setEnabled(False)
            self.addToInvoiceButton.setEnabled(False)
            QMessageBox.warning(self, "Cảnh báo", "Sản phẩm/thú cưng này đã hết hàng!")

    def load_detail_data(self):
        """Load chi tiết hóa đơn"""
        try:
            self.cursor.execute("""
                SELECT ct.MaChiTiet, ct.MaHoaDon, 
                       ct.MaThuCung, ct.MaSanPham, 
                       ct.SoLuong, ct.Gia,
                       ct.SoLuong * ct.Gia as ThanhTien
                FROM chitiethoadon ct
                WHERE ct.MaHoaDon = %s
            """, (self.invoice_data['MaHoaDon'],))
            
            details = self.cursor.fetchall()
            self.detailTable.setRowCount(len(details))
            
            for row, detail in enumerate(details):
                for col, value in enumerate(detail):
                    item = QTableWidgetItem(str(value) if value is not None else "")
                    if col in [5, 6]:  # Format price and total
                        item.setText(f"{value:,.0f} VNĐ")
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    self.detailTable.setItem(row, col, item)
            self.update_total_amount()
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Không thể tải chi tiết hóa đơn: {str(e)}")

    def add_to_invoice(self):
        """Thêm sản phẩm/thú cưng vào hóa đơn và cập nhật tồn kho"""
        selected_row = self.productTable.currentRow()
        if selected_row < 0:
            QMessageBox.warning(self, "Cảnh báo", "Vui lòng chọn một sản phẩm!")
            return
        
        try:
            category = self.categoryCombo.currentText()
            ma = self.productTable.item(selected_row, 0).text()
            gia = float(self.productTable.item(selected_row, 2).text().replace(' VNĐ', '').replace(',', ''))
            soluong_ton = int(self.productTable.item(selected_row, 3).text())
            soluong = self.quantitySpinBox.value()
        
            if soluong > soluong_ton:
                if category == "Thú cưng":
                    QMessageBox.warning(self, "Cảnh báo", f"{ma} không đủ tồn kho! Chỉ còn {soluong_ton} con.")
                else:
                    QMessageBox.warning(self, "Cảnh báo", f"{ma} không đủ tồn kho! Chỉ còn {soluong_ton} sản phẩm.")
                return
            
            if category == "Thú cưng":
                self.cursor.execute("""
                    INSERT INTO chitiethoadon (MaHoaDon, MaThuCung, SoLuong, Gia)
                    VALUES (%s, %s, %s, %s)
                """, (self.invoice_data['MaHoaDon'], ma, soluong, gia))
                self.cursor.execute("""
                    UPDATE thucung SET SoLuong = SoLuong - %s 
                    WHERE MaThuCung = %s
                """, (soluong, ma))
            else:
                self.cursor.execute("""
                    INSERT INTO chitiethoadon (MaHoaDon, MaSanPham, SoLuong, Gia)
                    VALUES (%s, %s, %s, %s)
                """, (self.invoice_data['MaHoaDon'], ma, soluong, gia))
                self.cursor.execute("""
                    UPDATE sanpham SET SoLuongTonKho = SoLuongTonKho - %s 
                    WHERE MaSanPham = %s
                """, (soluong, ma))
            
            self.db.commit()
            self.load_detail_data()
            self.load_products()
        except Exception as e:
            self.db.rollback()
            QMessageBox.critical(self, "Lỗi", f"Không thể thêm vào hóa đơn: {str(e)}")

    def edit_detail(self):
        """Sửa chi tiết hóa đơn và cập nhật tồn kho"""
        selected_row = self.detailTable.currentRow()
        if selected_row < 0:
            QMessageBox.warning(self, "Cảnh báo", "Vui lòng chọn một chi tiết để sửa!")
            return
            
        try:
            machitiet = self.detailTable.item(selected_row, 0).text()
            ma_thucung = self.detailTable.item(selected_row, 2).text() if self.detailTable.item(selected_row, 2) else None
            ma_sanpham = self.detailTable.item(selected_row, 3).text() if self.detailTable.item(selected_row, 3) else None
            soluong_cu = int(self.detailTable.item(selected_row, 4).text())
            
            soluong_moi, ok = QInputDialog.getInt(
                self, "Sửa số lượng", "Số lượng mới:",
                soluong_cu, 1, 100, 1
            )
            
            if ok and soluong_moi != soluong_cu:
                delta = soluong_moi - soluong_cu
                
                if ma_thucung:
                    self.cursor.execute("SELECT SoLuong FROM thucung WHERE MaThuCung = %s", (ma_thucung,))
                    soluong_ton = self.cursor.fetchone()[0]
                    if soluong_ton < delta:
                        raise Exception(f"{ma_thucung} không đủ tồn kho! Chỉ còn {soluong_ton} con.")
                    self.cursor.execute("""
                        UPDATE thucung SET SoLuong = SoLuong - %s 
                        WHERE MaThuCung = %s
                    """, (delta, ma_thucung))
                elif ma_sanpham:
                    self.cursor.execute("SELECT SoLuongTonKho FROM sanpham WHERE MaSanPham = %s", (ma_sanpham,))
                    soluong_ton = self.cursor.fetchone()[0]
                    if soluong_ton < delta:
                        raise Exception(f"{ma_sanpham} không đủ tồn kho! Chỉ còn {soluong_ton} sản phẩm.")
                    self.cursor.execute("""
                        UPDATE sanpham SET SoLuongTonKho = SoLuongTonKho - %s 
                        WHERE MaSanPham = %s
                    """, (delta, ma_sanpham))
                
                self.cursor.execute("""
                    UPDATE chitiethoadon 
                    SET SoLuong = %s
                    WHERE MaChiTiet = %s
                """, (soluong_moi, machitiet))
                
                self.db.commit()
                self.load_detail_data()
                self.load_products()
        except Exception as e:
            self.db.rollback()
            QMessageBox.critical(self, "Lỗi", f"Không thể sửa chi tiết: {str(e)}")

    def delete_detail(self):
        """Xóa chi tiết hóa đơn và hoàn lại tồn kho"""
        selected_row = self.detailTable.currentRow()
        if selected_row < 0:
            QMessageBox.warning(self, "Cảnh báo", "Vui lòng chọn một chi tiết để xóa!")
            return
            
        machitiet = self.detailTable.item(selected_row, 0).text()
        ma_thucung = self.detailTable.item(selected_row, 2).text() if self.detailTable.item(selected_row, 2) else None
        ma_sanpham = self.detailTable.item(selected_row, 3).text() if self.detailTable.item(selected_row, 3) else None
        soluong = int(self.detailTable.item(selected_row, 4).text())
        
        reply = QMessageBox.question(
            self, "Xác nhận", 
            "Bạn có chắc muốn xóa chi tiết này?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                if ma_thucung:
                    self.cursor.execute("""
                        UPDATE thucung SET SoLuong = SoLuong + %s 
                        WHERE MaThuCung = %s
                    """, (soluong, ma_thucung))
                elif ma_sanpham:
                    self.cursor.execute("""
                        UPDATE sanpham SET SoLuongTonKho = SoLuongTonKho + %s 
                        WHERE MaSanPham = %s
                    """, (soluong, ma_sanpham))
                
                self.cursor.execute("DELETE FROM chitiethoadon WHERE MaChiTiet = %s", (machitiet,))
                self.db.commit()
                self.load_detail_data()
                self.load_products()
            except Exception as e:
                self.db.rollback()
                QMessageBox.critical(self, "Lỗi", f"Không thể xóa chi tiết: {str(e)}")

    def validate_data(self):
        """Kiểm tra dữ liệu trước khi lưu"""
        if not self.customerId.text().strip():
            QMessageBox.warning(self, "Cảnh báo", "Vui lòng nhập mã khách hàng!")
            return False
            
        self.cursor.execute(
            "SELECT COUNT(*) FROM khachhang WHERE MaKhachHang = %s",
            (self.customerId.text().strip(),)
        )
        if self.cursor.fetchone()[0] == 0:
            QMessageBox.warning(self, "Cảnh báo", "Mã khách hàng không tồn tại!")
            return False
            
        # Kiểm tra mã nhân viên
        ma_nhan_vien = self.employeeCombo.currentText().split(" - ")[0] if self.employeeCombo.currentText() else None
        if not ma_nhan_vien:
            QMessageBox.warning(self, "Cảnh báo", "Vui lòng chọn mã nhân viên!")
            return False
            
        self.cursor.execute(
            "SELECT COUNT(*) FROM nhanvien WHERE MaNhanVien = %s",
            (ma_nhan_vien,)
        )
        if self.cursor.fetchone()[0] == 0:
            QMessageBox.warning(self, "Cảnh báo", "Mã nhân viên không tồn tại!")
            return False
            
        return True

    def save_changes(self):
        """Lưu thay đổi hóa đơn"""
        if not self.validate_data():
            return
            
        try:
            ma_nhan_vien = self.employeeCombo.currentText().split(" - ")[0]  # Lấy MaNhanVien từ combo box
            
            # Cập nhật thông tin hóa đơn
            self.cursor.execute("""
                UPDATE hoadon 
                SET MaKhachHang = %s, NgayLap = %s, MaNhanVien = %s
                WHERE MaHoaDon = %s
            """, (
                self.customerId.text().strip(),
                self.invoiceDate.date().toString("yyyy-MM-dd"),
                ma_nhan_vien,
                self.invoiceId.text().strip()
            ))
            
            # Cập nhật tổng tiền trong bảng hoadon
            self.cursor.execute("""
                UPDATE hoadon 
                SET TongTien = (SELECT SUM(SoLuong * Gia) FROM chitiethoadon WHERE MaHoaDon = %s)
                WHERE MaHoaDon = %s
            """, (self.invoiceId.text().strip(), self.invoiceId.text().strip()))
            
            self.db.commit()
            QMessageBox.information(self, "Thành công", "Đã cập nhật hóa đơn thành công!")
            self.accept()
        except Exception as e:
            self.db.rollback()
            QMessageBox.critical(self, "Lỗi", f"Không thể cập nhật hóa đơn: {str(e)}")

    def update_total_amount(self):
        """Cập nhật tổng tiền trên form"""
        try:
            self.cursor.execute("""
                SELECT SUM(SoLuong * Gia) 
                FROM chitiethoadon 
                WHERE MaHoaDon = %s
            """, (self.invoice_data['MaHoaDon'],))
        
            total = self.cursor.fetchone()[0] or 0
            self.totalAmount.setText(f"{total:,.0f} VNĐ")
        
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Không thể tính tổng tiền: {str(e)}")
    
    def closeEvent(self, event):
        """Xử lý sự kiện đóng cửa sổ"""
        if self.db and self.db.open:
            self.db.close()
        event.accept()

# Giả định lớp NhanVien trong models/nhanvien.py
class NhanVien:
    @staticmethod
    def get_all():
        db = connect_db()
        cursor = db.cursor()
        cursor.execute("SELECT MaNhanVien, HoTen FROM nhanvien ORDER BY MaNhanVien")
        employees = cursor.fetchall()
        db.close()
        return employees

    @staticmethod
    def get_name(ma_nhan_vien):
        db = connect_db()
        cursor = db.cursor()
        cursor.execute("SELECT HoTen FROM nhanvien WHERE MaNhanVien = %s", (ma_nhan_vien,))
        result = cursor.fetchone()
        db.close()
        return result[0] if result else "Không tìm thấy"
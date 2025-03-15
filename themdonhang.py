import sys
import os
from PyQt6.QtWidgets import QApplication, QDialog, QTableWidgetItem, QMessageBox
from PyQt6 import uic
from PyQt6.QtCore import Qt, QDate
import pymysql
from datetime import datetime
from config import connect_db

class AddOrderForm(QDialog):
    def __init__(self, parent=None, ma_nhan_vien=None):
        super().__init__(parent)
        self.parent_window = parent
        self.ma_nhan_vien = ma_nhan_vien  # Lưu mã nhân viên từ MainWindow
        uic.loadUi("views/themdonhang.ui", self)

        # Đặt ngày lập mặc định
        self.date_edit.setDate(QDate.currentDate())

        # Load dữ liệu khách hàng vào combo_khach
        self.load_khach_hang()

        # Cấu hình danh mục (Thú Cưng và Sản Phẩm)
        self.combo_danhmuc.addItem("Chọn loại sản phẩm")
        self.combo_danhmuc.addItem("Thú Cưng")
        self.combo_danhmuc.addItem("Sản Phẩm")

        # Kết nối tín hiệu
        self.combo_danhmuc.currentIndexChanged.connect(self.update_product_list)
        self.combo_sanpham.currentIndexChanged.connect(self.check_stock)  # Thêm tín hiệu kiểm tra tồn kho
        self.btn_add.clicked.connect(self.add_product)
        self.btn_save.clicked.connect(self.save_order)

        # Khởi tạo trạng thái ban đầu
        self.spin_sl.setEnabled(False)  # Vô hiệu hóa ô số lượng mặc định
        self.btn_add.setEnabled(False)  # Vô hiệu hóa nút thêm mặc định

    def load_khach_hang(self):
        """Tải danh sách khách hàng từ cơ sở dữ liệu vào combo_khach"""
        conn = connect_db()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute("SELECT MaKhachHang, HoTen FROM KhachHang")
                for makhach, tenkhach in cursor.fetchall():
                    self.combo_khach.addItem(f"{makhach} - {tenkhach}", makhach)
            except pymysql.Error as e:
                QMessageBox.critical(self, "Lỗi", f"Không thể tải danh sách khách hàng: {str(e)}")
            finally:
                cursor.close()
                conn.close()

    def update_product_list(self):
        """Cập nhật danh sách sản phẩm/thú cưng khi chọn danh mục"""
        self.combo_sanpham.clear()
        self.spin_sl.setEnabled(False)  # Vô hiệu hóa ô số lượng khi chưa chọn sản phẩm
        self.btn_add.setEnabled(False)  # Vô hiệu hóa nút thêm khi chưa chọn sản phẩm

        loai = self.combo_danhmuc.currentText()
        conn = connect_db()
        if conn:
            try:
                cursor = conn.cursor()

                if loai == "Thú Cưng":
                    cursor.execute("SELECT MaThuCung, Ten, GiaBan, SoLuong FROM ThuCung")
                    for mathucung, tenthucung, gia, soluong in cursor.fetchall():
                        self.combo_sanpham.addItem(
                            f"{mathucung} - {tenthucung} ({gia}đ, Tồn: {soluong})", (mathucung, gia, soluong)
                        )

                elif loai == "Sản Phẩm":
                    cursor.execute("SELECT MaSanPham, Ten, Gia, SoLuongTonKho FROM SanPham")
                    for masp, tensp, gia, soluongtonkho in cursor.fetchall():
                        self.combo_sanpham.addItem(
                            f"{masp} - {tensp} ({gia}đ, Tồn: {soluongtonkho})", (masp, gia, soluongtonkho)
                        )
            except pymysql.Error as e:
                QMessageBox.critical(self, "Lỗi", f"Không thể tải danh sách sản phẩm: {str(e)}")
            finally:
                cursor.close()
                conn.close()

    def check_stock(self):
        """Kiểm tra số lượng tồn kho khi chọn sản phẩm/thú cưng"""
        product_data = self.combo_sanpham.currentData()
        if not product_data:
            self.spin_sl.setEnabled(False)
            self.btn_add.setEnabled(False)
            return

        _, _, soluongton = product_data  # soluongton là SoLuong (Thú Cưng) hoặc SoLuongTonKho (Sản Phẩm)
        if soluongton > 0:
            self.spin_sl.setEnabled(True)
            self.spin_sl.setMaximum(soluongton)  # Giới hạn số lượng tối đa
            self.btn_add.setEnabled(True)
        else:
            self.spin_sl.setEnabled(False)
            self.btn_add.setEnabled(False)
            QMessageBox.warning(self, "Cảnh báo", "Sản phẩm/thú cưng này đã hết hàng!")

    def add_product(self):
        """Thêm thú cưng hoặc sản phẩm vào bảng"""
        loai = self.combo_danhmuc.currentText()
        product_data = self.combo_sanpham.currentData()
        soluong = self.spin_sl.value()

        if not product_data or loai == "Chọn loại sản phẩm":
            QMessageBox.warning(self, "Lỗi", "Vui lòng chọn loại sản phẩm và sản phẩm/thú cưng!")
            return

        ma, gia, soluongton = product_data
        if soluong > soluongton:
            QMessageBox.warning(self, "Lỗi", f"{ma} không đủ tồn kho! Chỉ còn {soluongton} đơn vị.")
            return

        self.add_to_table(ma, soluong, gia, loai)

    def add_to_table(self, ma, soluong, gia, loai):
        """Thêm vào bảng QTableWidget (table)"""
        row = self.table.rowCount()
        self.table.insertRow(row)
        self.table.setItem(row, 0, QTableWidgetItem(loai))  # Loại (Thú Cưng/Sản Phẩm)
        self.table.setItem(row, 1, QTableWidgetItem(str(ma)))  # Mã (MaThuCung/MaSanPham)
        self.table.setItem(row, 2, QTableWidgetItem(str(soluong)))  # Số lượng
        self.table.setItem(row, 3, QTableWidgetItem(f"{gia * soluong:,.0f} VNĐ"))  # Giá (thành tiền)
        self.update_total_price()

    def update_total_price(self):
        """Cập nhật tổng tiền"""
        total_price = 0
        for row in range(self.table.rowCount()):
            gia = float(self.table.item(row, 3).text().replace(" VNĐ", "").replace(",", ""))
            total_price += gia
        self.label_tong_tien_value.setText(f"{total_price:,.0f} VNĐ")

    def save_order(self):
        """Lưu hóa đơn và chi tiết vào database, đồng thời cập nhật số lượng tồn kho"""
        conn = connect_db()
        if not conn:
            QMessageBox.critical(self, "Lỗi", "Không thể kết nối đến cơ sở dữ liệu!")
            self.reject()
            return

        cursor = conn.cursor()
        makhach = self.combo_khach.currentData()
        ngaylap = self.date_edit.date().toString("yyyy-MM-dd")

    # Kiểm tra xem khách hàng đã được chọn chưa
        if not makhach:
            QMessageBox.critical(self, "Lỗi", "Vui lòng chọn khách hàng từ danh sách!")
            cursor.close()
            conn.close()
            self.reject()
            return

    # Kiểm tra xem MaKhachHang có tồn tại trong bảng KhachHang không
        cursor.execute("SELECT COUNT(*) FROM KhachHang WHERE MaKhachHang = %s", (makhach,))
        if cursor.fetchone()[0] == 0:
            QMessageBox.critical(self, "Lỗi", f"Mã khách hàng {makhach} không tồn tại trong hệ thống!")
            cursor.close()
            conn.close()
            self.reject()
            return

    # Kiểm tra xem có sản phẩm/thú cưng nào được thêm vào chưa
        if self.table.rowCount() == 0:
            QMessageBox.warning(self, "Lỗi", "Vui lòng thêm ít nhất một thú cưng hoặc sản phẩm vào hóa đơn!")
            cursor.close()
            conn.close()
            self.reject()
            return

        try:
        # 1. Tạo hóa đơn trước và lấy MaHoaDon, gán MaNhanVien từ self.ma_nhan_vien
            cursor.execute(
            "INSERT INTO HoaDon (MaKhachHang, NgayLap, TongTien, MaNhanVien) VALUES (%s, %s, %s, %s)",
                (makhach, ngaylap, 0, self.ma_nhan_vien)
            )
            conn.commit()
            cursor.execute("SELECT LAST_INSERT_ID()")
            mahoadon = cursor.fetchone()[0]

            tong_tien = 0
            for row in range(self.table.rowCount()):
                loai = self.table.item(row, 0).text()
                ma = self.table.item(row, 1).text()
                soluong = int(self.table.item(row, 2).text())
                gia = float(self.table.item(row, 3).text().replace(" VNĐ", "").replace(",", "")) / soluong

            # 2. Kiểm tra số lượng tồn kho trước khi thêm
                if loai == "Thú Cưng":
                    cursor.execute("SELECT SoLuong FROM ThuCung WHERE MaThuCung = %s", (ma,))
                else:  # Sản Phẩm
                    cursor.execute("SELECT SoLuongTonKho FROM SanPham WHERE MaSanPham = %s", (ma,))
            
                soluongton = cursor.fetchone()[0]
                if soluongton is None or soluong > soluongton:
                    raise Exception(
                        f"{ma} không đủ tồn kho! Chỉ còn {soluongton} {('con' if loai == 'Thú Cưng' else 'sản phẩm')}."
                    )

            # 3. Thêm vào ChiTietHoaDon
                ma_thucung = ma if loai == "Thú Cưng" else None
                ma_sanpham = ma if loai == "Sản Phẩm" else None
                cursor.execute(
                    "INSERT INTO ChiTietHoaDon (MaHoaDon, MaThuCung, MaSanPham, SoLuong, Gia) VALUES (%s, %s, %s, %s, %s)",
                    (mahoadon, ma_thucung, ma_sanpham, soluong, gia)
                )

            # 4. Cập nhật số lượng tồn kho
                if loai == "Thú Cưng":
                    cursor.execute(
                        "UPDATE ThuCung SET SoLuong = SoLuong - %s WHERE MaThuCung = %s",
                        (soluong, ma)
                    )
                else:  # Sản Phẩm
                    cursor.execute(
                        "UPDATE SanPham SET SoLuongTonKho = SoLuongTonKho - %s WHERE MaSanPham = %s",
                        (soluong, ma)
                    )

                tong_tien += soluong * gia

        # 5. Cập nhật tổng tiền của hóa đơn
            cursor.execute("UPDATE HoaDon SET TongTien = %s WHERE MaHoaDon = %s", (tong_tien, mahoadon))
            conn.commit()

        # 6. Thông báo thành công và đóng form
            QMessageBox.information(self, "Thành công", "Đơn hàng đã được lưu thành công!")
            self.accept()

        except pymysql.Error as e:
            QMessageBox.critical(self, "Lỗi", f"Lỗi khi lưu đơn hàng: {str(e)}")
            conn.rollback()
            self.reject()
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", str(e))
            conn.rollback()
            self.reject()
        finally:
            cursor.close()
            conn.close()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AddOrderForm()
    window.exec()
    sys.exit(app.exec())
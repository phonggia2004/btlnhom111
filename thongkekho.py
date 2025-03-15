from PyQt6 import QtWidgets, uic
from PyQt6.QtWidgets import QDialog, QMessageBox, QTableWidgetItem
from PyQt6.QtCore import Qt, QDate
from config import connect_db  # Giả định bạn đã có file config.py với hàm connect_db

# Lớp ThongKeKho để xử lý dữ liệu kho
class ThongKeKho:
    @staticmethod
    def get_inventory(filter_type=None, filter_date=None):
        """Lấy dữ liệu kho từ bảng thongkekho với bộ lọc"""
        db = connect_db()
        cursor = db.cursor()
        
        query = """
            SELECT Loai, Ten, SoLuong, MaThuCung, MaSanPham
            FROM thongkekho
            WHERE 1=1
        """
        params = []
        
        if filter_type and filter_type != "Tất cả":
            query += " AND Loai = %s"
            params.append(filter_type)
        
        if filter_date:
            query += " AND Ngay = %s"
            params.append(filter_date)
        
        query += " ORDER BY Loai, Ten"
        cursor.execute(query, params)
        
        inventory = cursor.fetchall()
        db.close()
        return inventory

    @staticmethod
    def save_inventory_report(ngay):
        """Lưu báo cáo kho vào bảng thongkekho dựa trên dữ liệu từ thucung và sanpham"""
        db = connect_db()
        cursor = db.cursor()
        
        try:
            # Xóa dữ liệu cũ cho ngày được chọn
            cursor.execute("DELETE FROM thongkekho WHERE Ngay = %s", (ngay,))
            
            # Lấy và lưu số lượng tồn kho của thú cưng từ bảng thucung
            cursor.execute("""
                SELECT 'Thú cưng' AS Loai, Ten, SoLuong, MaThuCung, NULL AS MaSanPham
                FROM thucung
                WHERE SoLuong > 0
            """)
            pets = cursor.fetchall()
            for pet in pets:
                cursor.execute("""
                    INSERT INTO thongkekho (Ngay, Loai, Ten, SoLuong, MaThuCung, MaSanPham)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (ngay, pet[0], pet[1], pet[2], pet[3], pet[4]))
            
            # Lấy và lưu số lượng tồn kho của sản phẩm từ bảng sanpham
            cursor.execute("""
                SELECT 'Sản phẩm' AS Loai, Ten, SoLuongTonKho AS SoLuong, NULL AS MaThuCung, MaSanPham
                FROM sanpham
                WHERE SoLuongTonKho > 0
            """)
            products = cursor.fetchall()
            for product in products:
                cursor.execute("""
                    INSERT INTO thongkekho (Ngay, Loai, Ten, SoLuong, MaThuCung, MaSanPham)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (ngay, product[0], product[1], product[2], product[3], product[4]))
            
            db.commit()
        except Exception as e:
            db.rollback()
            raise Exception(f"Lỗi khi lưu báo cáo kho: {str(e)}")
        finally:
            db.close()

# Lớp giao diện thống kê kho
class ThongKeKhoDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        uic.loadUi('views/tkkho1.ui', self)  # Tải file UI
        
        # Kết nối tín hiệu
        self.generateInventoryButton.clicked.connect(self.update_inventory)
        self.applyFilterButton.clicked.connect(self.apply_filter)
        
        # Khởi tạo giá trị mặc định cho bộ lọc
        self.filterTypeCombo.clear()  # Xóa các mục hiện tại để tránh trùng lặp
        self.filterTypeCombo.addItems(["Tất cả", "Thú cưng", "Sản phẩm"])
        
        today = QDate.currentDate()
        self.filterDateEdit.setDate(today)
        
        # Cấu hình bảng và tải báo cáo ban đầu
        self.setup_inventory_table()
        self.update_inventory()

    def setup_inventory_table(self):
        """Cấu hình bảng báo cáo kho"""
        headers = ["Loại", "Tên", "Số Lượng"]
        self.inventoryTable.setColumnCount(len(headers))
        self.inventoryTable.setHorizontalHeaderLabels(headers)
        self.inventoryTable.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows)
        self.inventoryTable.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.Stretch)

    def update_inventory(self):
        """Cập nhật báo cáo kho toàn bộ"""
        try:
            # Lấy ngày từ filterDateEdit để lưu báo cáo
            selected_date = self.filterDateEdit.date().toString("yyyy-MM-dd")
            
            # Lưu báo cáo kho vào cơ sở dữ liệu
            ThongKeKho.save_inventory_report(selected_date)
            
            # Lấy và hiển thị toàn bộ dữ liệu kho cho ngày đã chọn
            inventory = ThongKeKho.get_inventory(filter_date=selected_date)
            self.inventoryTable.setRowCount(len(inventory))
            
            for row, item in enumerate(inventory):
                for col, value in enumerate(item[:3]):  # Chỉ lấy Loai, Ten, SoLuong
                    table_item = QTableWidgetItem(str(value))
                    table_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    self.inventoryTable.setItem(row, col, table_item)
            
            # Hiển thị tổng số lượng tồn kho
            total_quantity = sum(item[2] for item in inventory)
            self.totalQuantityLabel.setText(f"Tổng số lượng tồn kho: {total_quantity}")
            
            QMessageBox.information(self, "Thành công", "Đã tạo báo cáo kho thành công!")
            
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Không thể tạo báo cáo kho: {str(e)}")

    def apply_filter(self):
        """Áp dụng bộ lọc theo loại và ngày"""
        try:
            filter_type = self.filterTypeCombo.currentText()
            filter_date = self.filterDateEdit.date().toString("yyyy-MM-dd")
            
            # Lấy dữ liệu kho theo bộ lọc
            inventory = ThongKeKho.get_inventory(filter_type, filter_date)
            self.inventoryTable.setRowCount(len(inventory))
            
            for row, item in enumerate(inventory):
                for col, value in enumerate(item[:3]):  # Chỉ lấy Loai, Ten, SoLuong
                    table_item = QTableWidgetItem(str(value))
                    table_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    self.inventoryTable.setItem(row, col, table_item)
            
            # Hiển thị tổng số lượng tồn kho theo bộ lọc
            total_quantity = sum(item[2] for item in inventory)
            self.totalQuantityLabel.setText(f"Tổng số lượng tồn kho: {total_quantity}")
            
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Không thể áp dụng bộ lọc: {str(e)}")

# Chạy ứng dụng
if __name__ == '__main__':
    app = QtWidgets.QApplication([])
    window = ThongKeKhoDialog()
    window.show()
    app.exec()
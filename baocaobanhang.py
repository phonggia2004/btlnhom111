from PyQt6 import QtWidgets, uic
from PyQt6.QtWidgets import QDialog, QMessageBox, QTableWidgetItem
from PyQt6.QtCore import Qt, QDate
from config import connect_db  # Sử dụng hàm connect_db từ file config.py

# Lớp BáoCaoBanHang để xử lý dữ liệu báo cáo bán hàng
class BaoCaoBanHang:
    @staticmethod
    def get_total_revenue(start_date=None, end_date=None):
        db = connect_db()
        cursor = db.cursor()
        query = "SELECT SUM(TongTien) FROM hoadon"
        params = []
        if start_date and end_date:
            query += " WHERE NgayLap BETWEEN %s AND %s"
            params = [start_date, end_date]
        cursor.execute(query, params)
        total = cursor.fetchone()[0] or 0
        db.close()
        return total

    @staticmethod
    def get_total_products_sold(start_date=None, end_date=None):
        db = connect_db()
        cursor = db.cursor()
        query = """
            SELECT SUM(SoLuong) 
            FROM chitiethoadon ct
            LEFT JOIN hoadon hd ON ct.MaHoaDon = hd.MaHoaDon
        """
        params = []
        if start_date and end_date:
            query += " WHERE hd.NgayLap BETWEEN %s AND %s"
            params = [start_date, end_date]
        cursor.execute(query, params)
        total = cursor.fetchone()[0] or 0
        db.close()
        return total

    @staticmethod
    def get_order_list(start_date=None, end_date=None):
        db = connect_db()
        cursor = db.cursor()
        query = """
            SELECT 
                hd.MaHoaDon, hd.NgayLap, kh.HoTen, 
                CASE 
                    WHEN ct.MaThuCung IS NOT NULL THEN tc.Ten
                    WHEN ct.MaSanPham IS NOT NULL THEN sp.Ten
                END AS SanPham,
                ct.SoLuong, ct.SoLuong * ct.Gia AS GiaTriDonHang
            FROM chitiethoadon ct
            LEFT JOIN hoadon hd ON ct.MaHoaDon = hd.MaHoaDon
            LEFT JOIN khachhang kh ON hd.MaKhachHang = kh.MaKhachHang
            LEFT JOIN thucung tc ON ct.MaThuCung = tc.MaThuCung
            LEFT JOIN sanpham sp ON ct.MaSanPham = sp.MaSanPham
        """
        params = []
        if start_date and end_date:
            query += " WHERE hd.NgayLap BETWEEN %s AND %s"
            params = [start_date, end_date]
        query += " ORDER BY hd.NgayLap DESC"
        cursor.execute(query, params)
        orders = cursor.fetchall()
        db.close()
        return orders

    @staticmethod
    def get_sales_by_product_type(start_date=None, end_date=None):
        db = connect_db()
        cursor = db.cursor()
        query = """
            SELECT 
                CASE 
                    WHEN ct.MaThuCung IS NOT NULL THEN 'Thú cưng'
                    WHEN ct.MaSanPham IS NOT NULL THEN sp.DanhMuc
                END AS LoaiMatHang,
                CASE 
                    WHEN ct.MaThuCung IS NOT NULL THEN tc.Ten
                    WHEN ct.MaSanPham IS NOT NULL THEN sp.Ten
                END AS Ten,
                SUM(ct.SoLuong) AS SoLuongBan, SUM(ct.SoLuong * ct.Gia) AS DoanhThu
            FROM chitiethoadon ct
            LEFT JOIN hoadon hd ON ct.MaHoaDon = hd.MaHoaDon
            LEFT JOIN thucung tc ON ct.MaThuCung = tc.MaThuCung
            LEFT JOIN sanpham sp ON ct.MaSanPham = sp.MaSanPham
        """
        params = []
        if start_date and end_date:
            query += " WHERE hd.NgayLap BETWEEN %s AND %s"
            params = [start_date, end_date]
        query += " GROUP BY LoaiMatHang, Ten ORDER BY DoanhThu DESC"
        cursor.execute(query, params)
        sales = cursor.fetchall()
        db.close()
        return sales

    @staticmethod
    def get_revenue_by_time_period(period, start_date=None, end_date=None):
        db = connect_db()
        cursor = db.cursor()
        if period == "Ngày":
            query = "SELECT NgayLap, SUM(TongTien) FROM hoadon GROUP BY NgayLap"
        elif period == "Tháng":
            query = "SELECT DATE_FORMAT(NgayLap, '%Y-%m') AS Thang, SUM(TongTien) FROM hoadon GROUP BY Thang"
        elif period == "Quý":
            query = "SELECT CONCAT(YEAR(NgayLap), '-Q', QUARTER(NgayLap)) AS Quy, SUM(TongTien) FROM hoadon GROUP BY Quy"
        elif period == "Năm":
            query = "SELECT YEAR(NgayLap) AS Nam, SUM(TongTien) FROM hoadon GROUP BY Nam"
        else:
            query = "SELECT NgayLap, SUM(TongTien) FROM hoadon GROUP BY NgayLap"
        
        params = []
        if start_date and end_date:
            query += " HAVING NgayLap BETWEEN %s AND %s"
            params = [start_date, end_date]
        cursor.execute(query, params)
        revenues = cursor.fetchall()
        db.close()
        return revenues

    @staticmethod
    def get_potential_customers(start_date=None, end_date=None):
        db = connect_db()
        cursor = db.cursor()
        query = """
            SELECT 
                kh.MaKhachHang, kh.HoTen, COUNT(hd.MaHoaDon) AS SoLanMua, SUM(hd.TongTien) AS TongGiaTri
            FROM khachhang kh
            LEFT JOIN hoadon hd ON kh.MaKhachHang = hd.MaKhachHang
        """
        params = []
        if start_date and end_date:
            query += " WHERE hd.NgayLap BETWEEN %s AND %s"
            params = [start_date, end_date]
        query += " GROUP BY kh.MaKhachHang, kh.HoTen ORDER BY SoLanMua DESC, TongGiaTri DESC"
        cursor.execute(query, params)
        customers = cursor.fetchall()
        db.close()
        return customers

    @staticmethod
    def get_employee_performance(start_date=None, end_date=None):
        db = connect_db()
        cursor = db.cursor()
        query = """
            SELECT 
                nv.MaNhanVien, nv.HoTen, COUNT(hd.MaHoaDon) AS SoDonHang, SUM(hd.TongTien) AS TongDoanhThu
            FROM nhanvien nv
            LEFT JOIN hoadon hd ON nv.MaNhanVien = hd.MaNhanVien
        """
        params = []
        if start_date and end_date:
            query += " WHERE hd.NgayLap BETWEEN %s AND %s"
            params = [start_date, end_date]
        query += " GROUP BY nv.MaNhanVien, nv.HoTen ORDER BY TongDoanhThu DESC"
        cursor.execute(query, params)
        employees = cursor.fetchall()
        db.close()
        return employees

# Lớp giao diện báo cáo bán hàng
class BaoCaoBanHangDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        uic.loadUi('views/baocaobanhang1.ui', self)
        
        # Kết nối tín hiệu
        self.generateTimeReportButton.clicked.connect(self.update_time_revenue)
        
        # Khởi tạo ngày mặc định cho bộ lọc thời gian
        today = QDate.currentDate()
        self.startDateEdit.setDate(today.addDays(-30))
        self.endDateEdit.setDate(today)
        
        # Tải báo cáo ban đầu
        self.update_all_reports()

    def setup_table(self, table, headers):
        table.setColumnCount(len(headers))
        table.setHorizontalHeaderLabels(headers)
        table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows)

    def update_all_reports(self):
        start_date = self.startDateEdit.date().toString("yyyy-MM-dd")
        end_date = self.endDateEdit.date().toString("yyyy-MM-dd")
        
        # Tổng quan
        total_revenue = BaoCaoBanHang.get_total_revenue(start_date, end_date)
        self.totalRevenueLabel.setText(f"Tổng doanh thu: {total_revenue:,.0f} VNĐ")
        total_products_sold = BaoCaoBanHang.get_total_products_sold(start_date, end_date)
        self.totalProductsSoldLabel.setText(f"Tổng số lượng sản phẩm bán ra: {total_products_sold}")
        
        # Danh sách đơn hàng
        orders = BaoCaoBanHang.get_order_list(start_date, end_date)
        self.setup_table(self.orderTable, ["Mã Đơn", "Ngày Bán", "Khách Hàng", "Sản Phẩm", "Số Lượng", "Giá Trị"])
        self.orderTable.setRowCount(len(orders))
        for row, order in enumerate(orders):
            for col, value in enumerate(order):
                item = QTableWidgetItem(str(value) if col < 4 else f"{value:,.0f} VNĐ" if col == 5 else str(value))
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.orderTable.setItem(row, col, item)
        
        # Doanh số theo loại sản phẩm
        sales = BaoCaoBanHang.get_sales_by_product_type(start_date, end_date)
        self.setup_table(self.productSalesTable, ["Loại Mặt Hàng", "Tên", "Số Lượng Bán", "Doanh Thu (VNĐ)"])
        self.productSalesTable.setRowCount(len(sales))
        for row, sale in enumerate(sales):
            for col, value in enumerate(sale):
                item = QTableWidgetItem(str(value) if col < 2 else str(value) if col == 2 else f"{value:,.0f} VNĐ")
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.productSalesTable.setItem(row, col, item)
        
        # Khách hàng tiềm năng
        customers = BaoCaoBanHang.get_potential_customers(start_date, end_date)
        self.setup_table(self.potentialCustomersTable, ["Mã Khách", "Tên", "Số Lần Mua", "Tổng Giá Trị (VNĐ)"])
        self.potentialCustomersTable.setRowCount(len(customers))
        for row, customer in enumerate(customers):
            for col, value in enumerate(customer):
                item = QTableWidgetItem(str(value) if col < 2 else str(value) if col == 2 else f"{value:,.0f} VNĐ")
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.potentialCustomersTable.setItem(row, col, item)
        
        # Hiệu suất nhân viên
        employees = BaoCaoBanHang.get_employee_performance(start_date, end_date)
        self.setup_table(self.employeePerformanceTable, ["Mã Nhân Viên", "Tên", "Số Đơn Hàng", "Tổng Doanh Thu (VNĐ)"])
        self.employeePerformanceTable.setRowCount(len(employees))
        for row, employee in enumerate(employees):
            for col, value in enumerate(employee):
                item = QTableWidgetItem(str(value) if col < 2 else str(value) if col == 2 else f"{value:,.0f} VNĐ")
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.employeePerformanceTable.setItem(row, col, item)

    def update_time_revenue(self):
        period = self.timePeriodCombo.currentText()
        start_date = self.startDateEdit.date().toString("yyyy-MM-dd")
        end_date = self.endDateEdit.date().toString("yyyy-MM-dd")
        
        revenues = BaoCaoBanHang.get_revenue_by_time_period(period, start_date, end_date)
        headers = ["Thời Gian", "Doanh Thu (VNĐ)"]
        self.setup_table(self.timeRevenueTable, headers)
        self.timeRevenueTable.setRowCount(len(revenues))
        for row, revenue in enumerate(revenues):
            for col, value in enumerate(revenue):
                item = QTableWidgetItem(str(value) if col == 0 else f"{value:,.0f} VNĐ")
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.timeRevenueTable.setItem(row, col, item)

# Chạy ứng dụng
if __name__ == '__main__':
    app = QtWidgets.QApplication([])
    window = BaoCaoBanHangDialog()
    window.show()
    app.exec()
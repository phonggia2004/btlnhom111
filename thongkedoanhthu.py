# import sys
# from PyQt6 import QtWidgets, uic
# from PyQt6.QtWidgets import QMainWindow, QMessageBox, QTableWidgetItem
# from PyQt6.QtCore import Qt, QDate
# import pymysql

# # Hàm kết nối cơ sở dữ liệu
# def connect_db():
#     try:
#         conn = pymysql.connect(
#             host="localhost",
#             user="root",         # Thay bằng user MySQL của bạn
#             password="",         # Thay bằng password MySQL của bạn
#             database="cua_hang_thu_cung"
#         )
#         return conn
#     except pymysql.MySQLError as err:
#         QMessageBox.critical(None, "Lỗi CSDL", f"Không thể kết nối: {err}")
#         return None

# # Lớp ThongKeDoanhThu để xử lý và hiển thị báo cáo tổng doanh thu
# class ThongKeDoanhThu(QMainWindow):
#     def __init__(self, parent=None):
#         super().__init__(parent)
#         uic.loadUi("views/tongdoanhthu.ui", self)
        
#         # Kiểm tra các thành phần UI
#         print("Kiểm tra UI:", 
#               hasattr(self, "startDateEdit"), 
#               hasattr(self, "endDateEdit"), 
#               hasattr(self, "generateReportButton"), 
#               hasattr(self, "totalRevenueLabel"), 
#               hasattr(self, "reportTable"))
        
#         # Kết nối tín hiệu
#         self.startDateEdit.dateChanged.connect(self.update_report)
#         self.endDateEdit.dateChanged.connect(self.update_report)
#         self.generateReportButton.clicked.connect(self.update_report)
#         self.generateReportButton.clicked.connect(lambda: print("Nút 'Tạo báo cáo' đã được nhấn!"))
        
#         # Khởi tạo ngày mặc định
#         today = QDate.currentDate()
#         self.startDateEdit.setDate(today.addDays(-30))  # Mặc định 30 ngày trước
#         self.endDateEdit.setDate(today)
        
#         # Tải báo cáo ban đầu
#         self.update_report()

#     def setup_report_table(self):
#         """Cấu hình bảng báo cáo doanh thu"""
#         headers = ["Loại", "Tên", "Khách hàng", "Doanh Thu (VNĐ)"]
#         self.reportTable.setColumnCount(len(headers))
#         self.reportTable.setHorizontalHeaderLabels(headers)
#         self.reportTable.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows)

#     def get_total_revenue(self, start_date, end_date):
#         """Lấy tổng doanh thu từ hoadon"""
#         db = connect_db()
#         if not db:
#             return 0
#         cursor = db.cursor()
#         cursor.execute("""
#             SELECT SUM(TongTien) 
#             FROM hoadon 
#             WHERE NgayLap BETWEEN %s AND %s
#         """, (start_date, end_date))
#         total = cursor.fetchone()[0] or 0
#         db.close()
#         return total

#     def get_revenue_details(self, start_date, end_date):
#         """Lấy chi tiết doanh thu theo sản phẩm/thú cưng và khách hàng"""
#         db = connect_db()
#         if not db:
#             return []
#         cursor = db.cursor()
#         cursor.execute("""
#             SELECT 
#                 CASE 
#                     WHEN ct.MaThuCung IS NOT NULL THEN 'Thú cưng'
#                     WHEN ct.MaSanPham IS NOT NULL THEN 'Sản phẩm'
#                 END AS Loai,
#                 CASE 
#                     WHEN ct.MaThuCung IS NOT NULL THEN tc.Ten
#                     WHEN ct.MaSanPham IS NOT NULL THEN sp.Ten
#                 END AS Ten,
#                 kh.HoTen AS KhachHang,
#                 SUM(ct.SoLuong * ct.Gia) AS DoanhThu
#             FROM chitiethoadon ct
#             LEFT JOIN thucung tc ON ct.MaThuCung = tc.MaThuCung
#             LEFT JOIN sanpham sp ON ct.MaSanPham = sp.MaSanPham
#             LEFT JOIN hoadon hd ON ct.MaHoaDon = hd.MaHoaDon
#             LEFT JOIN khachhang kh ON hd.MaKhachHang = kh.MaKhachHang
#             WHERE hd.NgayLap BETWEEN %s AND %s
#             AND ct.Gia > 0  -- Loại bỏ các bản ghi không hợp lệ
#             GROUP BY Loai, Ten, kh.HoTen
#             HAVING DoanhThu > 0  -- Loại bỏ các bản ghi với doanh thu 0 hoặc âm
#             ORDER BY DoanhThu DESC
#         """, (start_date, end_date))
#         details = cursor.fetchall()
#         db.close()
#         return details

#     def update_report(self):
#         """Cập nhật báo cáo doanh thu dựa trên khoảng thời gian"""
#         try:
#             start_date = self.startDateEdit.date().toString("yyyy-MM-dd")
#             end_date = self.endDateEdit.date().toString("yyyy-MM-dd")
            
#             # Debug: In ra khoảng thời gian để kiểm tra
#             print(f"Đang tạo báo cáo cho khoảng thời gian: {start_date} đến {end_date}")
            
#             # Lấy tổng doanh thu
#             total_revenue = self.get_total_revenue(start_date, end_date)
#             self.totalRevenueLabel.setText(f"Tổng doanh thu: {total_revenue:,.0f} VNĐ")
            
#             # Lấy chi tiết doanh thu
#             details = self.get_revenue_details(start_date, end_date)
#             self.setup_report_table()
#             self.reportTable.setRowCount(len(details))
            
#             for row, detail in enumerate(details):
#                 for col, value in enumerate(detail):
#                     item = QTableWidgetItem(str(value) if col < 3 else f"{value:,.0f} VNĐ")
#                     item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
#                     self.reportTable.setItem(row, col, item)
            
#         except Exception as e:
#             # In chi tiết lỗi để debug
#             print(f"Lỗi trong update_report: {str(e)}")
#             QMessageBox.critical(self, "Lỗi", f"Không thể tạo báo cáo: {str(e)}")

# # Chạy ứng dụng
# if __name__ == "__main__":
#     app = QtWidgets.QApplication(sys.argv)
    
#     # Tạo và hiển thị giao diện
#     window = ThongKeDoanhThu()
#     window.show()
    
#     sys.exit(app.exec())

import sys
from PyQt6 import QtWidgets, uic
from PyQt6.QtWidgets import QMainWindow, QMessageBox, QTableWidgetItem, QFileDialog
from PyQt6.QtCore import Qt, QDate
import pymysql
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet

# Hàm kết nối cơ sở dữ liệu
def connect_db():
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

# Lớp ThongKeDoanhThu để xử lý và hiển thị báo cáo tổng doanh thu
class ThongKeDoanhThu(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        uic.loadUi("views/tongdoanhthu.ui", self)
        
        # Kiểm tra các thành phần UI
        print("Kiểm tra UI:", 
              hasattr(self, "startDateEdit"), 
              hasattr(self, "endDateEdit"), 
              hasattr(self, "generateReportButton"), 
              hasattr(self, "totalRevenueLabel"), 
              hasattr(self, "reportTable"))
        
        # Kết nối tín hiệu
        self.startDateEdit.dateChanged.connect(self.update_report)
        self.endDateEdit.dateChanged.connect(self.update_report)
        self.generateReportButton.clicked.connect(self.update_report_and_export_pdf)
        self.generateReportButton.clicked.connect(lambda: print("Nút 'Tạo báo cáo' đã được nhấn!"))
        
        # Khởi tạo ngày mặc định
        today = QDate.currentDate()
        self.startDateEdit.setDate(today.addDays(-30))  # Mặc định 30 ngày trước
        self.endDateEdit.setDate(today)
        
        # Tải báo cáo ban đầu
        self.update_report()

    def setup_report_table(self):
        """Cấu hình bảng báo cáo doanh thu"""
        headers = ["Loại", "Tên", "Khách hàng", "Doanh Thu (VNĐ)"]
        self.reportTable.setColumnCount(len(headers))
        self.reportTable.setHorizontalHeaderLabels(headers)
        self.reportTable.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows)

    def get_total_revenue(self, start_date, end_date):
        """Lấy tổng doanh thu từ hoadon"""
        db = connect_db()
        if not db:
            return 0
        cursor = db.cursor()
        cursor.execute("""
            SELECT SUM(TongTien) 
            FROM hoadon 
            WHERE NgayLap BETWEEN %s AND %s
        """, (start_date, end_date))
        total = cursor.fetchone()[0] or 0
        db.close()
        return total

    def get_revenue_details(self, start_date, end_date):
        """Lấy chi tiết doanh thu theo sản phẩm/thú cưng và khách hàng"""
        db = connect_db()
        if not db:
            return []
        cursor = db.cursor()
        cursor.execute("""
            SELECT 
                CASE 
                    WHEN ct.MaThuCung IS NOT NULL THEN 'Thú cưng'
                    WHEN ct.MaSanPham IS NOT NULL THEN 'Sản phẩm'
                    ELSE 'Không xác định'  -- Giá trị mặc định nếu cả hai đều NULL
                END AS Loai,
                CASE 
                    WHEN ct.MaThuCung IS NOT NULL THEN tc.Ten
                    WHEN ct.MaSanPham IS NOT NULL THEN sp.Ten
                    ELSE 'Không xác định'
                END AS Ten,
                kh.HoTen AS KhachHang,
                SUM(ct.SoLuong * ct.Gia) AS DoanhThu
            FROM chitiethoadon ct
            LEFT JOIN thucung tc ON ct.MaThuCung = tc.MaThuCung
            LEFT JOIN sanpham sp ON ct.MaSanPham = sp.MaSanPham
            LEFT JOIN hoadon hd ON ct.MaHoaDon = hd.MaHoaDon
            LEFT JOIN khachhang kh ON hd.MaKhachHang = kh.MaKhachHang
            WHERE hd.NgayLap BETWEEN %s AND %s
            AND (ct.MaThuCung IS NOT NULL OR ct.MaSanPham IS NOT NULL)  -- Chỉ lấy bản ghi hợp lệ
            AND ct.Gia > 0  -- Loại bỏ các bản ghi không hợp lệ
            GROUP BY Loai, Ten, kh.HoTen
            HAVING DoanhThu > 0  -- Loại bỏ các bản ghi với doanh thu 0 hoặc âm
            ORDER BY DoanhThu DESC
        """, (start_date, end_date))
        details = cursor.fetchall()
        db.close()
        return details

    def export_to_pdf(self, start_date, end_date, total_revenue, details):
        """Xuất báo cáo doanh thu ra file PDF"""
        # Mở hộp thoại chọn vị trí lưu file PDF
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Lưu báo cáo doanh thu", f"BaoCaoDoanhThu_{start_date}_den_{end_date}.pdf", "PDF Files (*.pdf)"
        )
        
        if not file_path:
            return  # Người dùng hủy chọn file

        # Tạo tài liệu PDF
        doc = SimpleDocTemplate(file_path, pagesize=letter)
        elements = []

        # Lấy style mẫu
        styles = getSampleStyleSheet()
        normal_style = styles['Normal']

        # Tiêu đề báo cáo
        title = f"BÁO CÁO DOANH THU\nTừ {start_date} đến {end_date}"
        elements.append(Paragraph(title, styles['Heading1']))
        elements.append(Paragraph(f"Tổng doanh thu: {total_revenue:,.0f} VNĐ", normal_style))
        elements.append(Paragraph("<br/><br/>", normal_style))

        # Dữ liệu bảng
        data = [["Loại", "Tên", "Khách hàng", "Doanh Thu (VNĐ)"]]
        for detail in details:
            data.append([
                str(detail[0]),  # Loai
                str(detail[1]),  # Ten
                str(detail[2]) if detail[2] else "Không xác định",  # KhachHang
                f"{detail[3]:,.0f} VNĐ"  # DoanhThu
            ])

        # Tạo bảng trong PDF
        table = Table(data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ]))

        elements.append(table)
        doc.build(elements)
        QMessageBox.information(self, "Thành công", f"Báo cáo đã được xuất ra file: {file_path}")

    def update_report_and_export_pdf(self):
        """Cập nhật báo cáo doanh thu dựa trên khoảng thời gian và xuất ra PDF"""
        try:
            start_date = self.startDateEdit.date().toString("yyyy-MM-dd")
            end_date = self.endDateEdit.date().toString("yyyy-MM-dd")
            
            # Debug: In ra khoảng thời gian để kiểm tra
            print(f"Đang tạo báo cáo cho khoảng thời gian: {start_date} đến {end_date}")
            
            # Lấy tổng doanh thu
            total_revenue = self.get_total_revenue(start_date, end_date)
            self.totalRevenueLabel.setText(f"Tổng doanh thu: {total_revenue:,.0f} VNĐ")
            
            # Lấy chi tiết doanh thu
            details = self.get_revenue_details(start_date, end_date)
            self.setup_report_table()
            self.reportTable.setRowCount(len(details))
            
            for row, detail in enumerate(details):
                for col, value in enumerate(detail):  # Chỉ lấy 4 cột đầu (Loai, Ten, KhachHang, DoanhThu)
                    item = QTableWidgetItem(str(value) if col < 3 else f"{value:,.0f} VNĐ")
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    self.reportTable.setItem(row, col, item)
            
            # Xuất báo cáo ra PDF
            self.export_to_pdf(start_date, end_date, total_revenue, details)
        
        except Exception as e:
            # In chi tiết lỗi để debug
            print(f"Lỗi trong update_report_and_export_pdf: {str(e)}")
            QMessageBox.critical(self, "Lỗi", f"Không thể tạo hoặc xuất báo cáo: {str(e)}")
    def update_report(self):
        """Cập nhật báo cáo doanh thu dựa trên khoảng thời gian"""
        try:
            start_date = self.startDateEdit.date().toString("yyyy-MM-dd")
            end_date = self.endDateEdit.date().toString("yyyy-MM-dd")
            
            # Debug: In ra khoảng thời gian để kiểm tra
            print(f"Đang tạo báo cáo cho khoảng thời gian: {start_date} đến {end_date}")
            
            # Lấy tổng doanh thu
            total_revenue = self.get_total_revenue(start_date, end_date)
            self.totalRevenueLabel.setText(f"Tổng doanh thu: {total_revenue:,.0f} VNĐ")
            
            # Lấy chi tiết doanh thu
            details = self.get_revenue_details(start_date, end_date)
            self.setup_report_table()
            self.reportTable.setRowCount(len(details))
            
            for row, detail in enumerate(details):
                for col, value in enumerate(detail):
                    item = QTableWidgetItem(str(value) if col < 3 else f"{value:,.0f} VNĐ")
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    self.reportTable.setItem(row, col, item)
            
        except Exception as e:
            # In chi tiết lỗi để debug
            print(f"Lỗi trong update_report: {str(e)}")
            QMessageBox.critical(self, "Lỗi", f"Không thể tạo báo cáo: {str(e)}")


# Chạy ứng dụng
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    
    # Tạo và hiển thị giao diện
    window = ThongKeDoanhThu()
    window.show()
    
    sys.exit(app.exec())
from PyQt6 import QtWidgets, uic
from PyQt6.QtWidgets import QWidget
from thongkekho import ThongKeKhoDialog  # Giả định file thống kê kho
from thongkedoanhthu import ThongKeDoanhThu  # Giả định file thống kê doanh thu (tùy chỉnh tên file)
from baocaobanhang import BaoCaoBanHangDialog  # File báo cáo bán hàng

class BaoCaoThongKeWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        uic.loadUi("views/baocaothongke.ui", self)

        # Kết nối các nút với chức năng
        self.btnKhoReport.clicked.connect(self.show_kho_report)
        self.btnRevenueReport.clicked.connect(self.show_revenue_report)
        self.btnSalesReport.clicked.connect(self.show_sales_report)

    def show_kho_report(self):
        """Hiển thị báo cáo thống kê kho"""
        kho_dialog = ThongKeKhoDialog(self)
        kho_dialog.exec()

    def show_revenue_report(self):
        """Hiển thị báo cáo thống kê doanh thu"""
        revenue_dialog = ThongKeDoanhThu(self)  
        revenue_dialog.show()

    def show_sales_report(self):
        """Hiển thị báo cáo bán hàng"""
        sales_dialog = BaoCaoBanHangDialog(self)
        sales_dialog.exec()
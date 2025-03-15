from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLineEdit, QLabel,
    QMessageBox, QApplication, QGridLayout, QScrollArea, QGroupBox, QComboBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap
import pymysql
import requests

class AddPetWindow(QWidget):
    def __init__(self, parent, pet=None):
        super().__init__()
        self.parent = parent
        self.pet = pet
        self.setWindowTitle("Cập Nhật Thú Cưng" if pet else "Thêm Thú Cưng Mới")
        self.setGeometry(450, 200, 500, 700)
        self.setStyleSheet("background-color: #3E2723; color: white; font: 12pt 'Arial';")
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        self.inputs = {}
        fields = [
            ("Tên", "Ten"),
            ("Loại", "Loai"),
            ("Giống", "Giong"),
            ("Giới Tính", "GioiTinh"),
            ("Tuổi", "Tuoi"),
            ("Giá Bán", "GiaBan"),
            ("Số lương", "SoLuong"),
            ("Tình Trạng Sức Khỏe", "TinhTrangSucKhoe"),
            ("Link Ảnh", "image_link")
        ]

        for label_text, key in fields:
            label = QLabel(label_text + ":")
            layout.addWidget(label)
            if key == "GioiTinh":
                combo_box = QComboBox()
                combo_box.addItems(["Đực", "Cái"])
                if self.pet:
                    combo_box.setCurrentText(self.pet.get(key, ""))
                combo_box.setStyleSheet("padding: 8px; border-radius: 5px; border: 1px solid white;")
                self.inputs[key] = combo_box
                layout.addWidget(combo_box)
            else:
                input_field = QLineEdit()
                input_field.setStyleSheet("padding: 8px; border-radius: 5px; border: 1px solid white;")
                if self.pet:
                    input_field.setText(str(self.pet.get(key, "")))
                self.inputs[key] = input_field
                layout.addWidget(input_field)

        action_button = QPushButton("Cập Nhật" if self.pet else "Thêm")
        action_button.setStyleSheet("padding: 10px; background-color: #8BC34A; border: none; border-radius: 10px; color: white; font-weight: bold;")
        action_button.clicked.connect(self.update_pet if self.pet else self.add_pet)
        layout.addWidget(action_button)
        self.setLayout(layout)

    def connect_db(self):
        return pymysql.connect(
            host='localhost',
            user='root',
            password='',
            database='cua_hang_thu_cung',
            cursorclass=pymysql.cursors.DictCursor
        )

    def add_pet(self):
        pet_data = self.get_pet_data()
        try:
            connection = self.connect_db()
            with connection.cursor() as cursor:
                sql = """
                    INSERT INTO thucung (Ten, Loai, Giong, GioiTinh, Tuoi, GiaBan, SoLuong, TinhTrangSucKhoe, image_link)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                cursor.execute(sql, tuple(pet_data.values()))
                connection.commit()
            connection.close()
            QMessageBox.information(self, "Thành công", "Thêm thú cưng thành công!")
            self.parent.display_pets()
            self.close()
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Không thể thêm thú cưng: {e}")

    def update_pet(self):
        pet_data = self.get_pet_data()
        try:
            connection = self.connect_db()
            with connection.cursor() as cursor:
                sql = """
                    UPDATE thucung SET Ten=%s, Loai=%s, Giong=%s, GioiTinh=%s, Tuoi=%s, GiaBan=%s, SoLuong=%s, TinhTrangSucKhoe=%s, image_link=%s
                    WHERE MaThuCung=%s
                """
                cursor.execute(sql, tuple(pet_data.values()) + (self.pet['MaThuCung'],))
                connection.commit()
            connection.close()
            QMessageBox.information(self, "Thành công", "Cập nhật thông tin thú cưng thành công!")
            self.parent.display_pets()
            self.close()
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Không thể cập nhật thú cưng: {e}")

    def get_pet_data(self):
        return {key: (widget.currentText() if isinstance(widget, QComboBox) else widget.text())
                for key, widget in self.inputs.items()}

class QuanLyThuCung(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Quản Lý Thú Cưng")
        self.setGeometry(100, 100, 1000, 800)
        self.setStyleSheet("background-color: #5D4037; color: white; font: 12pt 'Arial';")
        self.layout = QVBoxLayout()
        self.create_search_add_section()
        self.grid_layout = QGridLayout()
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_content = QWidget()
        self.scroll_content.setLayout(self.grid_layout)
        self.scroll_area.setWidget(self.scroll_content)
        self.layout.addWidget(self.scroll_area)
        self.setLayout(self.layout)
        self.display_pets()

    def create_search_add_section(self):
        section_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Tìm kiếm theo tên...")
        self.search_input.setStyleSheet("padding: 8px; border-radius: 5px; border: 1px solid white;")
        section_layout.addWidget(self.search_input)

        search_button = QPushButton("Tìm kiếm")
        search_button.setStyleSheet("padding: 10px; background-color: #03A9F4; border-radius: 10px; color: white; font-weight: bold;")
        search_button.clicked.connect(self.search_pets)
        section_layout.addWidget(search_button)

        add_button = QPushButton("Thêm Thú Cưng")
        add_button.setStyleSheet("padding: 10px; background-color: #8BC34A; border-radius: 10px; color: white; font-weight: bold;")
        add_button.clicked.connect(self.open_add_pet_window)
        section_layout.addWidget(add_button)
        self.layout.addLayout(section_layout)

    def connect_db(self):
        return pymysql.connect(
            host='localhost',
            user='root',
            password='',
            database='cua_hang_thu_cung',
            cursorclass=pymysql.cursors.DictCursor
        )

    def display_pets(self, pets=None):
        for i in reversed(range(self.grid_layout.count())):
            self.grid_layout.itemAt(i).widget().setParent(None)

        try:
            if pets is None:
                connection = self.connect_db()
                with connection.cursor() as cursor:
                    cursor.execute("SELECT * FROM thucung")
                    pets = cursor.fetchall()
                connection.close()

            for index, pet in enumerate(pets):
                frame = self.create_pet_frame(pet)
                row = index // 4
                col = index % 4
                self.grid_layout.addWidget(frame, row, col)
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Không thể tải dữ liệu: {e}")

    def create_pet_frame(self, pet):
        frame = QGroupBox()
        frame.setStyleSheet("background-color: #6D4C41; border-radius: 15px; padding: 10px;")
        frame_layout = QVBoxLayout()

        if pet['image_link']:
            pixmap = QPixmap()
            pixmap.loadFromData(requests.get(pet['image_link']).content)
            pixmap = pixmap.scaled(200, 200, Qt.AspectRatioMode.KeepAspectRatio)
            img_label = QLabel()
            img_label.setPixmap(pixmap)
            img_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            frame_layout.addWidget(img_label)

        name_label = QLabel(pet['Ten'])
        name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        name_label.setStyleSheet("font: bold 14pt 'Arial'; margin-top: 10px;")
        frame_layout.addWidget(name_label)

        detail_button = QPushButton("Cập Nhật")
        detail_button.setStyleSheet("padding: 8px; background-color: #FF9800; border-radius: 10px; color: white; font-weight: bold;")
        detail_button.clicked.connect(lambda: self.open_update_pet_window(pet))
        frame_layout.addWidget(detail_button)

        delete_button = QPushButton("Xóa")
        delete_button.setStyleSheet("padding: 8px; background-color: #F44336; border-radius: 10px; color: white; font-weight: bold;")
        delete_button.clicked.connect(lambda: self.delete_pet(pet['MaThuCung']))
        frame_layout.addWidget(delete_button)

        frame.setLayout(frame_layout)
        return frame

    def open_update_pet_window(self, pet):
        self.update_pet_window = AddPetWindow(self, pet)
        self.update_pet_window.show()

    
    def delete_pet(self, ma_thu_cung):
        try:
            confirm = QMessageBox.question(
                self, "Xác nhận xóa", 
                "Bạn có chắc chắn muốn xóa thú cưng này? (Các bản ghi liên quan cũng sẽ bị xóa)",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
        
            if confirm == QMessageBox.StandardButton.Yes:
                connection = self.connect_db()
                with connection.cursor() as cursor:
                    cursor.execute("DELETE FROM thucung WHERE MaThuCung = %s", (ma_thu_cung,))
                    connection.commit()
                connection.close()
                QMessageBox.information(self, "Thành công", "Thú cưng và các bản ghi liên quan đã được xóa!")
                self.display_pets()
    
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Không thể xóa thú cưng: {e}")
            if 'connection' in locals():
                connection.close()

    def search_pets(self):
        keyword = self.search_input.text()
        try:
            connection = self.connect_db()
            with connection.cursor() as cursor:
                cursor.execute("SELECT * FROM thucung WHERE Ten LIKE %s", ('%' + keyword + '%',))
                pets = cursor.fetchall()
            connection.close()
            self.display_pets(pets)
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Không thể tìm kiếm: {e}")

    def open_add_pet_window(self):
        self.add_pet_window = AddPetWindow(self)
        self.add_pet_window.show()

if __name__ == "__main__":
    import sys
    import requests
    app = QApplication(sys.argv)
    window = QuanLyThuCung()
    window.show()
    sys.exit(app.exec())

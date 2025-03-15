-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Máy chủ: 127.0.0.1
-- Thời gian đã tạo: Th3 15, 2025 lúc 08:12 PM
-- Phiên bản máy phục vụ: 10.4.32-MariaDB
-- Phiên bản PHP: 8.2.12

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Cơ sở dữ liệu: `cua_hang_thu_cung`
--

-- --------------------------------------------------------

--
-- Cấu trúc bảng cho bảng `baocaobanhang`
--

CREATE TABLE `baocaobanhang` (
  `Loai` varchar(7) NOT NULL,
  `SoLuongBan` bigint(21) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Cấu trúc bảng cho bảng `chitiethoadon`
--

CREATE TABLE `chitiethoadon` (
  `MaChiTiet` int(11) NOT NULL,
  `MaHoaDon` int(11) DEFAULT NULL,
  `MaThuCung` int(11) DEFAULT NULL,
  `MaSanPham` int(11) DEFAULT NULL,
  `SoLuong` int(11) NOT NULL,
  `Gia` decimal(10,2) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Đang đổ dữ liệu cho bảng `chitiethoadon`
--

INSERT INTO `chitiethoadon` (`MaChiTiet`, `MaHoaDon`, `MaThuCung`, `MaSanPham`, `SoLuong`, `Gia`) VALUES
(10, 8, 62, NULL, 3, 750000.00),
(11, 12, 2, NULL, 5, 800000.00),
(12, 12, 53, NULL, 4, 450000.00),
(13, 8, 52, NULL, 7, 800000.00),
(14, 13, 51, NULL, 3, 500000.00),
(15, 14, NULL, 1, 4, 150000.00);

-- --------------------------------------------------------

--
-- Cấu trúc bảng cho bảng `hoadon`
--

CREATE TABLE `hoadon` (
  `MaHoaDon` int(11) NOT NULL,
  `MaKhachHang` int(11) DEFAULT NULL,
  `NgayLap` date NOT NULL,
  `TongTien` decimal(10,2) NOT NULL,
  `MaNhanVien` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Đang đổ dữ liệu cho bảng `hoadon`
--

INSERT INTO `hoadon` (`MaHoaDon`, `MaKhachHang`, `NgayLap`, `TongTien`, `MaNhanVien`) VALUES
(8, 11, '2025-02-25', 7850000.00, 1),
(12, 11, '2025-02-26', 5800000.00, 1),
(13, 11, '2025-03-16', 1500000.00, 3),
(14, 11, '2025-03-16', 600000.00, NULL);

--
-- Bẫy `hoadon`
--
DELIMITER $$
CREATE TRIGGER `insert_thongkedoanhthu_after_hoadon` AFTER INSERT ON `hoadon` FOR EACH ROW BEGIN
    DECLARE v_ma_khach_hang INT;
    DECLARE v_ngay DATE;
    DECLARE v_loai VARCHAR(20);
    DECLARE v_ten VARCHAR(100);
    DECLARE v_ma_thucung INT;
    DECLARE v_ma_sanpham INT;
    DECLARE v_doanh_thu_chiet DECIMAL(15,2);
    DECLARE v_doanh_thu_ngay DECIMAL(15,2);
    
    -- Lấy thông tin từ bản ghi mới trong HoaDon
    SET v_ma_khach_hang = NEW.MaKhachHang;
    SET v_ngay = NEW.NgayLap;
    
    -- Kiểm tra xem MaKhachHang có tồn tại trong KhachHang không
    IF v_ma_khach_hang IS NULL OR NOT EXISTS (SELECT MaKhachHang FROM KhachHang WHERE MaKhachHang = v_ma_khach_hang) THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Mã khách hàng không tồn tại trong hệ thống, không thể thêm vào thongkedoanhthu!';
    END IF;
    
    -- Lấy và thêm từng chi tiết từ ChiTietHoaDon vào thongkedoanhthu
    INSERT INTO thongkedoanhthu (Ngay, Loai, Ten, MaKhachHang, MaThuCung, MaSanPham, DoanhThuChiTiet, DoanhThuNgay)
    SELECT 
        NEW.NgayLap AS Ngay,
        CASE 
            WHEN ct.MaThuCung IS NOT NULL THEN 'Thú cưng'
            WHEN ct.MaSanPham IS NOT NULL THEN 'Sản phẩm'
            ELSE 'Không xác định'
        END AS Loai,
        CASE 
            WHEN ct.MaThuCung IS NOT NULL THEN tc.Ten
            WHEN ct.MaSanPham IS NOT NULL THEN sp.Ten
            ELSE 'Không xác định'
        END AS Ten,
        NEW.MaKhachHang AS MaKhachHang,
        ct.MaThuCung,
        ct.MaSanPham,
        (ct.SoLuong * ct.Gia) AS DoanhThuChiTiet,
        (SELECT SUM(c2.SoLuong * c2.Gia) FROM chitiethoadon c2 WHERE c2.MaHoaDon = NEW.MaHoaDon) AS DoanhThuNgay
    FROM chitiethoadon ct
    LEFT JOIN thucung tc ON ct.MaThuCung = tc.MaThuCung
    LEFT JOIN sanpham sp ON ct.MaSanPham = sp.MaSanPham
    WHERE ct.MaHoaDon = NEW.MaHoaDon;
END
$$
DELIMITER ;

-- --------------------------------------------------------

--
-- Cấu trúc bảng cho bảng `khachhang`
--

CREATE TABLE `khachhang` (
  `MaKhachHang` int(11) NOT NULL,
  `HoTen` varchar(100) NOT NULL,
  `SoDienThoai` varchar(15) NOT NULL,
  `Email` varchar(100) NOT NULL,
  `DiaChi` varchar(200) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Đang đổ dữ liệu cho bảng `khachhang`
--

INSERT INTO `khachhang` (`MaKhachHang`, `HoTen`, `SoDienThoai`, `Email`, `DiaChi`) VALUES
(11, 'Đạt', '02345678', 'dat@gmail.com', 'Hà NỘi'),
(12, 'Vũ Mơ', '012345678', 'vumo12123@gmail.com', 'Tân Đức - Phú Bình - Thái Nguyên'),
(13, 'Nguyễn Gia Phong', '0123456788', 'phong@gmail.com', 'Hà Nội');

-- --------------------------------------------------------

--
-- Cấu trúc bảng cho bảng `nhanvien`
--

CREATE TABLE `nhanvien` (
  `MaNhanVien` int(11) NOT NULL,
  `HoTen` varchar(100) NOT NULL,
  `TaiKhoan` varchar(50) NOT NULL,
  `MatKhau` varchar(100) NOT NULL,
  `PhanQuyen` varchar(20) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Đang đổ dữ liệu cho bảng `nhanvien`
--

INSERT INTO `nhanvien` (`MaNhanVien`, `HoTen`, `TaiKhoan`, `MatKhau`, `PhanQuyen`) VALUES
(1, 'Nguyễn Gia Phong', 'ahihi123', '111111', 'Nhân viên bán hàng'),
(2, 'Nguyen Van C', 'nvc', '123456', 'Nhân Viên'),
(3, 'Tran Thi D', 'admin', '789012', 'Quản lý'),
(4, 'Văn Huy', 'vh2006', '111111', 'Nhân viên'),
(5, 'Nguyễn Phong', 'np2004', '111111', 'Quản lý'),
(6, 'Nguyễn Phong', 'phong123', '111111', 'Nhân viên'),
(7, 'Vũ Trung Hiếu', 'vt123', '111111', 'Nhân viên bán hàng'),
(8, 'Vũ Trung Hiếu', 'hieu123', '111111', 'Quản lý'),
(9, 'Nguyễn Gia Phong', 'p111', '111111', 'Quản lý');

-- --------------------------------------------------------

--
-- Cấu trúc bảng cho bảng `sanpham`
--

CREATE TABLE `sanpham` (
  `MaSanPham` int(11) NOT NULL,
  `Ten` varchar(100) NOT NULL,
  `DanhMuc` varchar(50) DEFAULT NULL,
  `Gia` decimal(10,2) NOT NULL,
  `SoLuongTonKho` int(11) NOT NULL,
  `MoTa` text DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Đang đổ dữ liệu cho bảng `sanpham`
--

INSERT INTO `sanpham` (`MaSanPham`, `Ten`, `DanhMuc`, `Gia`, `SoLuongTonKho`, `MoTa`) VALUES
(1, 'Thuc an cho', 'Do an', 150000.00, 41, 'Thuc an chat luong cao');

-- --------------------------------------------------------

--
-- Cấu trúc bảng cho bảng `thongkedoanhthu`
--

CREATE TABLE `thongkedoanhthu` (
  `Ngay` date NOT NULL,
  `Loai` varchar(20) NOT NULL,
  `Ten` varchar(100) NOT NULL,
  `MaKhachHang` int(11) NOT NULL,
  `MaThuCung` int(11) NOT NULL,
  `MaSanPham` int(11) NOT NULL,
  `DoanhThuChiTiet` decimal(15,2) DEFAULT NULL,
  `DoanhThuNgay` decimal(15,2) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Cấu trúc bảng cho bảng `thongkekho`
--

CREATE TABLE `thongkekho` (
  `Ngay` date NOT NULL,
  `Loai` varchar(20) NOT NULL,
  `Ten` varchar(100) NOT NULL,
  `SoLuong` int(11) DEFAULT NULL,
  `MaSanPham` int(11) DEFAULT NULL,
  `MaThuCung` int(11) DEFAULT NULL,
  `ID` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Đang đổ dữ liệu cho bảng `thongkekho`
--

INSERT INTO `thongkekho` (`Ngay`, `Loai`, `Ten`, `SoLuong`, `MaSanPham`, `MaThuCung`, `ID`) VALUES
('2025-02-25', 'Sản phẩm', 'Thuc an cho', 50, 1, NULL, 137),
('2025-02-25', 'Thú cưng', 'Duke', 3, NULL, 58, 124),
('2025-02-25', 'Thú cưng', 'Luna', 5, NULL, 53, 119),
('2025-02-25', 'Thú cưng', 'Max', 8, NULL, 54, 120),
('2025-02-25', 'Thú cưng', 'Miu', 10, NULL, 51, 117),
('2025-02-25', 'Thú cưng', 'Nala', 9, NULL, 57, 123),
('2025-02-25', 'Thú cưng', 'Tom', 7, NULL, 2, 116),
('2025-02-26', 'Sản phẩm', 'Thuc an cho', 45, 1, NULL, 184),
('2025-02-26', 'Thú cưng', 'Duke', 3, NULL, 58, 171),
('2025-02-26', 'Thú cưng', 'Luna', 1, NULL, 53, 166),
('2025-02-26', 'Thú cưng', 'Max', 8, NULL, 54, 167),
('2025-02-26', 'Thú cưng', 'Miu', 10, NULL, 51, 164),
('2025-02-26', 'Thú cưng', 'Nala', 9, NULL, 57, 170),
('2025-02-26', 'Thú cưng', 'Tom', 7, NULL, 2, 163),
('2025-02-28', 'Sản phẩm', 'Thuc an cho', 45, 1, NULL, 208),
('2025-02-28', 'Thú cưng', 'Duke', 3, NULL, 58, 195),
('2025-02-28', 'Thú cưng', 'Luna', 1, NULL, 53, 190),
('2025-02-28', 'Thú cưng', 'Max', 8, NULL, 54, 191),
('2025-02-28', 'Thú cưng', 'Miu', 10, NULL, 51, 188),
('2025-02-28', 'Thú cưng', 'Nala', 9, NULL, 57, 194),
('2025-02-28', 'Thú cưng', 'Tom', 7, NULL, 2, 187),
('2025-03-11', 'Sản phẩm', 'Thuc an cho', 45, 1, NULL, 254),
('2025-03-11', 'Thú cưng', 'Duke', 3, NULL, 58, 241),
('2025-03-11', 'Thú cưng', 'Luna', 1, NULL, 53, 236),
('2025-03-11', 'Thú cưng', 'Max', 8, NULL, 54, 237),
('2025-03-11', 'Thú cưng', 'Miu', 10, NULL, 51, 235),
('2025-03-11', 'Thú cưng', 'Nala', 9, NULL, 57, 240),
('2025-03-11', 'Thú cưng', 'Tom', 2, NULL, 2, 234),
('2025-03-12', 'Sản phẩm', 'Thuc an cho', 45, 1, NULL, 277),
('2025-03-12', 'Thú cưng', 'Duke', 3, NULL, 58, 264),
('2025-03-12', 'Thú cưng', 'Luna', 1, NULL, 53, 259),
('2025-03-12', 'Thú cưng', 'Max', 8, NULL, 54, 260),
('2025-03-12', 'Thú cưng', 'Miu', 10, NULL, 51, 258),
('2025-03-12', 'Thú cưng', 'Nala', 9, NULL, 57, 263),
('2025-03-12', 'Thú cưng', 'Tom', 2, NULL, 2, 257),
('2025-03-16', 'Sản phẩm', 'Thuc an cho', 45, 1, NULL, 345),
('2025-03-16', 'Thú cưng', 'Chó ngu', 2, NULL, 2, 339),
('2025-03-16', 'Thú cưng', 'Duke', 3, NULL, 58, 344),
('2025-03-16', 'Thú cưng', 'Luna', 1, NULL, 53, 341),
('2025-03-16', 'Thú cưng', 'Max', 8, NULL, 54, 342),
('2025-03-16', 'Thú cưng', 'Miu', 10, NULL, 51, 340),
('2025-03-16', 'Thú cưng', 'Nala', 9, NULL, 57, 343);

-- --------------------------------------------------------

--
-- Cấu trúc bảng cho bảng `thucung`
--

CREATE TABLE `thucung` (
  `MaThuCung` int(11) NOT NULL,
  `Ten` varchar(100) NOT NULL,
  `Loai` varchar(50) NOT NULL,
  `Giong` varchar(50) DEFAULT NULL,
  `GioiTinh` varchar(10) DEFAULT NULL,
  `Tuoi` int(11) NOT NULL,
  `GiaBan` decimal(10,2) NOT NULL,
  `SoLuong` int(11) NOT NULL,
  `TinhTrangSucKhoe` varchar(100) DEFAULT NULL,
  `image_link` varchar(255) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Đang đổ dữ liệu cho bảng `thucung`
--

INSERT INTO `thucung` (`MaThuCung`, `Ten`, `Loai`, `Giong`, `GioiTinh`, `Tuoi`, `GiaBan`, `SoLuong`, `TinhTrangSucKhoe`, `image_link`) VALUES
(1, 'AhihiMiu', 'Meo', 'None', 'Cái', 2, 500000.00, 0, 'Khoe manh', 'https://file.hstatic.net/200000108863/file/3_33cbf6a0308e40ca8962af5e0460397c_grande.png'),
(2, 'Chó ngu', 'Cho', 'None', 'Đực', 3, 800000.00, 2, 'Khoe manh', 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRMcWVmo5Iz4uzntpSqxGngyOk1wZ-lWDWCVA&s'),
(51, 'Miu', 'Meo', 'None', 'Đực', 2, 500000.00, 7, 'Khoe manh', 'https://ampet.vn/wp-content/uploads/2022/09/Meo-tai-cup-Scottish-Fold-2.jpg'),
(52, 'Tom', 'Cho', 'None', 'Đực', 3, 800000.00, 0, 'Khoe manh', 'https://imgs.vietnamnet.vn/Images/2012/09/21/15/20120921154655_meo.jpeg'),
(53, 'Luna', 'Meo', 'None', 'Đực', 1, 450000.00, 1, 'Binh thuong', 'https://samyangvietnam.com/wp-content/uploads/2024/09/hanh-vi-cua-meo-cam-01.jpg.webp'),
(54, 'Max', 'Cho', 'None', 'Đực', 4, 900000.00, 8, 'Khoe manh', 'https://cdn.shopify.com/s/files/1/0624/1746/9697/files/siberian-husky-100800827-2000-9449ca147e0e4b819bce5189c2411188_600x600.jpg?v=1690185264'),
(57, 'Nala', 'Meo', 'None', 'Đực', 1, 480000.00, 9, 'Khoe manh', 'https://media-cdn-v2.laodong.vn/Storage/NewsPortal/2020/6/23/814689/7-Giong-Meo-Dat-Nhat-03.jpg'),
(58, 'Duke', 'Cho', 'None', 'Cái', 5, 950000.00, 3, 'Khoe manh', 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQzL6hQXoHARbmT-gVSmm6oa4Ln7-RllNEKFw&s');

--
-- Chỉ mục cho các bảng đã đổ
--

--
-- Chỉ mục cho bảng `baocaobanhang`
--
ALTER TABLE `baocaobanhang`
  ADD PRIMARY KEY (`Loai`);

--
-- Chỉ mục cho bảng `chitiethoadon`
--
ALTER TABLE `chitiethoadon`
  ADD PRIMARY KEY (`MaChiTiet`),
  ADD KEY `MaHoaDon` (`MaHoaDon`),
  ADD KEY `MaThuCung` (`MaThuCung`),
  ADD KEY `MaSanPham` (`MaSanPham`);

--
-- Chỉ mục cho bảng `hoadon`
--
ALTER TABLE `hoadon`
  ADD PRIMARY KEY (`MaHoaDon`),
  ADD KEY `MaKhachHang` (`MaKhachHang`),
  ADD KEY `MaNhanVien` (`MaNhanVien`);

--
-- Chỉ mục cho bảng `khachhang`
--
ALTER TABLE `khachhang`
  ADD PRIMARY KEY (`MaKhachHang`),
  ADD UNIQUE KEY `SoDienThoai` (`SoDienThoai`),
  ADD UNIQUE KEY `Email` (`Email`);

--
-- Chỉ mục cho bảng `nhanvien`
--
ALTER TABLE `nhanvien`
  ADD PRIMARY KEY (`MaNhanVien`),
  ADD UNIQUE KEY `TaiKhoan` (`TaiKhoan`);

--
-- Chỉ mục cho bảng `sanpham`
--
ALTER TABLE `sanpham`
  ADD PRIMARY KEY (`MaSanPham`);

--
-- Chỉ mục cho bảng `thongkedoanhthu`
--
ALTER TABLE `thongkedoanhthu`
  ADD PRIMARY KEY (`Ngay`,`Loai`,`Ten`,`MaKhachHang`,`MaThuCung`,`MaSanPham`),
  ADD KEY `MaKhachHang` (`MaKhachHang`),
  ADD KEY `MaThuCung` (`MaThuCung`),
  ADD KEY `MaSanPham` (`MaSanPham`);

--
-- Chỉ mục cho bảng `thongkekho`
--
ALTER TABLE `thongkekho`
  ADD PRIMARY KEY (`Ngay`,`Loai`,`Ten`),
  ADD UNIQUE KEY `ID` (`ID`),
  ADD KEY `MaSanPham` (`MaSanPham`),
  ADD KEY `MaThuCung` (`MaThuCung`);

--
-- Chỉ mục cho bảng `thucung`
--
ALTER TABLE `thucung`
  ADD PRIMARY KEY (`MaThuCung`);

--
-- AUTO_INCREMENT cho các bảng đã đổ
--

--
-- AUTO_INCREMENT cho bảng `chitiethoadon`
--
ALTER TABLE `chitiethoadon`
  MODIFY `MaChiTiet` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=16;

--
-- AUTO_INCREMENT cho bảng `hoadon`
--
ALTER TABLE `hoadon`
  MODIFY `MaHoaDon` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=15;

--
-- AUTO_INCREMENT cho bảng `khachhang`
--
ALTER TABLE `khachhang`
  MODIFY `MaKhachHang` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=14;

--
-- AUTO_INCREMENT cho bảng `nhanvien`
--
ALTER TABLE `nhanvien`
  MODIFY `MaNhanVien` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=10;

--
-- AUTO_INCREMENT cho bảng `sanpham`
--
ALTER TABLE `sanpham`
  MODIFY `MaSanPham` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=25;

--
-- AUTO_INCREMENT cho bảng `thongkekho`
--
ALTER TABLE `thongkekho`
  MODIFY `ID` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=347;

--
-- AUTO_INCREMENT cho bảng `thucung`
--
ALTER TABLE `thucung`
  MODIFY `MaThuCung` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=74;

--
-- Các ràng buộc cho các bảng đã đổ
--

--
-- Các ràng buộc cho bảng `chitiethoadon`
--
ALTER TABLE `chitiethoadon`
  ADD CONSTRAINT `chitiethoadon_ibfk_1` FOREIGN KEY (`MaHoaDon`) REFERENCES `hoadon` (`MaHoaDon`) ON DELETE CASCADE,
  ADD CONSTRAINT `chitiethoadon_ibfk_3` FOREIGN KEY (`MaSanPham`) REFERENCES `sanpham` (`MaSanPham`) ON DELETE SET NULL;

--
-- Các ràng buộc cho bảng `hoadon`
--
ALTER TABLE `hoadon`
  ADD CONSTRAINT `hoadon_ibfk_1` FOREIGN KEY (`MaKhachHang`) REFERENCES `khachhang` (`MaKhachHang`) ON DELETE CASCADE,
  ADD CONSTRAINT `hoadon_ibfk_2` FOREIGN KEY (`MaNhanVien`) REFERENCES `nhanvien` (`MaNhanVien`);

--
-- Các ràng buộc cho bảng `thongkedoanhthu`
--
ALTER TABLE `thongkedoanhthu`
  ADD CONSTRAINT `thongkedoanhthu_ibfk_1` FOREIGN KEY (`MaKhachHang`) REFERENCES `khachhang` (`MaKhachHang`),
  ADD CONSTRAINT `thongkedoanhthu_ibfk_3` FOREIGN KEY (`MaSanPham`) REFERENCES `sanpham` (`MaSanPham`);

--
-- Các ràng buộc cho bảng `thongkekho`
--
ALTER TABLE `thongkekho`
  ADD CONSTRAINT `thongkekho_ibfk_1` FOREIGN KEY (`MaSanPham`) REFERENCES `sanpham` (`MaSanPham`) ON DELETE CASCADE,
  ADD CONSTRAINT `thongkekho_ibfk_2` FOREIGN KEY (`MaThuCung`) REFERENCES `thucung` (`MaThuCung`) ON DELETE CASCADE;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;

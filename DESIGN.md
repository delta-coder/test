# CineBook UI Redesign — Cấu trúc thiết kế mới

## 1. Mục tiêu thiết kế
- Biến CineBook thành một trải nghiệm đặt vé xem phim có cảm giác “rạp chiếu phim thật”: tối, ấm, có chiều sâu và tập trung vào poster/phim.
- Giữ nguyên luồng nghiệp vụ hiện tại: Home → Danh mục phim → Chi tiết phim → Chọn ghế → Vé của tôi.
- Ưu tiên sự nhất quán: cùng một hệ màu, cùng một kiểu nút, cùng một cách bày trí thông tin trên mọi màn hình.

## 2. Phong cách chủ đạo
- **Midnight auditorium**: nền xanh đêm rất sâu, tạo cảm giác đang ở trong rạp.
- **Warm projection orange**: màu cam ấm làm điểm nhấn hành động, thay vì đỏ/cam quá gắt.
- **Serif display + grotesque UI**: tiêu đề có cảm giác poster điện ảnh; phần điều khiển và dữ liệu vẫn dễ đọc, hiện đại.
- **Một điểm nhấn đủ mạnh**: để poster và seat chart là phần nổi bật nhất, còn chrome giao diện giữ ở mức yên tĩnh.

## 3. Hệ màu hiện tại
Các màu được gom trong `:root` ở `web/public/css/style.css`.

### Nền và bề mặt
| Token | Giá trị | Cách dùng |
|---|---|---|
| `--bg` | `#070b16` | Nền chính của trang |
| `--stage` | `#0b1120` | Nền vùng nội dung chính |
| `--surface` | `rgba(13, 20, 38, 0.84)` | Card, panel, lớp phủ nhẹ |
| `--surface-2` | `rgba(9, 15, 30, 0.94)` | Vùng nổi hơn, ví dụ booking summary |
| `--border` | `rgba(255, 255, 255, 0.08)` | Viền nhẹ |
| `--border-strong` | `rgba(255, 255, 255, 0.14)` | Viền khi hover/focus |

### Chữ
| Token | Giá trị | Cách dùng |
|---|---|---|
| `--text` | `#eef2f7` | Chữ chính |
| `--text-soft` | `#c2cbdc` | Chữ phụ |
| `--muted` | `#8795ad` | Chữ mờ, trạng thái phụ |

### Điểm nhấn
| Token | Giá trị | Cách dùng |
|---|---|---|
| `--accent` | `#ff6b35` | Nút chính, trạng thái active, hover |
| `--accent-d` | `#e25a24` | Hover của nút accent |
| `--accent-glow` | `rgba(255, 107, 53, 0.35)` | Glow cho CTA |
| `--gold` | `#ffd166` | Rating, mã vé, VIP |
| `--green` | `#2dd4a0` | Ghế đã chọn, trạng thái thành công |
| `--green-d` | `#24a986` | Nền phụ của ghế đã chọn |
| `--green-glow` | `rgba(45, 212, 160, 0.40)` | Glow cho ghế đã chọn |
| `--amber` | `#ffb020` | Ghế người khác đang giữ |
| `--red` | `#ff5b5b` | Hủy vé, cảnh báo |

### Ghế
| Token | Giá trị | Cách dùng |
|---|---|---|
| `--seat-free` | `#1b2740` | Ghế trống |
| `--seat-free-base` | `#0c1322` | Phần chân ghế trống |
| `--seat-free-border` | `rgba(255, 255, 255, 0.12)` | Viền ghế trống |
| `--seat-mine` | `#2dd4a0` | Ghế tôi đã chọn |
| `--seat-mine-base` | `#189e73` | Chân ghế tôi đã chọn |
| `--seat-holding` | `#ffb020` | Ghế người khác giữ |
| `--seat-booked` | `#414c63` | Ghế đã bán |
| `--seat-vip` | `#5a3a1a` | Ghế VIP |
| `--seat-vip-border` | `#ff6b35` | Viền ghế VIP |
| `--seat-vip-bg` | `#342010` | Chân ghế VIP |
| `--stage-bg` | `#070b16` | Nền dùng cho phần cắt perforation của vé |

## 4. Typography
| Token | Font | Vai trò |
|---|---|---|
| `--font-display` | `Cormorant Garamond`, serif fallback | Tiêu đề lớn, hero, tên phim |
| `--font-ui` | `IBM Plex Sans`, sans-serif fallback | Nội dung chính, form, điều khiển |
| `--font-mono` | `IBM Plex Mono`, monospace fallback | Mã ghế, mã vé, dữ liệu nhỏ |

## 5. Cấu trúc trang
### Global chrome
- `site-navbar`: navbar cố định phía trên, nền kính tối, logo bên trái, nav/auth bên phải.
- `site-stage`: vùng nội dung chính, bo góc, có lớp nền và overlay.
- `stage-background`: ảnh nền mờ, tạo chiều sâu.
- `stage-overlay`: gradient tối để nội dung luôn dễ đọc.
- `stage-content`: vùng chứa các màn hình con.

### Home
- `hero-spotlight`: phần nổi bật nhất.
  - `hero-spotlight-backdrop`: ảnh poster làm nền mờ.
  - `hero-spotlight-content`: tag, tiêu đề, metadata, mô tả, CTA.
- `cinema-perks-row`: 3 lợi ích chính.
- `catalog-header-wrap`: tiêu đề danh mục + search/filter.
- `movie-grid-compact`: lưới phim.

### Movies
- `page-top-action-bar`: nút quay lại + breadcrumb.
- `section-title-box`: tiêu đề và mô tả ngắn.
- `genre-filter-pills`: bộ lọc thể loại.

### Schedule
- `schedule-date-tabs`: tab ngày.
- `schedule-movie-row`: mỗi phim là một hàng, có ảnh, thông tin và chip giờ chiếu.

### Movie detail
- `movie-detail-card`: poster bên trái, thông tin bên phải.
- `detail-showtimes-grid`: danh sách suất chiếu.

### Booking
- `booking-header-card`: tên phim, giờ chiếu, phòng, trạng thái kết nối.
- `booking-ticket-toolbar`: chọn loại vé và giá.
- `cinema-arena`: khu vực sơ đồ ghế.
  - `curved-screen`: màn hình giả lập.
  - `seat-legend-box`: bảng chú thích trạng thái ghế.
  - `cinema-seat-rows-list`: các hàng ghế.
  - `seat-row`: một hàng ghế.
  - `seat-row-label`: ký hiệu hàng A/B/C…
  - `seat-row-seats`: các ghế trong hàng.
  - `live-seat`: nút ghế.
    - `seat-back`: phần lưng ghế.
    - `seat-base`: phần chân ghế.
- `booking-summary-bar`: thanh tổng kết nổi khi chọn ghế.

### Tickets
- `ticket-grid`: lưới vé.
- `ticket-stub-card`: thẻ vé dạng stub.
- `ticket-stub-perforation`: đường đứt gãy giữa phần chính và phần đuôi vé.

### Auth & confirm
- `auth-modal-overlay`: lớp phủ đăng nhập/đăng ký.
- `auth-modal-card`: form đăng nhập/đăng ký.
- `cancel-confirm-overlay`: xác nhận hủy vé.

## 6. Layout và breakpoint
### Desktop
- Navbar cố định trên cùng.
- Nội dung chính nằm trong một “stage” bo góc, căn giữa.
- Lưới phim dùng `auto-fill`, mỗi cột tối thiểu 220px.
- Chi tiết phim dùng 2 cột: poster 270px + nội dung.

### Mobile
- `<= 992px`: navbar chuyển thành menu mở/xả; các phần quan trọng xếp dọc.
- `<= 600px`: lưới phim 2 cột, seat chart co lại, booking summary xếp dọc.

## 7. Tương tác
- Hover ghế: nhấc nhẹ, dễ thấy nhưng không gây rối.
- Chọn ghế: đổi màu ngay lập tức, summary cập nhật tức thì.
- Ghế người khác giữ: màu amber, không chọn được.
- Ghế đã bán: mờ, không tương tác.
- Nút chính: cam, có glow nhẹ.
- Focus ring: rõ ràng, dùng màu accent.
- Reduced motion: tắt animation nếu người dùng bật chế độ này.

## 8. Cách tùy chỉnh nhanh
- Đổi màu chủ đạo: sửa `--bg`, `--accent`, `--gold`, `--green` trong `:root`.
- Đổi font: sửa 3 token font trong `:root`.
- Đổi độ bo/giảm sáng: sửa các biến `--border`, `--border-strong`, `--surface`, `--surface-2`.
- Đổi trạng thái ghế: sửa nhóm `--seat-*`.
- Đổi layout: chỉnh các class chính như `movie-grid-compact`, `movie-detail-card`, `cinema-arena`, `booking-summary-bar`.

## 9. File liên quan
- `web/public/index.html`: markup và cấu trúc màn hình.
- `web/public/css/style.css`: toàn bộ hệ thống thiết kế mới.
- `web/public/js/app.js`: logic vận hành, giữ gần như nguyên bản.
- `web/public/images/movies/*`: poster phim hiện có.

## 10. Ghi chú triển khai
- Không đổi API.
- Không đổi luồng đặt vé.
- Không đổi dữ liệu phim.
- Chỉ thay đổi lớp trình bày và một số class CSS để giữ tương thích với JS hiện tại.

---
*End of design structure.*

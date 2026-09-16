# 🎬 CineBook - Hệ Thống Đặt Vé Xem Phim Trực Tuyến

> Website đặt vé xem phim hiện đại, chọn ghế thời gian thực (Real-time Live Seats), giao diện rạp phim sang trọng, tối ưu 100% để triển khai miễn phí lên **Vercel Free Tier** và kết nối **GitHub**.

---

## ✨ Tính Năng Nổi Bật

- 🎞 **Danh sách & Chi tiết phim**: Thông tin đầy đủ về phim, đạo diễn, thời lượng, thể loại, ngày công chiếu và suất chiếu.
- 🗓 **Lịch chiếu phim**: Theo dõi lịch chiếu sắp diễn ra theo ngày, giờ và phòng chiếu.
- 💺 **Sơ đồ ghế thời gian thực (Realtime Seat Booking)**:
  - Hiển thị trực quan: *Trống*, *Bạn đang chọn*, *Người khác đang chọn*, *Đã đặt*.
  - Giữ ghế tạm thời (Hold Seat) tự động giải phóng sau thời gian chờ.
  - Đồng bộ ghế tức thì qua Server-Sent Events (SSE) và tự động chuyển sang Polling thông minh nếu mạng gián đoạn.
- 🎟 **Vé của tôi**:
  - Xem danh sách vé đã đặt: phòng chiếu, số ghế, loại vé (Người lớn / Trẻ em), giá tiền.
  - Hỗ trợ **Hủy vé** trước giờ chiếu kèm hộp thoại xác nhận trực quan.
- 🔐 **Bảo mật**: Đăng ký, đăng nhập với mã hóa Bcrypt và JWT HttpOnly Cookie.
- ☁️ **Sẵn sàng cho Vercel Free**: Cấu hình tự động chuẩn hóa chuỗi kết nối PostgreSQL (Neon, Supabase) và fallback SQLite an toàn trên môi trường Serverless.

---

## 🔑 Tài Khoản Mặc Định

Hệ thống tự động tạo sẵn tài khoản Admin:
- **Tên đăng nhập**: `admin`
- **Mật khẩu**: `123`

---

## ☁️ Hướng Dẫn Đưa Lên Vercel (Miễn Phí 100%)

### Bước 1: Đưa Source Code Lên GitHub
Chạy các lệnh sau trong thư mục dự án (Terminal / PowerShell / Git Bash):
```bash
git init
git add .
git commit -m "feat: hoàn thiện cinema booking sẵn sàng deploy Vercel"
git branch -M main
git remote add origin https://github.com/TÊN_TÀI_KHOẢN/TÊN_REPO.git
git push -u origin main
```

### Bước 2: Tạo Cơ Sở Dữ Liệu PostgreSQL Miễn Phí (Khuyên Dùng)
Để dữ liệu người dùng, phim và vé đặt được lưu trữ vĩnh viễn trên môi trường Serverless của Vercel:
1. Đăng ký tài khoản miễn phí tại [Neon.tech](https://neon.tech/) hoặc [Supabase.com](https://supabase.com/).
2. Tạo một database mới và copy chuỗi kết nối `DATABASE_URL` (ví dụ: `postgresql://user:pass@ep-xyz.neon.tech/cinema?sslmode=require`).

> *Lưu ý: Nếu không cấu hình Database ngoài, hệ thống sẽ tự động dùng SQLite tạm thời trên `/tmp` của Vercel để trang web vẫn hoạt động bình thường.*

### Bước 3: Import và Deploy Trên Vercel
1. Đăng nhập [Vercel.com](https://vercel.com/) và chọn **Add New...** -> **Project**.
2. Chọn kho mã nguồn GitHub bạn vừa tải lên.
3. Trong bảng cấu hình:
   - **Framework Preset**: Chọn **Other**.
   - **Root Directory**: Để mặc định `./` (hoặc chọn `web` đều được, dự án đã có cấu hình cho cả 2 trường hợp).
4. Thêm các **Environment Variables** (Biến môi trường):
   - `DATABASE_URL`: Dán chuỗi kết nối PostgreSQL (từ Neon / Supabase).
   - `SECRET_KEY`: Chuỗi bí mật bất kỳ (Ví dụ: `cinema-secret-key-2026`).
   - `ADMIN_USERNAME`: `admin`
   - `ADMIN_PASSWORD`: `123`
5. Nhấn nút **Deploy**! Vercel sẽ tự động build và cung cấp cho bạn đường link website (ví dụ: `https://your-cinema.vercel.app`).

---

## 💻 Hướng Dẫn Chạy Cục Bộ (Local)

Dành cho bạn hoặc bất kỳ ai tải mã nguồn về muốn chạy thử trên máy tính cá nhân:

1. **Mở Terminal tại thư mục dự án**:
   ```bash
   # Tạo môi trường ảo Python
   python -m venv .venv

   # Kích hoạt môi trường ảo:
   # Trên Windows:
   .venv\Scripts\activate
   # Trên macOS / Linux:
   source .venv/bin/activate

   # Cài đặt các thư viện:
   pip install -r requirements.txt
   ```

2. **Chạy máy chủ**:
   ```bash
   uvicorn web.api.index:app --host 127.0.0.1 --port 8000 --reload
   ```

3. **Mở trình duyệt**:
   - Website chính: [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
   - Swagger API Docs: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

---

## 📂 Cấu Trúc Thư Mục Dự Án

```
cinema_booking_simple/
├── web/                           # Ứng dụng chính (FastAPI backend & Static frontend)
│   ├── api/                       # Mã nguồn Backend
│   │   ├── routers/               # Các endpoint API (auth, movies, showtimes, tickets)
│   │   ├── auth.py                # Xử lý JWT & băm mật khẩu Bcrypt
│   │   ├── config.py              # Đọc cấu hình & chuẩn hóa kết nối DB
│   │   ├── db.py                  # Khởi tạo SQLAlchemy Engine & dữ liệu mẫu
│   │   ├── deps.py                # Dependency injection & xác thực người dùng
│   │   ├── models.py              # Định nghĩa các bảng dữ liệu
│   │   ├── schemas.py             # Pydantic schemas kiểm tra dữ liệu
│   │   └── index.py               # Điểm khởi chạy FastAPI & mount frontend
│   ├── public/                    # Giao diện người dùng (HTML/CSS/JS)
│   │   ├── css/                   # Stylesheet giao diện
│   │   ├── js/app.js              # Xử lý tương tác, gọi API, SSE stream & Polling
│   │   └── index.html             # Giao diện chính Single Page Application
│   ├── vercel.json                # Cấu hình khi deploy thư mục web
│   └── requirements.txt           # Danh sách thư viện Python
├── vercel.json                    # Cấu hình Vercel ở thư mục gốc (auto-deploy)
├── requirements.txt               # Thư viện dùng chung
├── .gitignore                     # Tệp loại trừ các file rác, file tạm, cache
└── README.md                      # Hướng dẫn chi tiết
```

---

## 🛡 Xử Lý Lỗi Thường Gặp (FAQ)

- **Q: Tại sao tôi tải code từ máy khác về bị lỗi không tìm thấy python?**
  *A: Do thư mục `.venv` cũ chứa đường dẫn của máy người khác. Bạn chỉ cần xóa thư mục `.venv` đi và tạo lại bằng lệnh `python -m venv .venv` là xong.*
- **Q: Tài khoản quản trị viên là gì?**
  *A: Tên đăng nhập: `admin`, Mật khẩu: `123`.*
- **Q: Làm sao để deploy Vercel mà không bị lỗi timeout?**
  *A: API SSE real-time stream đã được tối ưu chu kỳ phát dữ liệu ngắn (~8s) phù hợp hoàn hảo với giới hạn 10s của gói Vercel Free, kết hợp cơ chế tự động kết nối lại và polling dự phòng.*

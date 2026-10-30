ỨNG DỤNG THEO DÕI LUYỆN TẬP THỂ THAO (Đề tài 16)

Giới thiệu
Đây là ứng dụng quản lý và theo dõi luyện tập thể thao được viết bằng Python (giao diện Tkinter). Ứng dụng giúp người dùng ghi nhận các buổi tập, lập kế hoạch, theo dõi tiến độ calo và quản lý chỉ số cơ thể (BMI).

Yêu cầu hệ thống

Hệ điều hành: Windows / macOS / Linux.

Python: Phiên bản 3.8 trở lên (Khuyến nghị 3.10+).

Hướng dẫn cài đặt và Khởi chạy
Cách 1: Chạy trực tiếp bằng mã nguồn (Dành cho nhà phát triển)

Bước 1: Cài đặt các thư viện phụ thuộc. Mở Terminal/CMD tại thư mục dự án và chạy lệnh:
pip install tkcalendar requests beautifulsoup4 pyinstaller

Bước 2: Khởi chạy ứng dụng bằng lệnh:
python main.py

Cách 2: Chạy file thực thi (Dành cho người dùng cuối)

Truy cập vào thư mục chứa file thực thi.

Nhấp đúp chuột vào file main.exe để mở ứng dụng.

Tài khoản mặc định (Dành cho Demo)
Nếu là lần đầu chạy (file accounts.json trống hoặc chưa có), hệ thống sẽ tự động tạo tài khoản Quản trị viên:

Tên đăng nhập: admin

Mật khẩu: 123
(Lưu ý: Bạn có thể tự tạo tài khoản Người dùng mới thông qua nút "Đăng ký" trên giao diện).

Cấu trúc thư mục dữ liệu
Ứng dụng lưu trữ dữ liệu hoàn toàn bằng file JSON (không dùng CSDL). Các file dữ liệu sẽ tự động được tạo/cập nhật trong quá trình sử dụng:

accounts.json: Lưu thông tin tài khoản (mật khẩu đã mã hóa SHA-256).

activities.json: Lưu lịch sử các buổi tập.

plans.json: Lưu danh sách kế hoạch luyện tập.

exercises.json: Danh mục bài tập (có thể tự động cào thêm từ API Free Exercise DB).

bodymetrics.json: Lịch sử đo chỉ số cơ thể (BMI).

Các chức năng chính

Đăng nhập, Đăng ký, Phân quyền (Admin/User).

Thêm, Xóa, Sửa, Tìm kiếm buổi tập.

Lập kế hoạch và xem tiến độ hoàn thành (%).

Vẽ biểu đồ cột (Canvas) và vòng tròn tiến độ (CircularProgress).

Tính chỉ số BMI và phân loại sức khỏe.

Xuất nhật ký luyện tập ra file văn bản .txt.

Tự động lấy dữ liệu bài tập từ API bên ngoài (Free Exercise DB).
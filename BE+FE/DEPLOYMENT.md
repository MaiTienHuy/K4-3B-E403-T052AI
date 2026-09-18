# 🐳 Hướng Dẫn Triển Khai (Docker & Tunnels)

Để khắc phục giới hạn tài nguyên của các dịch vụ miễn phí (như Render) và bảo vệ ứng dụng khỏi Spam/DDoS, dự án hỗ trợ triển khai bằng **Docker Compose** kết hợp **Nginx** và **Cloudflare Tunnels**.

## 1. Kiến trúc triển khai
- **App:** Ứng dụng Streamlit & ChromaDB.
- **Nginx:** Đứng trước App, giới hạn tốc độ truy cập (Rate Limiting: 20 req/s, chống spam F5).
- **Cloudflare Tunnel:** Tự động tạo link public (`*.trycloudflare.com`) giúp đưa ứng dụng ra mạng Internet mà không cần NAT port hay mua tên miền.

## 2. Cách khởi chạy
Mở terminal tại thư mục `BE+FE` và gõ:
```bash
docker compose up --build -d
```

## 3. Lấy link truy cập Public
Sau khi các container đã chạy, bạn xem log của Tunnel để lấy link:
```bash
docker compose logs tunnel
```
Tìm dòng có chứa `https://<random-name>.trycloudflare.com` và truy cập bằng trình duyệt.

client: django ui - gọi api services 
API getway: KONG: http://localhost:8000
services: 
- user services: Đăng ký đang nhập, lấy thông tin của người dùng, kiểm tra phiên đăng nhập -> chạy ở port 8000 -> xuất port 8003
- business service: Chứa code logic cho trang web, CRUD: brand, category, products, cart, order, bài viết -> chạy ở port 8000 -> xuất port 8004

- payment service: công thanh toán momo -> chạy ở port 8000 -> xuất port 8005
- chatbot service: AI agent -> chạy ở port 8000 -> xuất port 8006

# Trung Việt Learning — bản Streamlit khởi đầu

## Chạy trên máy tính
1. Cài Python 3.10 trở lên.
2. Mở Terminal/CMD trong thư mục dự án.
3. Chạy: `pip install -r requirements.txt`
4. Chạy: `streamlit run app.py`

## Chức năng hiện có
- Phân loại bài theo HSK 1–HSK 6.
- Luyện dịch Trung → Việt và Việt → Trung.
- Luyện gõ Trung–Trung, chấm độ khớp ký tự theo vị trí.
- Từ vựng, pinyin, bộ thủ, mẹo nhớ, ví dụ.
- Ngữ pháp và ví dụ.
- Nhập JSON trước; gộp/cập nhật bài theo `lesson_id`.
- Tải nhiều MP3 sau; ghép theo `sentence_id`/`audio_id` hoặc `lesson_id`.
- Xuất JSON để sao lưu.

## Quy tắc đặt mã
- Mỗi bài phải có `lesson_id` duy nhất toàn ứng dụng, ví dụ `HSK1_B001`.
- Mỗi câu nên có `sentence_id` duy nhất, ví dụ `HSK1_B001_S001`.
- Tên file MP3 lấy đúng mã cần gắn: `HSK1_B001_S001.mp3` (theo câu) hoặc `HSK1_B001.mp3` (theo bài).
- Có thể nhập JSON trước và tải MP3 sau.

## Cấu trúc JSON
Xem `data/lessons.json` để tham khảo.

## Lưu trữ — lưu ý quan trọng
Bản này lưu JSON và MP3 vào thư mục `data/` của máy chạy Streamlit. Khi chạy trên máy tính cá nhân, dữ liệu nằm trên máy đó. Khi triển khai trên dịch vụ cloud, thư mục có thể không phải kho lưu trữ bền vững; cần nối Supabase Database + Storage ở bước tiếp theo. **Bản này chưa kết nối Supabase và chưa có giọng đọc TTS tự động**; nút phát MP3 hoạt động khi đã có file âm thanh được gắn.

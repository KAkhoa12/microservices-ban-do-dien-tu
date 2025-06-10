import sqlite3
import os
def list_all_tables(database_path):
    try:
        conn = sqlite3.connect(database_path)
        cursor = conn.cursor()

        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()

        if not tables:
            print("⚠️ Không có bảng nào trong cơ sở dữ liệu.")
        else:
            print("📋 Danh sách các bảng trong database:")
            for table in tables:
                print("-", table[0])

        conn.close()
    except Exception as e:
        print("❌ Lỗi khi liệt kê bảng:", e)

def update_image_urls(database_path, table_name, column_name, new_prefix):
    try:
        conn = sqlite3.connect(database_path)
        cursor = conn.cursor()

        # Lấy tất cả image_url
        cursor.execute(f"SELECT rowid, {column_name} FROM {table_name}")
        rows = cursor.fetchall()

        for row in rows:
            rowid, image_url = row

            # Lấy tên file
            filename = os.path.basename(image_url)

            # Tạo URL mới với tiền tố (đảm bảo dùng dấu '/')
            new_url = os.path.join(new_prefix, filename).replace("\\", "/")

            # Cập nhật lại dòng bằng rowid (nội bộ của SQLite)
            cursor.execute(f"""
                UPDATE {table_name}
                SET {column_name} = ?
                WHERE rowid = ?
            """, (new_url, rowid))

        conn.commit()
        print(f"✅ Đã cập nhật {len(rows)} dòng thành công.")
    except Exception as e:
        print("❌ Lỗi:", e)
    finally:
        conn.close()

if __name__ == "__main__":
    # ⚙️ Thay đổi các giá trị này theo nhu cầu của bạn
    DATABASE_PATH = "./db.sqlite3"     # 👉 Tên file database
    TABLE_NAME = "frontend_giaiphapamthanh"
    COLUMN_NAME = "image_url"
    NEW_PREFIX = "static/business/imgs/giai_phap/"     # 👉 Tiền tố bạn muốn thêm vào tên file

    # list_all_tables(DATABASE_PATH)
    update_image_urls(DATABASE_PATH, TABLE_NAME, COLUMN_NAME, NEW_PREFIX)

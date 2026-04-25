import pandas as pd
import matplotlib.pyplot as plt
import os

# Cấu hình biểu đồ
plt.rcParams['figure.figsize'] = (12, 8)

def analyze_sales(csv_path):
    # 1. Đọc dữ liệu
    print(f"Đang đọc dữ liệu từ {csv_path}...")
    try:
        df = pd.read_csv(csv_path)
    except Exception as e:
        print(f"Lỗi khi đọc file CSV: {e}")
        return

    # 2. Tiền xử lý dữ liệu
    # Chuyển đổi OrderDate sang kiểu datetime
    df['OrderDate'] = pd.to_datetime(df['OrderDate'])
    
    # Trích xuất các thông tin thời gian
    df['Year'] = df['OrderDate'].dt.year
    df['Month'] = df['OrderDate'].dt.month
    df['Quarter'] = df['OrderDate'].dt.quarter
    
    # Đảm bảo cột Sales và Profit là kiểu số
    df['Sales'] = pd.to_numeric(df['Sales'], errors='coerce')
    
    # Tạo thư mục lưu biểu đồ
    output_dir = 'charts'
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    print("Bắt đầu vẽ các biểu đồ thống kê...")

    # --- 1. Doanh thu theo Năm ---
    plt.figure()
    yearly_sales = df.groupby('Year')['Sales'].sum()
    yearly_sales.plot(kind='bar', color='skyblue', edgecolor='black')
    plt.title('TỔNG DOANH THU THEO NĂM', fontsize=16, fontweight='bold')
    plt.xlabel('Năm', fontsize=12)
    plt.ylabel('Doanh Thu ($)', fontsize=12)
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.savefig(os.path.join(output_dir, 'doanh_thu_theo_nam.png'))
    print("- Đã lưu: doanh_thu_theo_nam.png")

    # --- 2. Doanh thu theo Quý ---
    plt.figure()
    quarterly_sales = df.groupby(['Year', 'Quarter'])['Sales'].sum()
    labels = [f"{y}-Q{q}" for y, q in quarterly_sales.index]
    plt.plot(labels, quarterly_sales.values, marker='o', color='red', linewidth=2)
    plt.xticks(rotation=45)
    plt.title('BIẾN ĐỘNG DOANH THU THEO QUÝ', fontsize=16, fontweight='bold')
    plt.xlabel('Quý', fontsize=12)
    plt.ylabel('Doanh Thu ($)', fontsize=12)
    plt.grid(True, linestyle=':', alpha=0.6)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'doanh_thu_theo_quy.png'))
    print("- Đã lưu: doanh_thu_theo_quy.png")

    # --- 3. Doanh thu theo Tháng (Tổng hợp qua các năm) ---
    plt.figure()
    monthly_sales = df.groupby('Month')['Sales'].sum()
    monthly_sales.plot(kind='line', marker='s', color='green', linewidth=2)
    plt.title('TỔNG DOANH THU THEO THÁNG (Tích lũy)', fontsize=16, fontweight='bold')
    plt.xlabel('Tháng', fontsize=12)
    plt.ylabel('Doanh Thu ($)', fontsize=12)
    plt.xticks(range(1, 13))
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.savefig(os.path.join(output_dir, 'doanh_thu_theo_thang.png'))
    print("- Đã lưu: doanh_thu_theo_thang.png")

    # --- 4. Doanh thu theo loại mặt hàng (Category) ---
    plt.figure()
    category_sales = df.groupby('Category')['Sales'].sum().sort_values()
    category_sales.plot(kind='pie', autopct='%1.1f%%', startangle=140, cmap='Pastel1')
    plt.title('TỶ TRỌNG DOANH THU THEO LOẠI MẶT HÀNG', fontsize=16, fontweight='bold')
    plt.ylabel('') # Ẩn nhãn trục Y
    plt.savefig(os.path.join(output_dir, 'doanh_thu_loai_mat_hang.png'))
    print("- Đã lưu: doanh_thu_loai_mat_hang.png")

    # --- 5. Top 10 Sản phẩm bán chạy nhất ---
    plt.figure()
    top_products = df.groupby('ProductName')['Sales'].sum().sort_values(ascending=False).head(10)
    top_products.sort_values().plot(kind='barh', color='salmon', edgecolor='black')
    plt.title('TOP 10 SẢN PHẨM CÓ DOANH THU CAO NHẤT', fontsize=16, fontweight='bold')
    plt.xlabel('Doanh Thu ($)', fontsize=12)
    plt.ylabel('Tên Sản Phẩm', fontsize=12)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'top_10_san_pham.png'))
    print("- Đã lưu: top_10_san_pham.png")

    print(f"\nPhân tích hoàn tất! Biểu đồ được lưu tại: {os.path.abspath(output_dir)}")

if __name__ == "__main__":
    # Sử dụng đường dẫn tuyệt đối để tránh lỗi
    current_dir = os.path.dirname(os.path.abspath(__file__))
    csv_file = os.path.abspath(os.path.join(current_dir, "sales-data-sample.csv"))
    
    if os.path.exists(csv_file):
        analyze_sales(csv_file)
    else:
        print(f"Lỗi: Không tìm thấy tệp dữ liệu tại {csv_file}")

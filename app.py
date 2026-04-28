import tkinter as tk
from tkinter import ttk, messagebox
from data_loader import DataLoader
from optimizer import AdaboostWeightPredictor, DijkstraPathFinder, RouteOptimizer

class WarehouseGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Hệ Thống Tối Ưu Lộ Trình Gom Đơn - Warehouse Optimizer")
        self.root.geometry("900x600")
        
        # Khởi tạo các lớp xử lý dữ liệu
        self.db = DataLoader()
        self.adaboost = AdaboostWeightPredictor()
        self.dijkstra = DijkstraPathFinder(self.adaboost)
        self.all_orders = []

        self.setup_ui()

    def setup_ui(self):
        # --- Frame chính ---
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # --- Tiêu đề ---
        header = ttk.Label(main_frame, text="TỐI ƯU HÓA LỘ TRÌNH KHO HÀNG", font=("Arial", 16, "bold"))
        header.pack(pady=10)

        # --- Bố cục chia 2 cột ---
        content_frame = ttk.Frame(main_frame)
        content_frame.pack(fill=tk.BOTH, expand=True)

        # CỘT TRÁI: Danh sách đơn hàng
        left_frame = ttk.LabelFrame(content_frame, text=" Danh sách đơn hàng trong SQL ", padding="5")
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)

        columns = ("id", "order_id", "qty", "zones")
        self.tree = ttk.Treeview(left_frame, columns=columns, show="headings", selectmode="extended")
        self.tree.heading("id", text="STT")
        self.tree.heading("order_id", text="Mã Đơn")
        self.tree.heading("qty", text="SL")
        self.tree.heading("zones", text="Khu vực")
        
        self.tree.column("id", width=40)
        self.tree.column("order_id", width=100)
        self.tree.column("qty", width=50)
        self.tree.pack(fill=tk.BOTH, expand=True)

        # CỘT PHẢI: Điều khiển và Kết quả
        right_frame = ttk.Frame(content_frame, padding="5")
        right_frame.pack(side=tk.RIGHT, fill=tk.Y)

        btn_connect = ttk.Button(right_frame, text="1. Kết nối & Tải dữ liệu", command=self.load_data)
        btn_connect.pack(fill=tk.X, pady=5)

        btn_optimize = ttk.Button(right_frame, text="2. Tối ưu đơn đã chọn", command=self.run_optimization)
        btn_optimize.pack(fill=tk.X, pady=5)

        # Khu vực hiển thị kết quả
        self.res_frame = ttk.LabelFrame(right_frame, text=" Thống kê lộ trình ", padding="10")
        self.res_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        self.lbl_dist = ttk.Label(self.res_frame, text="Quãng đường: --")
        self.lbl_dist.pack(anchor=tk.W)
        self.lbl_time = ttk.Label(self.res_frame, text="Thời gian: --")
        self.lbl_time.pack(anchor=tk.W)

        # --- PHẦN DƯỚI: Hiển thị lộ trình đường đi ---
        bottom_frame = ttk.LabelFrame(main_frame, text=" Lộ trình di chuyển chi tiết ", padding="5")
        bottom_frame.pack(fill=tk.X, side=tk.BOTTOM, pady=10)
        
        self.lbl_route = ttk.Label(bottom_frame, text="Chưa có lộ trình", foreground="blue", font=("Consolas", 10, "bold"))
        self.lbl_route.pack(pady=5)

    def load_data(self):
        if self.db.connect():
            self.all_orders = self.db.get_all_orders_from_sql()
            # Xóa bảng cũ
            for item in self.tree.get_children():
                self.tree.delete(item)
            # Thêm dữ liệu mới
            for i, order in enumerate(self.all_orders):
                self.tree.insert("", tk.END, i, values=(
                    i + 1, 
                    order['orderID'], 
                    order['total_quantity'], 
                    ", ".join(order['zones'])
                ))
            messagebox.showinfo("Thành công", f"Đã tải {len(self.all_orders)} đơn hàng!")
        else:
            messagebox.showerror("Lỗi", "Không thể kết nối database!")

    def run_optimization(self):
        # Lấy các đơn hàng người dùng chọn trong Treeview
        selected_items = self.tree.selection()
        if not selected_items:
            messagebox.showwarning("Chú ý", "Vui lòng chọn ít nhất một đơn hàng từ danh sách!")
            return

        selected_orders = [self.all_orders[int(item)] for item in selected_items]

        # Thực hiện logic giống file main.py
        points = [(0, 0)]  # Kho
        for order in selected_orders:
            points.append(order['center_location'])

        # Tính toán
        dist_matrix = self.dijkstra.all_pairs_shortest_paths(points)
        optimizer = RouteOptimizer(dist_matrix, selected_orders)
        result = optimizer.optimize()

        # Cập nhật giao diện
        self.lbl_dist.config(text=f"Quãng đường: {result['total_distance']:.2f} m")
        self.lbl_time.config(text=f"Thời gian: {result['total_time']:.2f} phút")
        self.lbl_route.config(text=" → ".join(result['route']))
        
        messagebox.showinfo("Hoàn tất", "Đã tính toán xong lộ trình tối ưu!")

if __name__ == "__main__":
    root = tk.Tk()
    app = WarehouseGUI(root)
    root.mainloop()
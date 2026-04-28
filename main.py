# main.py
from data_loader import DataLoader
from optimizer import AdaboostWeightPredictor, DijkstraPathFinder, RouteOptimizer

def display_header():
    """Hiển thị header chương trình"""
    print("\n" + "="*70)
    print("   TỐI ƯU ĐƯỜNG ĐI GOM ĐƠN HÀNG TRONG KHO")
    print("   =========================================")
    print("="*70)

def create_order_batches(all_orders, capacity):
    """Chia đơn hàng thành các batches dựa trên capacity"""
    # Sắp xếp đơn hàng theo vị trí để gom những đơn gần nhau
    sorted_orders = sorted(all_orders, key=lambda x: (x['center_location'][0], x['center_location'][1]))
    
    batches = []
    current_batch = []
    current_quantity = 0
    
    for order in sorted_orders:
        if current_quantity + order['total_quantity'] <= capacity:
            current_batch.append(order)
            current_quantity += order['total_quantity']
        else:
            # Nếu batch hiện tại không rỗng, lưu lại
            if current_batch:
                batches.append(current_batch)
            # Bắt đầu batch mới
            current_batch = [order]
            current_quantity = order['total_quantity']
    
    # Thêm batch cuối cùng
    if current_batch:
        batches.append(current_batch)
    
    return batches

def show_orders_from_sql(orders_list):
    """Hiển thị danh sách đơn hàng từ CSV"""
    print("\n DANH SÁCH ĐƠN HÀNG:")
    print("   " + "-"*70)
    print(f"   {'STT':<4} {'Mã đơn':<10} {'Tọa độ X':<12} {'Tọa độ Y':<12} {'SL':<6}")
    print("   " + "-"*70)
    
    for idx, order in enumerate(orders_list, 1):
        x, y = order['center_location']
        print(f"   {idx:<4} {order['orderID']:<10} {x:<12.1f} {y:<12.1f} {order['total_quantity']:<6}")
    
    print("   " + "-"*70)
    return len(orders_list)

def main():
    display_header()

    db = DataLoader()
    if not db.connect():
        print(" Không thể đọc file CSV! Thoát chương trình.")
        return

    print("\n ĐỌC DỮ LIỆU ĐƠN HÀNG TỪ CSV")
    print("-"*50)

    all_orders = db.get_all_orders_from_sql()

    if not all_orders:
        print(" Không có dữ liệu đơn hàng!")
        db.close()
        return

    while True:
        print("   MENU CHÍNH - TỐI ƯU HÓA ĐƯỜNG ĐI GOM ĐƠN")
        print("   1. Bắt đầu tối ưu hóa lộ trình")
        print("   2. Xem danh sách đơn hàng")
        print("   3. Thoát chương trình")
        

        while True:
            try:
                choice = int(input("Nhập lựa chọn (1-3): "))
                if choice in [1, 2, 3]:
                    break
                else:
                    print("Vui lòng chọn 1, 2 hoặc 3!")
            except ValueError:
                print("Vui lòng nhập số nguyên!")
            except KeyboardInterrupt:
                print("\n\n Đã dừng chương trình theo yêu cầu của người dùng.")
                print("Cảm ơn bạn đã sử dụng hệ thống tối ưu hóa!")
                db.close()
                return

        if choice == 1:
            result = run_optimization(db, all_orders)
            if result == "exit":
                break  # Thoát vòng lặp chính

        elif choice == 2:
            total = show_orders_from_sql(all_orders)
            print(f"\nTổng cộng: {total} đơn hàng trong hệ thống")

            input("\n⏎ Nhấn Enter để quay lại menu chính...")

        elif choice == 3:
            break  # Thoát vòng lặp chính

    # Đóng kết nối database khi thoát
    print("\n Cảm ơn bạn đã sử dụng hệ thống tối ưu hóa đường đi gom đơn hàng!")
    print("   Hẹn gặp lại! ")
    db.close()


def run_optimization(db, all_orders):
    """Chạy quá trình tối ưu hóa với dữ liệu đã có"""

    # Giới hạn xe (capacity per batch)
    VEHICLE_CAPACITY = 50  # Mỗi chuyến xe đẩy chở tối đa 50 sản phẩm
    
    print(f"\n Mỗi chuyến xe đẩy chở tối đa {VEHICLE_CAPACITY} sản phẩm")

    #  HIỂN THỊ DANH SÁCH ĐƠN HÀNG 
    total = show_orders_from_sql(all_orders)
    print(f"\nTổng cộng: {total} đơn hàng trong hệ thống")

    # CHIA BATCHES THEO TẢI TRỌNG
    print("\n CHIA BATCHES THEO TẢI TRỌNG")
    print("="*50)
    
    batches = create_order_batches(all_orders, VEHICLE_CAPACITY)
    
    print(f"Đã chia thành {len(batches)} batches:")
    for i, batch in enumerate(batches, 1):
        total_qty = sum(order['total_quantity'] for order in batch)
        print(f"  Batch {i}: {len(batch)} đơn hàng, {total_qty}/{VEHICLE_CAPACITY} sản phẩm")
    
    # Chọn batch để tối ưu
    while True:
        try:
            batch_choice = int(input(f"\nChọn batch (1-{len(batches)}): "))
            if 1 <= batch_choice <= len(batches):
                break
            else:
                print(f"Vui lòng chọn từ 1 đến {len(batches)}!")
        except ValueError:
            print("Vui lòng nhập số nguyên!")
    
    selected_batch = batches[batch_choice - 1]
    selected_orders = selected_batch
    
    print(f"\nĐã chọn Batch {batch_choice}: {len(selected_orders)} đơn hàng")
    
    # Hiển thị chi tiết batch
    print("\n CHI TIẾT BATCH ĐÃ CHỌN:")
    print("="*50)
    total_selected_quantity = 0
    for i, order in enumerate(selected_orders, 1):
        print(f"   {i}. {order['orderID']} - {order['total_quantity']} sản phẩm")
        print(f"      Vị trí: {order['center_location']}")
        total_selected_quantity += order['total_quantity']
    print("="*50)
    print(f"   Tổng số lượng: {total_selected_quantity}/{VEHICLE_CAPACITY} sản phẩm")

    # Tiếp tục với quá trình tối ưu như cũ...
    print(f"\nĐã chọn {len(selected_orders)} đơn hàng để gom")

    # KHỞI TẠO ADABOOST 
    print("\n KHỞI TẠO ADABOOST")
    print("-"*50)
    adaboost = AdaboostWeightPredictor()
    adaboost.train()

    #  KHỞI TẠO DIJKSTRA 
    print("\n KHỞI TẠO DIJKSTRA")
    print("-"*50)
    dijkstra = DijkstraPathFinder(adaboost)

    #  TẠO DANH SÁCH ĐIỂM 
    print("\n  TẠO DANH SÁCH ĐIỂM")
    print("-"*50)
    points = [(0, 0)]  # Kho chính
    for order in selected_orders:
        points.append(order['center_location'])

    print(f"   • Điểm xuất phát (KHO): (0, 0)")
    for i, order in enumerate(selected_orders, 1):
        print(f"   • {order['orderID']}: {order['center_location']}")

    #  TÍNH MA TRẬN KHOẢNG CÁCH 
    print("\n TÍNH ĐƯỜNG ĐI NGẮN NHẤT ")
    print("-"*50)
    dist_matrix = dijkstra.all_pairs_shortest_paths(points)

    #  KẾT QUẢ
    print("\n KẾT QUẢ")
    print("-"*50)
    optimizer = RouteOptimizer(dist_matrix, selected_orders)

    # Tính các quãng đường để so sánh
    default_result = optimizer.get_route_by_order()
    default_distance = default_result[1]  # Thứ tự nhập vào
    
    traditional_distance = optimizer.get_traditional_distance()  # Từng đơn lẻ
    
    # Lấy kết quả tối ưu
    route, total_distance = optimizer.tsp_nearest_neighbor()
    
    # Tạo route names
    route_names = []
    for idx in route:
        if idx == 0:  # depot
            route_names.append("KHO")
        else:
            route_names.append(selected_orders[idx-1]['orderID'])
    
    # Tạo result dictionary để tương thích với code cũ
    result = {
        'route': route_names,
        'total_distance': total_distance,
        'num_stops': len(route) - 2,  # trừ depot đầu và cuối
        'total_time': total_distance / 30  # 30 mét/phút
    }

    # In ma trận khoảng cách
    optimizer.print_distance_matrix()

    #  HIỂN THỊ KẾT QUẢ 
    print("    KẾT QUẢ TỐI ƯU ĐƯỜNG ĐI")

    print(f"\n LỘ TRÌNH GOM ĐƠN:")
    print(f"   {' → '.join(result['route'])}")

    # Tính phần trăm tiết kiệm so với từng đơn lẻ
    if traditional_distance > 0:
        savings_vs_traditional = ((traditional_distance - result['total_distance']) / traditional_distance) * 100
    else:
        savings_vs_traditional = 0
    
    # Tính phần trăm tiết kiệm so với thứ tự mặc định
    if default_distance > 0:
        savings_vs_default = ((default_distance - result['total_distance']) / default_distance) * 100
    else:
        savings_vs_default = 0

    print(f"\n 📊 BẢNG SO SÁNH KPIs:")
    print("="*60)
    print(f"   Phương pháp truyền thống (từng đơn lẻ): {traditional_distance:.2f} mét")
    print(f"   Thứ tự mặc định (theo danh sách):       {default_distance:.2f} mét")
    print(f"   Sau khi tối ưu :         {result['total_distance']:.2f} mét")
    print("="*60)
    print(f"   Tiết kiệm so với từng đơn lẻ:          {savings_vs_traditional:.1f}%")
    print(f"   Tiết kiệm so với thứ tự mặc định:      {savings_vs_default:.1f}%")
    print("="*60)

    print(f"\n THÔNG SỐ THỐNG KÊ BATCH:")
    print(f"   • Tổng số đơn hàng trong batch: {result['num_stops']}")
    print(f"   • Tổng số lượng sản phẩm: {total_selected_quantity}/{VEHICLE_CAPACITY}")
    print(f"   • Thời gian ước tính: {result['total_time']:.2f} phút")
    print(f"   • Tốc độ trung bình: 30 mét/phút")

    print("\n ✅ HOÀN THÀNH TỐI ƯU LỘ TRÌNH BATCH!")
    # ========== MENU SAU KHI HOÀN THÀNH ==========
    print("    MENU SAU KHI HOÀN THÀNH")
    print("   1.  Chạy lại với đơn hàng khác")
    print("   2.  Quay lại menu chính")
    print("   3.  Thoát chương trình")


    while True:
        try:
            next_choice = int(input(" Nhập lựa chọn (1-3): "))
            if next_choice in [1, 2, 3]:
                break
            else:
                print(" Vui lòng chọn 1, 2 hoặc 3!")
        except ValueError:
            print(" Vui lòng nhập số nguyên!")
        except KeyboardInterrupt:
            print("\n\n  Đã dừng chương trình theo yêu cầu của người dùng.")
            print(" Cảm ơn bạn đã sử dụng hệ thống tối ưu hóa!")
            return

    if next_choice == 1:
        # Chạy lại với đơn hàng khác
        print("\n Khởi động lại quá trình tối ưu hóa...")
        return  # Quay lại vòng lặp chính để chọn lại
    elif next_choice == 2:
        # Quay lại menu chính
        print("\n Quay lại menu chính...")
        return  # Quay lại vòng lặp chính
    elif next_choice == 3:
        # Thoát chương trình
        print("\n Cảm ơn bạn đã sử dụng hệ thống tối ưu hóa đường đi gom đơn hàng!")
        print("   Hẹn gặp lại! ")
        return "exit"  # Signal để thoát chương trình
if __name__ == "__main__":
    main()

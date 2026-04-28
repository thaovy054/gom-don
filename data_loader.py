# data_loader.py
import pandas as pd
import numpy as np
import os

class DataLoader:
    
    def __init__(self, orders_csv='orders.csv', products_csv='products.csv'):
        self.orders_csv = orders_csv
        self.products_csv = products_csv
        self.df_orders = None
        self.df_products = None
    
    def connect(self):
        try:
            # Đọc file CSV
            self.df_orders = pd.read_csv(self.orders_csv)
            self.df_products = pd.read_csv(self.products_csv)
            
            # Kiểm tra file có tồn tại
            if self.df_orders.empty:
                print(" Lỗi: File orders.csv trống!")
                return False
            if self.df_products.empty:
                print(" Lỗi: File products.csv trống!")
                return False
                
            print(" Đọc file CSV thành công!")
            return True
        except FileNotFoundError as e:
            print(f" Lỗi: Không tìm thấy file - {e}")
            return False
        except Exception as e:
            print(f" Lỗi đọc file: {e}")
            return False
    
    def get_all_orders_from_sql(self):
        if self.df_orders is None or self.df_products is None:
            print(" Lỗi: Dữ liệu chưa được load!")
            return []
        
        orders = []
        
        # Nhóm các sản phẩm theo order_id
        grouped = self.df_orders.groupby('order_id')
        
        for order_id, group in grouped:
            products = []
            coordinates = []
            total_qty = 0
            
            for _, row in group.iterrows():
                product_id = row['product_id'].strip()
                quantity = int(row['quantity'])
                
                # Lấy tọa độ sản phẩm từ products.csv
                product_data = self.df_products[self.df_products['product_id'] == product_id]
                
                if not product_data.empty:
                    x = float(product_data.iloc[0]['x'])
                    y = float(product_data.iloc[0]['y'])
                    
                    products.append({
                        'productID': product_id,
                        'quantity': quantity,
                        'location': (x, y)
                    })
                    coordinates.append((x, y))
                    total_qty += quantity
            
            if coordinates:
                center_x = np.mean([c[0] for c in coordinates])
                center_y = np.mean([c[1] for c in coordinates])
            else:
                center_x, center_y = 0, 0
            
            orders.append({
                'orderID': order_id,
                'center_location': (center_x, center_y),
                'products': products,
                'total_quantity': total_qty,
                'zones': []
            })
        
        print(f" Đã đọc {len(orders)} đơn hàng từ CSV")
        return orders
    
    def get_order_by_id(self, orderID):
        """Lấy thông tin 1 đơn hàng cụ thể"""
        if self.df_orders is None or self.df_products is None:
            return None
        
        order_data = self.df_orders[self.df_orders['order_id'] == orderID]
        
        if order_data.empty:
            return None
        
        products = []
        coordinates = []
        total_qty = 0
        
        for _, row in order_data.iterrows():
            product_id = row['product_id'].strip()
            quantity = int(row['quantity'])
            
            product_data = self.df_products[self.df_products['product_id'] == product_id]
            
            if not product_data.empty:
                x = float(product_data.iloc[0]['x'])
                y = float(product_data.iloc[0]['y'])
                
                products.append({
                    'productID': product_id,
                    'quantity': quantity,
                    'location': (x, y)
                })
                coordinates.append((x, y))
                total_qty += quantity
        
        if coordinates:
            center_x = np.mean([c[0] for c in coordinates])
            center_y = np.mean([c[1] for c in coordinates])
        else:
            center_x, center_y = 0, 0
        
        return {
            'orderID': orderID,
            'center_location': (center_x, center_y),
            'products': products,
            'total_quantity': total_qty,
            'zones': []
        }
    
    def get_all_order_ids(self):
        """Lấy danh sách mã đơn hàng"""
        if self.df_orders is None:
            return []
        return self.df_orders['order_id'].tolist()
    
    def close(self):
        """Đóng kết nối (không cần cho CSV)"""
        print(" Đã hoàn tất đọc file CSV")

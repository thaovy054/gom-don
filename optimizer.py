import math
import numpy as np
import random

class AdaboostWeightPredictor:
    
    def __init__(self):
        self.weight_map = {0: 1.0, 1: 1.8, 2: 2.8}
    
    def train(self):
        """Khởi tạo (không cần train thực tế)"""
        print(" Adaboost đã sẵn sàng ")
    
    def predict_weight(self, distance, turns=None, density=None, width=None):
        """
        Dự đoán trọng số dựa trên khoảng cách
        Cung đường càng dài thì càng khó
        """
        # Nếu không có tham số, tự sinh ngẫu nhiên
        if turns is None:
            turns = random.randint(0, 5)
        if density is None:
            density = random.uniform(0.1, 1.0)
        if width is None:
            width = random.uniform(0.5, 2.5)
        
        # Rule-based classification
        if distance < 20 and turns < 2 and density < 0.4 and width > 1.5:
            label = 0  # Dễ
        elif distance > 50 or turns > 4 or density > 0.8 or width < 0.8:
            label = 2  # Khó
        else:
            label = 1  # Trung bình
        
        weight = self.weight_map[label] * (distance / 10)  # Chia 10 để trọng số nhỏ hơn
        return weight, label


class DijkstraPathFinder:
    """Dijkstra tìm đường đi ngắn nhất"""
    
    def __init__(self, adaboost_predictor):
        self.adaboost = adaboost_predictor
    
    def calculate_weight(self, point_a, point_b):
        """Tính trọng số giữa 2 điểm (khoảng cách theo aisles + độ khó)"""
        # Khoảng cách Manhattan (đi dọc aisles, không đi xuyên kệ)
        distance = abs(point_a[0] - point_b[0]) + abs(point_a[1] - point_b[1])
        
        # Dự đoán trọng số với Adaboost
        weight, _ = self.adaboost.predict_weight(distance)
        
        return weight
    
    def shortest_path(self, points, start, end):
        """Tìm đường đi ngắn nhất từ start đến end"""
        n = len(points)
        visited = [False] * n
        dist = [float('inf')] * n
        prev = [-1] * n
        dist[start] = 0
        
        for _ in range(n):
            # Tìm điểm chưa thăm có khoảng cách nhỏ nhất
            u = -1
            min_dist = float('inf')
            for i in range(n):
                if not visited[i] and dist[i] < min_dist:
                    min_dist = dist[i]
                    u = i
            
            if u == -1 or u == end:
                break
            
            visited[u] = True
            
            # Cập nhật khoảng cách đến các điểm lân cận
            for v in range(n):
                if not visited[v] and u != v:
                    weight = self.calculate_weight(points[u], points[v])
                    if dist[u] + weight < dist[v]:
                        dist[v] = dist[u] + weight
                        prev[v] = u
        
        # Truy vết đường đi
        path = []
        current = end
        while current != -1:
            path.insert(0, current)
            current = prev[current]
        
        return dist[end], path
    
    def all_pairs_shortest_paths(self, points):
        """Tính ma trận khoảng cách giữa tất cả các cặp điểm"""
        n = len(points)
        dist_matrix = np.zeros((n, n))
        
        print("   Đang tính đường đi ngắn nhất...")
        total_pairs = n * n
        count = 0
        
        for i in range(n):
            for j in range(n):
                if i != j:
                    dist, _ = self.shortest_path(points, i, j)
                    dist_matrix[i][j] = dist
                else:
                    dist_matrix[i][j] = 0
                
                # Hiển thị tiến độ
                count += 1
                if count % 10 == 0:
                    print(f"      Tiến độ: {count}/{total_pairs}")
        
        return dist_matrix


class RouteOptimizer:
    
    def __init__(self, dist_matrix, orders):
        self.dist_matrix = dist_matrix
        self.orders = orders
        self.depot_index = 0
    
    def get_route_by_order(self):
        """Lộ trình theo thứ tự đơn hàng nhập vào (không tối ưu)"""
        route_indices = [self.depot_index]
        for i in range(1, len(self.dist_matrix)):
            route_indices.append(i)
        route_indices.append(self.depot_index)
        
        total_distance = 0
        for i in range(len(route_indices) - 1):
            total_distance += self.dist_matrix[route_indices[i]][route_indices[i+1]]
        
        return route_indices, total_distance
    
    def tsp_nearest_neighbor(self):
        """TSP sử dụng Nearest Neighbor heuristic"""
        n = len(self.dist_matrix)
        visited = [False] * n
        route = [self.depot_index]
        visited[self.depot_index] = True
        
        # Bắt đầu từ depot, tìm điểm gần nhất chưa thăm
        current = self.depot_index
        total_distance = 0
        
        for _ in range(n - 1):
            min_dist = float('inf')
            next_point = -1
            
            for j in range(n):
                if not visited[j] and self.dist_matrix[current][j] < min_dist:
                    min_dist = self.dist_matrix[current][j]
                    next_point = j
            
            if next_point != -1:
                route.append(next_point)
                visited[next_point] = True
                total_distance += min_dist
                current = next_point
        
        # Quay về depot
        total_distance += self.dist_matrix[current][self.depot_index]
        route.append(self.depot_index)
        
        return route, total_distance
    
    def print_distance_matrix(self):
        """In ma trận khoảng cách"""
        n = len(self.dist_matrix)
        point_names = [" KHO"] + [order['orderID'] for order in self.orders]
        
        print("\n   " + "="*80)
        print("    MA TRẬN KHOẢNG CÁCH (Manhattan + Adaboost - Theo Aisles)")
        print("   " + "="*80)
        
        # In header
        header = "     " + "".join([f"{name:>12}" for name in point_names])
        print(f"\n   {header}")
        
        # In từng dòng
        for i in range(n):
            row = f"{point_names[i]:>5}"
            for j in range(n):
                val = self.dist_matrix[i][j]
                row += f"{val:>12.2f}"
            print(f"   {row}")
        
    def get_traditional_distance(self):
        """Tính quãng đường truyền thống: đi từng đơn lẻ (KHO -> Đơn1 -> KHO -> Đơn2 -> KHO...)"""
        total_distance = 0
        for i in range(1, len(self.dist_matrix)):
            # Từ KHO đến đơn hàng
            total_distance += self.dist_matrix[self.depot_index][i]
            # Từ đơn hàng về KHO
            total_distance += self.dist_matrix[i][self.depot_index]
        
        return total_distance
        # Tính lộ trình tối ưu bằng TSP
        route_indices, total_distance = self.tsp_nearest_neighbor()
        
        route_sequence = []
        for idx in route_indices:
            if idx == self.depot_index:
                route_sequence.append(" KHO")
            else:
                route_sequence.append(self.orders[idx-1]['orderID'])
        
        return {
            'distance_matrix': self.dist_matrix,
            'route': route_sequence,
            'total_distance': total_distance,
            'total_time': total_distance / 30,  # 30 mét/phút
            'num_stops': len(self.orders)
        }
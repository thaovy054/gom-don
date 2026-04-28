# Warehouse Order Picking Optimization

This project implements an intelligent order picking system for warehouses using machine learning and graph algorithms.

## Data Structures

### Order
- `orderID`: String - Unique order identifier
- `productList`: List[OrderItem] - List of products in the order
- `totalQuantity`: Integer - Total quantity of all products

### OrderItem
- `productID`: String - Product identifier
- `quantity`: Integer - Quantity needed

## Algorithms

| Algorithm | Operation | Output |
|-----------|-----------|--------|
| Preprocessing | Collect order list: positions (shelf coordinates), weight, priority, deadline | Set of delivery points P = {p₁, p₂, ..., pₙ} |
| Adaboost | Classify path difficulty based on: area density, turns, narrow/wide, congestion history. Labels: Easy, Medium, Hard | Weight coefficients w[i][j] - predicted cost/time for each path |
| Combination | Calculate expected weight matrix: C[i][j] = w[i][j] (based on Adaboost) | Weight matrix C[i][j] |
| Dijkstra | Calculate shortest path between all points (main warehouse + order positions), considering obstacles | Distance matrix D[i][j] = shortest path length from i to j<br>Path matrix P[i][j] = detailed path for tracing |

## Implementation

### Language and Libraries
- **Python** as the main language
- **Pandas** for data processing
- **Scikit-learn** for Adaboost (AdaBoostRegressor)
- **NetworkX** for graph operations and Dijkstra algorithm
- **NumPy** for numerical computations
- **Matplotlib** for visualization (optional)

### Program Structure
The program is organized into modular components for maintainability and scalability:

#### `data_loader.py` - Data Management Module
- **Purpose**: Handles database connections and data loading from SQLite database
- **Functions**:
  - `connect()`: Establishes connection to SQLite database
  - `get_all_orders_from_sql()`: Loads all orders with product details and calculates center locations
  - `get_order_by_id()`: Retrieves specific order information
  - `close()`: Closes database connection
- **Dependencies**: sqlite3, pandas, numpy

#### `optimizer.py` - Optimization Engine Module  
- **Purpose**: Contains the core AI and graph algorithms for route optimization
- **Classes**:
  - `AdaboostWeightPredictor`: Rule-based path difficulty prediction (simplified Adaboost)
  - `DijkstraPathFinder`: Graph-based shortest path calculation with weighted edges
  - `RouteOptimizer`: Route optimization orchestrator and result presentation
- **Dependencies**: math, numpy, random

#### `main.py` - Application Controller Module
- **Purpose**: Coordinates the entire optimization workflow and user interface
- **Functions**:
  - `display_header()`: Shows program title and menu
  - `show_orders_from_sql()`: Displays order list in formatted table
  - `run_optimization()`: Executes the complete optimization pipeline
  - `main()`: Main program loop with user interaction
- **Dependencies**: All other modules
  - `build_cost_matrix()`: Creates edge cost matrix using AI predictions
  - `dijkstra_shortest_paths()`: Computes optimal routes
  - `optimize_routes()`: Main optimization orchestrator
- **Dependencies**: Scikit-learn, NetworkX, NumPy

#### `main.py` - Application Controller Module
- **Purpose**: Coordinates the entire optimization workflow
- **Functions**:
  - `main()`: Executes the complete optimization pipeline
  - `tao_du_lieu_huan_luyen()`: Generates training data for Adaboost
- **Dependencies**: All other modules

#### `data/` - Data Directory
- **Purpose**: Stores input data and configuration files
- **Contents**: CSV files for orders, product locations, and SQL database file

### Core Functions

#### Data Loading (`data_loader.py`)
```python
def get_all_orders_from_sql(self):
    """
    Lấy tất cả đơn hàng từ SQL database và tính toán vị trí trung tâm
    
    Input parameters: None (sử dụng kết nối database đã thiết lập)
    
    Output: 
    - List[Dict] - Danh sách đơn hàng với cấu trúc:
        {
            'orderID': str,           # Mã đơn hàng
            'center_location': tuple, # Tọa độ trung tâm (x, y)
            'products': List[Dict],   # Danh sách sản phẩm
            'total_quantity': int,    # Tổng số lượng
            'zones': List[str]        # Danh sách khu vực
        }
    
    Logic: 
    - JOIN 4 bảng: orders, orderitems, products, locations
    - Tính trung bình có trọng số của tọa độ sản phẩm
    - Gom nhóm theo orderID
    """
    query = """
    SELECT 
        o.orderID,
        oi.productID,
        oi.quantity,
        p.productName,
        p.category,
        l.x, l.y, l.zone
    FROM orders o
    JOIN orderitems oi ON o.orderID = oi.orderID
    JOIN products p ON oi.productID = p.productID
    JOIN locations l ON p.locationID = l.locationID
    """
    
    df = pd.read_sql_query(query, self.connection)
    
    # Gom nhóm theo orderID và tính toán
    orders = []
    for orderID in df['orderID'].unique():
        order_data = df[df['orderID'] == orderID]
        coordinates = list(zip(order_data['x'], order_data['y']))
        center_x = np.mean([c[0] for c in coordinates])
        center_y = np.mean([c[1] for c in coordinates])
        
        # ... (xử lý products và zones)
        orders.append({
            'orderID': orderID,
            'center_location': (center_x, center_y),
            'products': products,
            'total_quantity': total_qty,
            'zones': order_data['zone'].unique().tolist()
        })
    
    return orders
```

#### Adaboost Weight Prediction (`optimizer.py`)
```python
def predict_weight(self, distance, turns=None, density=None, width=None):
    """
    Dự đoán trọng số đường đi dựa trên khoảng cách và yếu tố môi trường
    
    Input parameters:
    - distance (float): Khoảng cách Euclidean giữa 2 điểm (mét)
    - turns (int, optional): Số lần rẽ đường (0-5, mặc định random)
    - density (float, optional): Mật độ sản phẩm xung quanh (0.1-1.0, mặc định random)
    - width (float, optional): Độ rộng lối đi (0.5-2.5m, mặc định random)
    
    Output: 
    - weight (float): Trọng số dự đoán (thấp=dễ, cao=khó)
    - label (int): Nhãn phân loại (0=dễ, 1=trung bình, 2=khó)
    
    Logic "Smart": Rule-based classification:
    - Dễ: distance < 20m AND turns < 2 AND density < 0.4 AND width > 1.5m
    - Khó: distance > 50m OR turns > 4 OR density > 0.8 OR width < 0.8m  
    - Trung bình: Các trường hợp còn lại
    - Weight = weight_map[label] * (distance / 10)
    """
    # Tự sinh tham số ngẫu nhiên nếu không cung cấp
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
    
    weight = self.weight_map[label] * (distance / 10)
    return weight, label
```

#### Dijkstra Shortest Path (`optimizer.py`)
```python
def shortest_path(self, points, start, end):
    """Tìm đường đi ngắn nhất từ start đến end sử dụng Dijkstra với trọng số
    
    Input parameters:
    - points (List[Tuple]): Danh sách tọa độ các điểm [(x1,y1), (x2,y2), ...]
    - start (int): Index của điểm bắt đầu trong danh sách points
    - end (int): Index của điểm kết thúc trong danh sách points
    
    Output:
    - distance (float): Tổng khoảng cách đường đi ngắn nhất
    - path (List[int]): Danh sách index các điểm trong lộ trình tối ưu
    
    Logic "Smart": 
    - Sử dụng Adaboost để tính trọng số cho mỗi cạnh
    - Trọng số = khoảng cách + độ khó dự đoán (không chỉ Euclidean)
    - Tìm đường đi có tổng trọng số nhỏ nhất
    """
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
```

#### Route Optimization (`optimizer.py`)
```python
def optimize(self):
    """Chạy quá trình tối ưu hóa và trả về kết quả
    
    Input parameters: None (sử dụng dist_matrix và orders đã khởi tạo)
    
    Output: Dict chứa kết quả tối ưu hóa:
    - 'distance_matrix': Ma trận khoảng cách
    - 'route': Lộ trình tối ưu ['KHO', 'O01', 'O02', 'KHO']
    - 'total_distance': Tổng quãng đường (float)
    - 'total_time': Thời gian ước tính (float)
    - 'num_stops': Số điểm dừng (int)
    
    Logic: Hiện tại sử dụng lộ trình theo thứ tự đơn hàng (có thể mở rộng TSP)
    """
    route_indices, total_distance = self.get_route_by_order()
    
    # Chuyển đổi sang tên điểm
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
```

## Requirements
Install dependencies:
```bash
pip install pandas>=2.0.0 numpy>=1.24.0
```

## Usage
1. Setup database: Run the SQL script `gom_đơn_kho.sql` to create and populate the SQLite database
2. Run the program: `python main.py`
3. Follow the menu prompts to select orders and optimize routes

## Database Schema
The system uses SQLite with the following tables:
- `Locations`: Product positions in warehouse (x, y coordinates, zone)
- `Products`: Product information (ID, name, category, location)
- `Orders`: Order headers (ID)
- `OrderItems`: Order details (order ID, product ID, quantity)
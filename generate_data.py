import random
import csv

# Generate 50 products
products = []
for i in range(1, 51):
    products.append({
        'product_id': f'P{i:03d}',
        'x': round(random.uniform(0, 100), 1),
        'y': round(random.uniform(0, 100), 1)
    })

# Save product_locations.csv
with open('data/product_locations.csv', 'w', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=['product_id', 'x', 'y'])
    writer.writeheader()
    writer.writerows(products)

print(f"✓ Created {len(products)} products in product_locations.csv")

# Generate 100 orders
orders = []
for i in range(1, 101):
    num_items = random.randint(1, 5)
    selected_products = random.sample(products, num_items)
    
    product_ids = ','.join([p['product_id'] for p in selected_products])
    quantities = ','.join([str(random.randint(1, 10)) for _ in selected_products])
    
    orders.append({
        'order_id': f'ORD{i:03d}',
        'product_ids': product_ids,
        'quantities': quantities
    })

# Save orders.csv
with open('data/orders.csv', 'w', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=['order_id', 'product_ids', 'quantities'])
    writer.writeheader()
    writer.writerows(orders)

print(f"✓ Created {len(orders)} orders in orders.csv")
print(f"✓ Dataset ready for optimization!")

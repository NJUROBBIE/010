import sqlite3

# 连接到数据库
db_file = 'concert_ticketing.db'
conn = sqlite3.connect(db_file)
cursor = conn.cursor()

# 检查各表数据量
tables = [
    'user',
    'singer',
    'concert',
    'event',
    'ticket',
    'orders',
    'seat',
    'rush_record',
    'user_favorite_concert',
    'user_follow_singer',
    'concert_singer'
]

print('数据库各表数据量统计：')
print('-' * 40)

for table in tables:
    cursor.execute(f'SELECT COUNT(*) FROM {table}')
    count = cursor.fetchone()[0]
    print(f'{table:<25} {count:>10} 条记录')

print('-' * 40)

# 检查演唱会数据
cursor.execute('SELECT COUNT(*) FROM concert WHERE concert_id > 3')  # 3是初始数据
new_concerts = cursor.fetchone()[0]
print(f'新生成的演唱会数量: {new_concerts}')

# 检查购票数据
total_orders = cursor.execute('SELECT COUNT(*) FROM orders').fetchone()[0]
total_seats = cursor.execute('SELECT COUNT(*) FROM seat').fetchone()[0]
print(f'总购票订单数量: {total_orders}')
print(f'总购票座位数量: {total_seats}')

# 检查票档剩余数量
cursor.execute('SELECT SUM(total_quantity - remaining_quantity) FROM ticket')
sold_tickets = cursor.fetchone()[0]
print(f'已售出的票档数量: {sold_tickets}')

# 关闭连接
conn.close()

print('\n数据验证完成！')
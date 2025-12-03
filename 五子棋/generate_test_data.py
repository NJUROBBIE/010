import sqlite3
import random
from datetime import datetime, timedelta

# 连接到数据库
db_file = 'concert_ticketing.db'
conn = sqlite3.connect(db_file)
cursor = conn.cursor()

def generate_concerts(num_concerts=100):
    """生成指定数量的演唱会数据"""
    # 随机生成演唱会名称的模板
    concert_templates = [
        '{}全国巡回演唱会',
        '{}世界巡回演唱会',
        '{}2024全新专辑发布会',
        '{}夏日限定演唱会',
        '{}年终盛典演唱会'
    ]
    
    # 随机生成歌手名称
    singer_names = [
        '周杰伦', '陈奕迅', '林俊杰', '五月天', '张学友',
        '刘德华', '王力宏', '陶喆', '孙燕姿', '蔡依林',
        '梁静茹', '张韶涵', '张惠妹', '王菲', '李荣浩',
        '薛之谦', '邓紫棋', '毛不易', '周深', '华晨宇'
    ]
    
    # 随机生成主办方名称
    organizers = [
        '杰威尔音乐有限公司', '英皇娱乐集团', '华纳音乐', '环球音乐',
        '索尼音乐', '滚石唱片', '华研国际音乐', '福茂唱片',
        '太合音乐集团', '网易云音乐'
    ]
    
    concerts = []
    
    # 生成演唱会数据
    for i in range(num_concerts):
        # 随机选择歌手
        singer_name = random.choice(singer_names)
        
        # 随机选择演唱会模板
        template = random.choice(concert_templates)
        concert_name = template.format(singer_name)
        
        # 随机选择主办方
        organizer_name = random.choice(organizers)
        
        # 随机生成演唱会时间（未来1-365天）
        start_date = datetime.now() + timedelta(days=random.randint(1, 365))
        start_time = start_date.strftime('%Y-%m-%d %H:%M:%S')
        
        # 演唱会持续时间（2-3小时）
        duration = random.randint(120, 180)
        end_date = start_date + timedelta(minutes=duration)
        end_time = end_date.strftime('%Y-%m-%d %H:%M:%S')
        
        concerts.append((concert_name, organizer_name, start_time, end_time))
    
    # 插入演唱会数据
    cursor.executemany(
        'INSERT INTO concert (concert_name, organizer_name, start_time, end_time) VALUES (?, ?, ?, ?)',
        concerts
    )
    
    # 获取生成的演唱会ID
    cursor.execute('SELECT concert_id FROM concert ORDER BY concert_id DESC LIMIT ?', (num_concerts,))
    concert_ids = [row[0] for row in cursor.fetchall()]
    
    return concert_ids

def generate_events(concert_ids):
    """为每个演唱会生成场次数据"""
    # 随机生成场馆名称
    venues = [
        '北京国家体育场(鸟巢)', '上海体育场', '广州天河体育场',
        '成都凤凰山体育公园', '深圳湾体育中心', '杭州奥体中心',
        '南京奥林匹克体育中心', '武汉体育中心', '重庆奥体中心',
        '西安奥体中心', '长沙贺龙体育中心', '郑州奥林匹克体育中心'
    ]
    
    events = []
    
    # 为每个演唱会生成1-3个场次
    for concert_id in concert_ids:
        num_events = random.randint(1, 3)
        
        for _ in range(num_events):
            # 随机选择场馆
            venue_id = random.randint(1, 20)  # 假设场馆ID在1-20之间
            venue_name = random.choice(venues)
            
            # 随机生成演出日期（在演唱会开始时间附近）
            cursor.execute('SELECT start_time FROM concert WHERE concert_id = ?', (concert_id,))
            concert_start = cursor.fetchone()[0]
            concert_start_date = datetime.strptime(concert_start, '%Y-%m-%d %H:%M:%S')
            
            # 演出日期在演唱会开始日期前后7天内
            event_date = concert_start_date + timedelta(days=random.randint(-7, 7))
            performance_date = event_date.strftime('%Y-%m-%d')
            
            # 演出时间
            hour = random.randint(18, 20)  # 18:00-20:00之间开始
            minute = random.choice([0, 30])
            performance_start_time = f'{hour:02d}:{minute:02d}:00'
            
            # 演出结束时间（持续2-3小时）
            duration = random.randint(120, 180)
            end_hour = hour + (duration // 60)
            end_minute = minute + (duration % 60)
            if end_minute >= 60:
                end_hour += 1
                end_minute -= 60
            performance_end_time = f'{end_hour:02d}:{end_minute:02d}:00'
            
            events.append((concert_id, venue_id, venue_name, performance_date, performance_start_time, performance_end_time))
    
    # 插入场次数据
    cursor.executemany(
        'INSERT INTO event (concert_id, venue_id, venue_name, performance_date, performance_start_time, performance_end_time) VALUES (?, ?, ?, ?, ?, ?)',
        events
    )
    
    # 获取生成的场次ID
    cursor.execute('SELECT event_id FROM event ORDER BY event_id DESC LIMIT ?', (len(events),))
    event_ids = [row[0] for row in cursor.fetchall()]
    
    return event_ids

def generate_tickets(event_ids):
    """为每个场次生成票档数据"""
    # 票档模板
    ticket_templates = [
        ('看台A区', 'STDA', 580),
        ('看台B区', 'STDB', 780),
        ('看台C区', 'STDC', 980),
        ('内场A区', 'INNA', 1280),
        ('内场B区', 'INNB', 1580),
        ('内场VIP区', 'INNV', 1880),
        ('摇滚区', 'ROCK', 2280)
    ]
    
    tickets = []
    
    # 为每个场次生成3-5个票档
    for event_id in event_ids:
        num_tickets = random.randint(3, 5)
        selected_templates = random.sample(ticket_templates, num_tickets)
        
        for ticket_name, ticket_identifier, base_price in selected_templates:
            # 随机调整价格（±10%）
            price = round(base_price * (1 + random.uniform(-0.1, 0.1)), 2)
            
            # 随机生成总票数（1000-5000）
            total_quantity = random.randint(1000, 5000)
            remaining_quantity = total_quantity
            
            tickets.append((event_id, ticket_name, ticket_identifier, price, total_quantity, remaining_quantity))
    
    # 插入票档数据
    cursor.executemany(
        'INSERT INTO ticket (event_id, ticket_name, ticket_identifier, price, total_quantity, remaining_quantity) VALUES (?, ?, ?, ?, ?, ?)',
        tickets
    )
    
    # 获取生成的票档ID
    cursor.execute('SELECT ticket_id FROM ticket ORDER BY ticket_id DESC LIMIT ?', (len(tickets),))
    ticket_ids = [row[0] for row in cursor.fetchall()]
    
    return ticket_ids

def generate_purchase_data(num_purchases=10000):
    """生成购票数据"""
    # 获取所有用户ID
    cursor.execute('SELECT user_id FROM user')
    user_ids = [row[0] for row in cursor.fetchall()]
    
    # 如果没有用户，创建一些测试用户
    if not user_ids:
        test_users = []
        for i in range(50):
            username = f'test_user_{i}'
            password = 'password123'
            email = f'test_{i}@example.com'
            phone_number = f'138{random.randint(10000000, 99999999)}'
            real_name = f'测试用户{i}'
            test_users.append((username, password, email, phone_number, real_name, 0))
        
        cursor.executemany(
            'INSERT INTO user (username, password, email, phone_number, real_name, is_admin) VALUES (?, ?, ?, ?, ?, ?)',
            test_users
        )
        
        cursor.execute('SELECT user_id FROM user WHERE username LIKE "test_user_%"')
        user_ids = [row[0] for row in cursor.fetchall()]
    
    # 获取所有票档ID
    cursor.execute('SELECT ticket_id FROM ticket')
    ticket_ids = [row[0] for row in cursor.fetchall()]
    
    orders = []
    seats = []
    
    # 生成购票数据
    for i in range(num_purchases):
        # 随机选择用户
        user_id = random.choice(user_ids)
        
        # 随机选择票档
        ticket_id = random.choice(ticket_ids)
        
        # 获取票档信息
        cursor.execute('SELECT event_id, price FROM ticket WHERE ticket_id = ?', (ticket_id,))
        event_id, price = cursor.fetchone()
        
        # 生成订单
        order_amount = price
        payment_status = random.choice([0, 1])  # 0:未支付, 1:已支付
        create_time = (datetime.now() - timedelta(days=random.randint(0, 30))).strftime('%Y-%m-%d %H:%M:%S')
        
        if payment_status == 1:
            payment_time = (datetime.strptime(create_time, '%Y-%m-%d %H:%M:%S') + timedelta(minutes=random.randint(1, 120))).strftime('%Y-%m-%d %H:%M:%S')
        else:
            payment_time = None
        
        orders.append((user_id, order_amount, payment_status, payment_time))
        
        # 插入订单并获取订单ID
        cursor.execute(
            'INSERT INTO orders (user_id, order_amount, payment_status, payment_time) VALUES (?, ?, ?, ?)',
            (user_id, order_amount, payment_status, payment_time)
        )
        order_id = cursor.lastrowid
        
        # 生成座位信息
        seat_number = f'{random.randint(1, 100)}-{random.randint(1, 50)}'
        seat_status = payment_status  # 0:未使用, 1:已使用
        
        seats.append((order_id, ticket_id, event_id, seat_number, seat_status))
        
        # 更新票档剩余数量
        if payment_status == 1:
            cursor.execute(
                'UPDATE ticket SET remaining_quantity = remaining_quantity - 1 WHERE ticket_id = ?',
                (ticket_id,)
            )
        
        # 每100笔订单提交一次事务
        if (i + 1) % 100 == 0:
            conn.commit()
            print(f'已生成 {i + 1}/{num_purchases} 条购票数据')
    
    # 插入所有座位数据
    cursor.executemany(
        'INSERT INTO seat (order_id, ticket_id, event_id, seat_number, seat_status) VALUES (?, ?, ?, ?, ?)',
        seats
    )
    
    return len(orders)

def main():
    print('开始生成测试数据...')
    
    # 1. 生成100场演唱会
    print('正在生成演唱会数据...')
    concert_ids = generate_concerts(100)
    print(f'生成了 {len(concert_ids)} 场演唱会')
    
    # 2. 生成场次数据
    print('正在生成场次数据...')
    event_ids = generate_events(concert_ids)
    print(f'生成了 {len(event_ids)} 个场次')
    
    # 3. 生成票档数据
    print('正在生成票档数据...')
    ticket_ids = generate_tickets(event_ids)
    print(f'生成了 {len(ticket_ids)} 个票档')
    
    # 4. 生成10000条购票数据
    print('正在生成购票数据...')
    num_purchases = generate_purchase_data(10000)
    print(f'生成了 {num_purchases} 条购票数据')
    
    # 提交所有事务并关闭连接
    conn.commit()
    conn.close()
    
    print('测试数据生成完成！')

if __name__ == '__main__':
    main()
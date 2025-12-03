import sqlite3
import os

def init_database():
    # 检查数据库文件是否存在，如果存在则删除（用于重新初始化）
    db_file = 'concert_ticketing.db'
    if os.path.exists(db_file):
        os.remove(db_file)
    
    # 连接到SQLite数据库
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    
    # 创建用户表
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS user (
        user_id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL UNIQUE,
        password TEXT NOT NULL,
        email TEXT,
        phone_number TEXT,
        real_name TEXT,
        is_admin INTEGER DEFAULT 0
    )
    ''')
    
    # 创建歌手表
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS singer (
        singer_id INTEGER PRIMARY KEY AUTOINCREMENT,
        singer_name TEXT NOT NULL,
        description TEXT
    )
    ''')
    
    # 创建演唱会表
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS concert (
        concert_id INTEGER PRIMARY KEY AUTOINCREMENT,
        concert_name TEXT NOT NULL,
        organizer_name TEXT NOT NULL,
        start_time TEXT NOT NULL,
        end_time TEXT
    )
    ''')
    
    # 创建场次表
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS event (
        event_id INTEGER PRIMARY KEY AUTOINCREMENT,
        concert_id INTEGER NOT NULL,
        venue_id INTEGER NOT NULL,
        venue_name TEXT NOT NULL,
        performance_date TEXT NOT NULL,
        performance_start_time TEXT NOT NULL,
        performance_end_time TEXT,
        FOREIGN KEY (concert_id) REFERENCES concert (concert_id)
    )
    ''')
    
    # 创建票档表
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS ticket (
        ticket_id INTEGER PRIMARY KEY AUTOINCREMENT,
        event_id INTEGER NOT NULL,
        ticket_name TEXT NOT NULL,
        ticket_identifier TEXT NOT NULL,
        price REAL NOT NULL,
        total_quantity INTEGER NOT NULL,
        remaining_quantity INTEGER NOT NULL,
        FOREIGN KEY (event_id) REFERENCES event (event_id)
    )
    ''')
    
    # 创建抢票记录表
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS rush_record (
        rush_record_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        event_id INTEGER NOT NULL,
        ticket_id INTEGER NOT NULL,
        rush_result INTEGER DEFAULT 0,
        create_time TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES user (user_id),
        FOREIGN KEY (event_id) REFERENCES event (event_id),
        FOREIGN KEY (ticket_id) REFERENCES ticket (ticket_id)
    )
    ''')
    
    # 创建订单表
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS orders (
        order_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        order_amount REAL NOT NULL,
        payment_status INTEGER DEFAULT 0,
        payment_method TEXT,
        create_time TEXT DEFAULT CURRENT_TIMESTAMP,
        payment_time TEXT,
        FOREIGN KEY (user_id) REFERENCES user (user_id)
    )
    ''')
    
    # 创建座位表
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS seat (
        seat_id INTEGER PRIMARY KEY AUTOINCREMENT,
        order_id INTEGER NOT NULL,
        ticket_id INTEGER NOT NULL,
        event_id INTEGER NOT NULL,
        seat_number TEXT NOT NULL,
        seat_status INTEGER DEFAULT 0,
        FOREIGN KEY (order_id) REFERENCES orders (order_id),
        FOREIGN KEY (ticket_id) REFERENCES ticket (ticket_id),
        FOREIGN KEY (event_id) REFERENCES event (event_id)
    )
    ''')
    
    # 创建用户收藏演唱会表
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS user_favorite_concert (
        user_id INTEGER NOT NULL,
        concert_id INTEGER NOT NULL,
        PRIMARY KEY (user_id, concert_id),
        FOREIGN KEY (user_id) REFERENCES user (user_id),
        FOREIGN KEY (concert_id) REFERENCES concert (concert_id)
    )
    ''')
    
    # 创建用户关注歌手表
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS user_follow_singer (
        user_id INTEGER NOT NULL,
        singer_id INTEGER NOT NULL,
        PRIMARY KEY (user_id, singer_id),
        FOREIGN KEY (user_id) REFERENCES user (user_id),
        FOREIGN KEY (singer_id) REFERENCES singer (singer_id)
    )
    ''')
    
    # 创建演唱会出演歌手表
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS concert_singer (
        concert_id INTEGER NOT NULL,
        singer_id INTEGER NOT NULL,
        PRIMARY KEY (concert_id, singer_id),
        FOREIGN KEY (concert_id) REFERENCES concert (concert_id),
        FOREIGN KEY (singer_id) REFERENCES singer (singer_id)
    )
    ''')
    
    # 插入默认管理员用户
    cursor.execute('''
    INSERT INTO user (username, password, email, phone_number, real_name, is_admin)
    VALUES (?, ?, ?, ?, ?, ?)
    ''', ('admin', 'admin123', 'admin@example.com', '13800138000', '管理员', 1))
    
    # 插入一些测试数据
    # 插入歌手
    singers = [
        ('周杰伦', '华语流行音乐歌手、词曲作家、音乐制作人、演员、导演'),
        ('陈奕迅', '香港流行音乐男歌手、演员'),
        ('林俊杰', '新加坡流行音乐男歌手、词曲作家、音乐制作人')
    ]
    cursor.executemany('INSERT INTO singer (singer_name, description) VALUES (?, ?)', singers)
    
    # 插入演唱会
    concerts = [
        ('周杰伦嘉年华世界巡回演唱会', '杰威尔音乐有限公司', '2024-06-01 19:30:00', '2024-06-01 22:00:00'),
        ('陈奕迅FEAR AND DREAMS世界巡回演唱会', '英皇娱乐集团', '2024-07-15 20:00:00', '2024-07-15 22:30:00'),
        ('林俊杰JJ20世界巡回演唱会', '华纳音乐', '2024-08-20 19:00:00', '2024-08-20 21:30:00')
    ]
    cursor.executemany('INSERT INTO concert (concert_name, organizer_name, start_time, end_time) VALUES (?, ?, ?, ?)', concerts)
    
    # 插入场次
    events = [
        (1, 1, '北京国家体育场(鸟巢)', '2024-06-01', '19:30:00', '22:00:00'),
        (1, 2, '上海体育场', '2024-06-15', '19:30:00', '22:00:00'),
        (2, 3, '广州天河体育场', '2024-07-15', '20:00:00', '22:30:00'),
        (3, 4, '成都凤凰山体育公园', '2024-08-20', '19:00:00', '21:30:00')
    ]
    cursor.executemany('INSERT INTO event (concert_id, venue_id, venue_name, performance_date, performance_start_time, performance_end_time) VALUES (?, ?, ?, ?, ?, ?)', events)
    
    # 插入票档
    tickets = [
        (1, '看台A区', 'STDA', 580.0, 5000, 5000),
        (1, '看台B区', 'STDB', 780.0, 4000, 4000),
        (1, '内场A区', 'INNA', 1280.0, 3000, 3000),
        (1, '内场VIP区', 'INNV', 1880.0, 1000, 1000),
        (2, '看台A区', 'STDA', 680.0, 5000, 5000),
        (2, '看台B区', 'STDB', 880.0, 4000, 4000),
        (2, '内场A区', 'INNA', 1380.0, 3000, 3000),
        (3, '看台A区', 'STDA', 580.0, 5000, 5000),
        (3, '内场A区', 'INNA', 1280.0, 3000, 3000),
        (4, '看台A区', 'STDA', 680.0, 5000, 5000),
        (4, '内场A区', 'INNA', 1380.0, 3000, 3000)
    ]
    cursor.executemany('INSERT INTO ticket (event_id, ticket_name, ticket_identifier, price, total_quantity, remaining_quantity) VALUES (?, ?, ?, ?, ?, ?)', tickets)
    
    # 关联演唱会和歌手
    concert_singers = [
        (1, 1),  # 周杰伦演唱会 - 周杰伦
        (2, 2),  # 陈奕迅演唱会 - 陈奕迅
        (3, 3)   # 林俊杰演唱会 - 林俊杰
    ]
    cursor.executemany('INSERT INTO concert_singer (concert_id, singer_id) VALUES (?, ?)', concert_singers)
    
    # 提交事务并关闭连接
    conn.commit()
    conn.close()
    print("数据库初始化完成！")

if __name__ == "__main__":
    init_database()
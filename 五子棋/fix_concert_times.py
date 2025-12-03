import sqlite3
from datetime import datetime, timedelta

# 连接数据库
conn = sqlite3.connect('concert_ticketing.db')
cursor = conn.cursor()

# 获取当前时间
now = datetime.now()

print('=== 修复前的演唱会和场次时间 ===')
cursor.execute('SELECT concert_id, concert_name, start_time, end_time FROM concert')
concerts = cursor.fetchall()
for concert in concerts:
    print(f'演唱会ID: {concert[0]}, 名称: {concert[1]}, 开始时间: {concert[2]}, 结束时间: {concert[3]}')

cursor.execute('SELECT event_id, concert_id, venue_name, performance_date, performance_start_time FROM event')
events = cursor.fetchall()
for event in events:
    print(f'场次ID: {event[0]}, 演唱会ID: {event[1]}, 场馆: {event[2]}, 日期: {event[3]}, 时间: {event[4]}')

# 修复演唱会时间
for i, concert in enumerate(concerts):
    concert_id = concert[0]
    concert_name = concert[1]
    
    # 设置演唱会开始时间为当前时间后1个月
    start_time = now + timedelta(days=30 + i*15)
    start_time_str = start_time.strftime('%Y-%m-%d %H:%M:%S')
    
    # 设置演唱会结束时间为开始时间后2.5小时
    end_time = start_time + timedelta(hours=2, minutes=30)
    end_time_str = end_time.strftime('%Y-%m-%d %H:%M:%S')
    
    # 更新演唱会时间
    cursor.execute(
        'UPDATE concert SET start_time = ?, end_time = ? WHERE concert_id = ?',
        [start_time_str, end_time_str, concert_id]
    )
    
    print(f'\n修复演唱会 {concert_name} 的时间:')
    print(f'  开始时间: {start_time_str}')
    print(f'  结束时间: {end_time_str}')

# 修复场次时间
for i, event in enumerate(events):
    event_id = event[0]
    concert_id = event[1]
    venue_name = event[2]
    
    # 获取对应的演唱会信息
    cursor.execute('SELECT start_time FROM concert WHERE concert_id = ?', [concert_id])
    concert_start = cursor.fetchone()[0]
    concert_start_time = datetime.strptime(concert_start, '%Y-%m-%d %H:%M:%S')
    
    # 设置场次日期为演唱会开始时间后的1-3天
    performance_date = (concert_start_time + timedelta(days=i+1)).strftime('%Y-%m-%d')
    
    # 设置场次开始时间为演唱会开始时间的时间部分
    performance_start_time = concert_start_time.strftime('%H:%M:%S')
    
    # 更新场次时间
    cursor.execute(
        'UPDATE event SET performance_date = ?, performance_start_time = ? WHERE event_id = ?',
        [performance_date, performance_start_time, event_id]
    )
    
    print(f'\n修复场次 {event_id} 的时间:')
    print(f'  场馆: {venue_name}')
    print(f'  日期: {performance_date}')
    print(f'  时间: {performance_start_time}')

# 提交事务
conn.commit()

print('\n=== 修复后的演唱会和场次时间 ===')
cursor.execute('SELECT concert_id, concert_name, start_time, end_time FROM concert')
concerts = cursor.fetchall()
for concert in concerts:
    print(f'演唱会ID: {concert[0]}, 名称: {concert[1]}, 开始时间: {concert[2]}, 结束时间: {concert[3]}')

cursor.execute('SELECT event_id, concert_id, venue_name, performance_date, performance_start_time FROM event')
events = cursor.fetchall()
for event in events:
    print(f'场次ID: {event[0]}, 演唱会ID: {event[1]}, 场馆: {event[2]}, 日期: {event[3]}, 时间: {event[4]}')

# 关闭连接
conn.close()

print('\n时间修复完成！所有演唱会和场次现在都可以正常购买了。')
import sqlite3
from datetime import datetime, timedelta

# 连接数据库
conn = sqlite3.connect('concert_ticketing.db')
cursor = conn.cursor()

print('=== 演唱会列表 ===')
cursor.execute('SELECT concert_id, concert_name, start_time, end_time FROM concert')
concerts = cursor.fetchall()
for concert in concerts:
    print(f'ID: {concert[0]}, 名称: {concert[1]}, 开始时间: {concert[2]}, 结束时间: {concert[3]}')

print('\n=== 场次列表 ===')
cursor.execute('SELECT event_id, concert_id, venue_name, performance_date, performance_start_time FROM event')
events = cursor.fetchall()
for event in events:
    print(f'ID: {event[0]}, 演唱会ID: {event[1]}, 场馆: {event[2]}, 日期: {event[3]}, 时间: {event[4]}')

# 关闭连接
conn.close()
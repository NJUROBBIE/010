from flask import Flask, request, jsonify, g
import sqlite3
import time
import json
import os
from datetime import datetime

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False

# 数据库路径
DATABASE = 'concert_ticketing.db'

# 获取数据库连接
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db

# 关闭数据库连接
@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

# 执行SQL查询
def query_db(query, args=(), one=False):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv

# 更新数据库
def update_db(query, args=()):
    db = get_db()
    cur = db.execute(query, args)
    db.commit()
    return cur.lastrowid

# 错误响应
def error_response(message, code=400):
    return jsonify({'error': message}), code

# 成功响应
def success_response(data=None, message='success'):
    response = {'status': 'success', 'message': message}
    if data is not None:
        response['data'] = data
    return jsonify(response)

# 用户注册
@app.route('/api/register', methods=['POST'])
def register():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    email = data.get('email', '')
    phone_number = data.get('phone_number', '')
    real_name = data.get('real_name', '')
    
    if not username or not password:
        return error_response('用户名和密码不能为空')
    
    # 检查用户名是否已存在
    existing_user = query_db('SELECT * FROM user WHERE username = ?', [username], one=True)
    if existing_user:
        return error_response('用户名已存在')
    
    # 创建新用户
    user_id = update_db(
        'INSERT INTO user (username, password, email, phone_number, real_name) VALUES (?, ?, ?, ?, ?)',
        [username, password, email, phone_number, real_name]
    )
    
    return success_response({'user_id': user_id, 'username': username}, '注册成功')

# 用户登录
@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return error_response('用户名和密码不能为空')
    
    # 查找用户
    user = query_db('SELECT * FROM user WHERE username = ? AND password = ?', [username, password], one=True)
    if not user:
        return error_response('用户名或密码错误')
    
    # 生成简单的session_token（实际应该使用更安全的方式）
    session_token = f"{user['user_id']}_{int(time.time())}"
    
    return success_response({
        'user_id': user['user_id'],
        'username': user['username'],
        'is_admin': user['is_admin'],
        'session_token': session_token
    }, '登录成功')

# 获取演唱会列表
@app.route('/api/concerts', methods=['GET'])
def get_concerts():
    concerts = query_db('SELECT * FROM concert ORDER BY start_time DESC')
    result = []
    for concert in concerts:
        # 获取演唱会的歌手
        singers = query_db('''
            SELECT s.singer_id, s.singer_name 
            FROM singer s 
            JOIN concert_singer cs ON s.singer_id = cs.singer_id 
            WHERE cs.concert_id = ?
        ''', [concert['concert_id']])
        
        result.append({
            'concert_id': concert['concert_id'],
            'concert_name': concert['concert_name'],
            'organizer_name': concert['organizer_name'],
            'start_time': concert['start_time'],
            'singers': [{'singer_id': s['singer_id'], 'singer_name': s['singer_name']} for s in singers]
        })
    
    return success_response(result)

# 获取演唱会详情
@app.route('/api/concerts/<int:concert_id>', methods=['GET'])
def get_concert_detail(concert_id):
    concert = query_db('SELECT * FROM concert WHERE concert_id = ?', [concert_id], one=True)
    if not concert:
        return error_response('演唱会不存在')
    
    # 获取演唱会的歌手
    singers = query_db('''
        SELECT s.singer_id, s.singer_name 
        FROM singer s 
        JOIN concert_singer cs ON s.singer_id = cs.singer_id 
        WHERE cs.concert_id = ?
    ''', [concert_id])
    
    # 获取演唱会的场次
    events = query_db('SELECT * FROM event WHERE concert_id = ?', [concert_id])
    
    result = {
        'concert_id': concert['concert_id'],
        'concert_name': concert['concert_name'],
        'organizer_name': concert['organizer_name'],
        'start_time': concert['start_time'],
        'end_time': concert['end_time'],
        'singers': [{'singer_id': s['singer_id'], 'singer_name': s['singer_name']} for s in singers],
        'events': [{
            'event_id': e['event_id'],
            'venue_name': e['venue_name'],
            'performance_date': e['performance_date'],
            'performance_start_time': e['performance_start_time']
        } for e in events]
    }
    
    return success_response(result)

# 获取场次的票档信息
@app.route('/api/events/<int:event_id>/tickets', methods=['GET'])
def get_event_tickets(event_id):
    tickets = query_db('SELECT * FROM ticket WHERE event_id = ?', [event_id])
    result = [{
        'ticket_id': t['ticket_id'],
        'ticket_name': t['ticket_name'],
        'price': float(t['price']),
        'remaining_quantity': t['remaining_quantity'],
        'total_quantity': t['total_quantity']
    } for t in tickets]
    
    return success_response(result)

# 抢票功能（使用事务确保并发安全）
@app.route('/api/rush_ticket', methods=['POST'])
def rush_ticket():
    data = request.json
    user_id = data.get('user_id')
    event_id = data.get('event_id')
    ticket_id = data.get('ticket_id')
    
    if not user_id or not event_id or not ticket_id:
        return error_response('参数不完整')
    
    # 记录抢票尝试
    create_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    rush_record_id = update_db(
        'INSERT INTO rush_record (user_id, event_id, ticket_id, rush_result, create_time) VALUES (?, ?, ?, ?, ?)',
        [user_id, event_id, ticket_id, 0, create_time]
    )
    
    db = get_db()
    try:
        # 开启事务
        db.execute('BEGIN TRANSACTION')
        
        # 检查票是否还有剩余（使用FOR UPDATE锁定行）
        ticket = db.execute('SELECT * FROM ticket WHERE ticket_id = ? AND remaining_quantity > 0 FOR UPDATE', [ticket_id]).fetchone()
        if not ticket:
            db.execute('ROLLBACK')
            # 更新抢票记录为失败
            update_db('UPDATE rush_record SET rush_result = -1 WHERE rush_record_id = ?', [rush_record_id])
            return error_response('票已售罄或不存在')
        
        # 减少库存
        db.execute('UPDATE ticket SET remaining_quantity = remaining_quantity - 1 WHERE ticket_id = ?', [ticket_id])
        
        # 获取更新后的票信息，用于生成座位号
        updated_ticket = db.execute('SELECT * FROM ticket WHERE ticket_id = ?', [ticket_id]).fetchone()
        
        # 创建订单
        order_amount = ticket['price']
        order_id = db.execute(
            'INSERT INTO orders (user_id, order_amount, payment_status, create_time) VALUES (?, ?, ?, ?)',
            [user_id, order_amount, 1, create_time]
        ).lastrowid  # 简化处理，直接设置为已支付
        
        # 生成座位号（使用更新后的库存信息）
        seat_number = f"{updated_ticket['ticket_identifier']}-{updated_ticket['total_quantity'] - updated_ticket['remaining_quantity']}"
        
        # 创建座位记录
        db.execute(
            'INSERT INTO seat (order_id, ticket_id, event_id, seat_number, seat_status) VALUES (?, ?, ?, ?, ?)',
            [order_id, ticket_id, event_id, seat_number, 1]
        )
        
        # 更新抢票记录为成功
        db.execute('UPDATE rush_record SET rush_result = 1 WHERE rush_record_id = ?', [rush_record_id])
        
        # 提交事务
        db.commit()
        
        return success_response({
            'order_id': order_id,
            'ticket_id': ticket_id,
            'seat_number': seat_number,
            'order_amount': float(order_amount)
        }, '抢票成功！')
        
    except Exception as e:
        # 发生错误，回滚事务
        db.execute('ROLLBACK')
        # 更新抢票记录为失败
        update_db('UPDATE rush_record SET rush_result = -2 WHERE rush_record_id = ?', [rush_record_id])
        return error_response(f'抢票失败：{str(e)}')

# 获取用户订单列表
@app.route('/api/users/<int:user_id>/orders', methods=['GET'])
def get_user_orders(user_id):
    orders = query_db('SELECT * FROM orders WHERE user_id = ? ORDER BY create_time DESC', [user_id])
    result = []
    
    for order in orders:
        # 获取订单相关的座位信息
        seats = query_db('SELECT * FROM seat WHERE order_id = ?', [order['order_id']])
        seat_info = []
        
        for seat in seats:
            # 获取票档信息
            ticket = query_db('SELECT * FROM ticket WHERE ticket_id = ?', [seat['ticket_id']], one=True)
            # 获取场次信息
            event = query_db('SELECT * FROM event WHERE event_id = ?', [seat['event_id']], one=True)
            # 获取演唱会信息
            concert = query_db('SELECT * FROM concert WHERE concert_id = ?', [event['concert_id']], one=True)
            
            seat_info.append({
                'seat_id': seat['seat_id'],
                'seat_number': seat['seat_number'],
                'ticket_name': ticket['ticket_name'],
                'ticket_price': float(ticket['price']),
                'venue_name': event['venue_name'],
                'performance_date': event['performance_date'],
                'concert_name': concert['concert_name']
            })
        
        result.append({
            'order_id': order['order_id'],
            'order_amount': float(order['order_amount']),
            'payment_status': order['payment_status'],
            'create_time': order['create_time'],
            'seats': seat_info
        })
    
    return success_response(result)

# 收藏演唱会
@app.route('/api/favorite_concert', methods=['POST'])
def favorite_concert():
    data = request.json
    user_id = data.get('user_id')
    concert_id = data.get('concert_id')
    
    if not user_id or not concert_id:
        return error_response('参数不完整')
    
    try:
        update_db(
            'INSERT INTO user_favorite_concert (user_id, concert_id) VALUES (?, ?)',
            [user_id, concert_id]
        )
        return success_response(message='收藏成功')
    except sqlite3.IntegrityError:
        return error_response('已经收藏过该演唱会')

# 取消收藏演唱会
@app.route('/api/unfavorite_concert', methods=['POST'])
def unfavorite_concert():
    data = request.json
    user_id = data.get('user_id')
    concert_id = data.get('concert_id')
    
    if not user_id or not concert_id:
        return error_response('参数不完整')
    
    update_db(
        'DELETE FROM user_favorite_concert WHERE user_id = ? AND concert_id = ?',
        [user_id, concert_id]
    )
    return success_response(message='取消收藏成功')

# 获取用户收藏的演唱会
@app.route('/api/users/<int:user_id>/favorites', methods=['GET'])
def get_user_favorites(user_id):
    favorites = query_db('''
        SELECT c.* FROM concert c
        JOIN user_favorite_concert ufc ON c.concert_id = ufc.concert_id
        WHERE ufc.user_id = ?
    ''', [user_id])
    
    result = []
    for concert in favorites:
        result.append({
            'concert_id': concert['concert_id'],
            'concert_name': concert['concert_name'],
            'organizer_name': concert['organizer_name'],
            'start_time': concert['start_time']
        })
    
    return success_response(result)

# 管理员接口 - 添加演唱会
@app.route('/api/admin/concerts', methods=['POST'])
def admin_add_concert():
    data = request.json
    concert_name = data.get('concert_name')
    organizer_name = data.get('organizer_name')
    start_time = data.get('start_time')
    end_time = data.get('end_time')
    singer_ids = data.get('singer_ids', [])
    
    if not concert_name or not organizer_name or not start_time:
        return error_response('参数不完整')
    
    # 创建演唱会
    concert_id = update_db(
        'INSERT INTO concert (concert_name, organizer_name, start_time, end_time) VALUES (?, ?, ?, ?)',
        [concert_name, organizer_name, start_time, end_time]
    )
    
    # 关联歌手
    for singer_id in singer_ids:
        update_db(
            'INSERT INTO concert_singer (concert_id, singer_id) VALUES (?, ?)',
            [concert_id, singer_id]
        )
    
    return success_response({'concert_id': concert_id}, '演唱会创建成功')

# 管理员接口 - 更新演唱会
@app.route('/api/admin/concerts/<int:concert_id>', methods=['PUT'])
def admin_update_concert(concert_id):
    data = request.json
    concert = query_db('SELECT * FROM concert WHERE concert_id = ?', [concert_id], one=True)
    if not concert:
        return error_response('演唱会不存在')
    
    # 更新演唱会信息
    update_db(
        'UPDATE concert SET concert_name = ?, organizer_name = ?, start_time = ?, end_time = ? WHERE concert_id = ?',
        [data.get('concert_name', concert['concert_name']),
         data.get('organizer_name', concert['organizer_name']),
         data.get('start_time', concert['start_time']),
         data.get('end_time', concert['end_time']),
         concert_id]
    )
    
    # 更新关联歌手（先删除旧的，再添加新的）
    if 'singer_ids' in data:
        update_db('DELETE FROM concert_singer WHERE concert_id = ?', [concert_id])
        for singer_id in data['singer_ids']:
            update_db(
                'INSERT INTO concert_singer (concert_id, singer_id) VALUES (?, ?)',
                [concert_id, singer_id]
            )
    
    return success_response(message='演唱会更新成功')

# 管理员接口 - 删除演唱会
@app.route('/api/admin/concerts/<int:concert_id>', methods=['DELETE'])
def admin_delete_concert(concert_id):
    db = get_db()
    try:
        db.execute('BEGIN TRANSACTION')
        
        # 删除关联数据
        db.execute('DELETE FROM concert_singer WHERE concert_id = ?', [concert_id])
        db.execute('DELETE FROM user_favorite_concert WHERE concert_id = ?', [concert_id])
        
        # 删除场次和相关票档
        events = db.execute('SELECT event_id FROM event WHERE concert_id = ?', [concert_id]).fetchall()
        for event in events:
            event_id = event[0]
            db.execute('DELETE FROM ticket WHERE event_id = ?', [event_id])
            db.execute('DELETE FROM event WHERE event_id = ?', [event_id])
        
        # 删除演唱会
        db.execute('DELETE FROM concert WHERE concert_id = ?', [concert_id])
        db.commit()
        
        return success_response(message='演唱会删除成功')
    except Exception as e:
        db.execute('ROLLBACK')
        return error_response(f'删除失败：{str(e)}')

# 管理员接口 - 添加场次
@app.route('/api/admin/events', methods=['POST'])
def admin_add_event():
    data = request.json
    concert_id = data.get('concert_id')
    venue_id = data.get('venue_id')
    venue_name = data.get('venue_name')
    performance_date = data.get('performance_date')
    performance_start_time = data.get('performance_start_time')
    performance_end_time = data.get('performance_end_time')
    
    if not concert_id or not venue_id or not venue_name or not performance_date or not performance_start_time:
        return error_response('参数不完整')
    
    event_id = update_db(
        'INSERT INTO event (concert_id, venue_id, venue_name, performance_date, performance_start_time, performance_end_time) VALUES (?, ?, ?, ?, ?, ?)',
        [concert_id, venue_id, venue_name, performance_date, performance_start_time, performance_end_time]
    )
    
    return success_response({'event_id': event_id}, '场次添加成功')

# 管理员接口 - 获取所有场次
@app.route('/api/admin/events', methods=['GET'])
def admin_get_events():
    # 获取查询参数
    concert_id = request.args.get('concert_id')
    
    if concert_id:
        events = query_db('SELECT * FROM event WHERE concert_id = ? ORDER BY performance_date DESC', [concert_id])
    else:
        events = query_db('SELECT * FROM event ORDER BY performance_date DESC')
    
    result = []
    for event in events:
        # 获取演唱会名称
        concert = query_db('SELECT concert_name FROM concert WHERE concert_id = ?', [event['concert_id']], one=True)
        concert_name = concert['concert_name'] if concert else '未知演唱会'
        
        result.append({
            'event_id': event['event_id'],
            'concert_id': event['concert_id'],
            'concert_name': concert_name,
            'venue_id': event['venue_id'],
            'venue_name': event['venue_name'],
            'performance_date': event['performance_date'],
            'performance_start_time': event['performance_start_time'],
            'performance_end_time': event['performance_end_time']
        })
    
    return success_response(result)

# 管理员接口 - 删除场次
@app.route('/api/admin/events/<int:event_id>', methods=['DELETE'])
def admin_delete_event(event_id):
    db = get_db()
    try:
        db.execute('BEGIN TRANSACTION')
        
        # 删除关联的票档
        db.execute('DELETE FROM ticket WHERE event_id = ?', [event_id])
        
        # 删除场次
        db.execute('DELETE FROM event WHERE event_id = ?', [event_id])
        db.commit()
        
        return success_response(message='场次删除成功')
    except Exception as e:
        db.execute('ROLLBACK')
        return error_response(f'删除失败：{str(e)}')

# 管理员接口 - 添加票档
@app.route('/api/admin/tickets', methods=['POST'])
def admin_add_ticket():
    data = request.json
    event_id = data.get('event_id')
    ticket_name = data.get('ticket_name')
    # 自动生成ticket_identifier，如果前端没有提供
    ticket_identifier = data.get('ticket_identifier', f"TKT_{event_id}_{int(time.time())}")
    price = data.get('price')
    total_quantity = data.get('total_quantity')
    
    if not event_id or not ticket_name or not price or not total_quantity:
        return error_response('参数不完整')
    
    ticket_id = update_db(
        'INSERT INTO ticket (event_id, ticket_name, ticket_identifier, price, total_quantity, remaining_quantity) VALUES (?, ?, ?, ?, ?, ?)',
        [event_id, ticket_name, ticket_identifier, price, total_quantity, total_quantity]
    )
    
    return success_response({'ticket_id': ticket_id}, '票档添加成功')

# 管理员接口 - 获取票档列表
@app.route('/api/admin/tickets', methods=['GET'])
def admin_get_tickets():
    # 获取查询参数
    event_id = request.args.get('event_id')
    
    if event_id:
        tickets = query_db('SELECT * FROM ticket WHERE event_id = ?', [event_id])
    else:
        tickets = query_db('SELECT * FROM ticket')
    
    result = []
    for ticket in tickets:
        # 获取场次信息
        event = query_db('SELECT * FROM event WHERE event_id = ?', [ticket['event_id']], one=True)
        if event:
            # 获取演唱会信息
            concert = query_db('SELECT concert_name FROM concert WHERE concert_id = ?', [event['concert_id']], one=True)
            concert_name = concert['concert_name'] if concert else '未知演唱会'
            
            result.append({
                'ticket_id': ticket['ticket_id'],
                'event_id': ticket['event_id'],
                'concert_name': concert_name,
                'venue_name': event['venue_name'],
                'performance_date': event['performance_date'],
                'ticket_name': ticket['ticket_name'],
                'price': float(ticket['price']),
                'total_quantity': ticket['total_quantity'],
                'remaining_quantity': ticket['remaining_quantity']
            })
    
    return success_response(result)

# 管理员接口 - 删除票档
@app.route('/api/admin/tickets/<int:ticket_id>', methods=['DELETE'])
def admin_delete_ticket(ticket_id):
    try:
        # 删除票档
        update_db('DELETE FROM ticket WHERE ticket_id = ?', [ticket_id])
        return success_response(message='票档删除成功')
    except Exception as e:
        return error_response(f'删除失败：{str(e)}')

# 管理员接口 - 获取所有订单
@app.route('/api/admin/orders', methods=['GET'])
def admin_get_orders():
    # 可以添加过滤和分页参数
    orders = query_db('SELECT * FROM orders ORDER BY create_time DESC')
    result = []
    
    for order in orders:
        # 获取用户信息
        user = query_db('SELECT * FROM user WHERE user_id = ?', [order['user_id']], one=True)
        # 获取座位信息
        seats = query_db('SELECT * FROM seat WHERE order_id = ?', [order['order_id']])
        
        seat_info = []
        for seat in seats:
            ticket = query_db('SELECT * FROM ticket WHERE ticket_id = ?', [seat['ticket_id']], one=True)
            event = query_db('SELECT * FROM event WHERE event_id = ?', [seat['event_id']], one=True)
            concert = query_db('SELECT * FROM concert WHERE concert_id = ?', [event['concert_id']], one=True)
            
            seat_info.append({
                'seat_number': seat['seat_number'],
                'ticket_name': ticket['ticket_name'],
                'concert_name': concert['concert_name'],
                'venue_name': event['venue_name'],
                'performance_date': event['performance_date']
            })
        
        result.append({
            'order_id': order['order_id'],
            'username': user['username'],
            'order_amount': float(order['order_amount']),
            'payment_status': order['payment_status'],
            'create_time': order['create_time'],
            'seats': seat_info
        })
    
    return success_response(result)

# 管理员接口 - 获取所有用户
@app.route('/api/admin/users', methods=['GET'])
def admin_get_users():
    users = query_db('SELECT * FROM user')
    result = [{
        'user_id': u['user_id'],
        'username': u['username'],
        'email': u['email'],
        'phone_number': u['phone_number'],
        'real_name': u['real_name'],
        'is_admin': u['is_admin']
    } for u in users]
    
    return success_response(result)

# 管理员接口 - 添加歌手
@app.route('/api/admin/singers', methods=['POST'])
def admin_add_singer():
    data = request.json
    singer_name = data.get('singer_name')
    description = data.get('description', '')
    
    if not singer_name:
        return error_response('歌手名称不能为空')
    
    singer_id = update_db(
        'INSERT INTO singer (singer_name, description) VALUES (?, ?)',
        [singer_name, description]
    )
    
    return success_response({'singer_id': singer_id}, '歌手添加成功')

# 管理员接口 - 获取所有演唱会
@app.route('/api/admin/concerts', methods=['GET'])
def admin_get_concerts():
    concerts = query_db('SELECT * FROM concert ORDER BY start_time DESC')
    result = []
    for concert in concerts:
        # 获取演唱会的歌手
        singers = query_db('''
            SELECT s.singer_id, s.singer_name 
            FROM singer s 
            JOIN concert_singer cs ON s.singer_id = cs.singer_id 
            WHERE cs.concert_id = ?
        ''', [concert['concert_id']])
        
        result.append({
            'concert_id': concert['concert_id'],
            'concert_name': concert['concert_name'],
            'organizer_name': concert['organizer_name'],
            'start_time': concert['start_time'],
            'end_time': concert['end_time'],
            'singers': [{'singer_id': s['singer_id'], 'singer_name': s['singer_name']} for s in singers]
        })
    
    return success_response(result)

# 管理员接口 - 获取单个演唱会详情
@app.route('/api/admin/concerts/<int:concert_id>', methods=['GET'])
def admin_get_concert_detail(concert_id):
    concert = query_db('SELECT * FROM concert WHERE concert_id = ?', [concert_id], one=True)
    if not concert:
        return error_response('演唱会不存在')
    
    # 获取演唱会的歌手
    singers = query_db('''
        SELECT s.singer_id, s.singer_name 
        FROM singer s 
        JOIN concert_singer cs ON s.singer_id = cs.singer_id 
        WHERE cs.concert_id = ?
    ''', [concert_id])
    
    result = {
        'concert_id': concert['concert_id'],
        'concert_name': concert['concert_name'],
        'organizer_name': concert['organizer_name'],
        'start_time': concert['start_time'],
        'end_time': concert['end_time'],
        'singers': [{'singer_id': s['singer_id'], 'singer_name': s['singer_name']} for s in singers]
    }
    
    return success_response(result)

# 管理员接口 - 获取所有歌手
@app.route('/api/admin/singers', methods=['GET'])
def admin_get_singers():
    singers = query_db('SELECT * FROM singer')
    result = [{
        'singer_id': s['singer_id'],
        'singer_name': s['singer_name'],
        'description': s['description']
    } for s in singers]
    
    return success_response(result)

# 管理员接口 - 获取歌手的演唱会
@app.route('/api/admin/singers/<int:singer_id>/concerts', methods=['GET'])
def admin_get_singer_concerts(singer_id):
    # 获取歌手信息
    singer = query_db('SELECT * FROM singer WHERE singer_id = ?', [singer_id], one=True)
    if not singer:
        return error_response('歌手不存在')
    
    # 获取歌手的演唱会
    concerts = query_db('''
        SELECT c.* FROM concert c
        JOIN concert_singer cs ON c.concert_id = cs.concert_id
        WHERE cs.singer_id = ?
        ORDER BY c.start_time DESC
    ''', [singer_id])
    
    result = []
    for concert in concerts:
        # 获取演唱会的其他歌手
        singers = query_db('''
            SELECT s.singer_id, s.singer_name 
            FROM singer s 
            JOIN concert_singer cs ON s.singer_id = cs.singer_id 
            WHERE cs.concert_id = ?
        ''', [concert['concert_id']])
        
        result.append({
            'concert_id': concert['concert_id'],
            'concert_name': concert['concert_name'],
            'organizer_name': concert['organizer_name'],
            'start_time': concert['start_time'],
            'end_time': concert['end_time'],
            'singers': [{'singer_id': s['singer_id'], 'singer_name': s['singer_name']} for s in singers]
        })
    
    return success_response(result)

# CORS支持
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,POST,PUT,DELETE,OPTIONS')
    return response

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
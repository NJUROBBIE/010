# 演唱会抢票系统

一个基于Python Flask和SQLite的演唱会抢票系统，支持用户注册、登录、查看演唱会信息、抢票、收藏等功能。

## 技术栈

- **后端框架**: Python Flask
- **数据库**: SQLite
- **前端**: HTML, Bootstrap 5
- **API测试**: 内置测试页面

## 环境要求

- Python 3.7+  
- pip 包管理工具

## 安装步骤

### 1. 安装依赖

首先，确保你已经安装了Python 3.7+。然后，安装项目所需的依赖：

```bash
pip install flask
```

### 2. 初始化数据库

运行以下命令初始化数据库，创建所需的表结构并插入测试数据：

```bash
python init_db.py
```

执行成功后，会在项目根目录生成 `concert_ticketing.db` 数据库文件。

## 运行步骤

### 1. 启动后端服务器

运行以下命令启动Flask开发服务器：

```bash
python server.py
```

服务器将在 `http://127.0.0.1:5000` 上运行。

### 2. 访问系统

#### 2.1 普通用户界面

在浏览器中打开 `index.html` 文件，即可进入用户界面：

```
index.html
```

#### 2.2 管理员界面

在浏览器中打开 `admin.html` 文件，即可进入管理员界面：

```
admin.html
```

#### 2.3 API测试界面

在浏览器中打开 `test_api.html` 文件，即可进入API测试界面：

```
test_api.html
```

## 使用说明

### 1. 普通用户功能

- **注册**: 在用户界面或API测试页面注册新用户
- **登录**: 使用注册的账号登录系统
- **查看演唱会**: 浏览所有演唱会信息
- **查看演唱会详情**: 查看具体演唱会的场次和票档信息
- **抢票**: 选择场次和票档进行抢票
- **查看订单**: 查看已购买的订单
- **收藏演唱会**: 收藏感兴趣的演唱会

### 2. 管理员功能

管理员默认账号：
- 用户名: `admin`
- 密码: `admin123`

管理员可以：
- 添加、更新、删除演唱会
- 添加场次和票档
- 添加歌手
- 查看所有用户和订单

### 3. API测试

在API测试页面，你可以测试所有后端API，包括：
- 用户注册和登录
- 获取演唱会列表和详情
- 获取场次票档信息
- 抢票功能
- 查看订单
- 收藏/取消收藏演唱会

## API接口列表

### 用户相关

- `POST /api/register` - 用户注册
- `POST /api/login` - 用户登录

### 演唱会相关

- `GET /api/concerts` - 获取演唱会列表
- `GET /api/concerts/<int:concert_id>` - 获取演唱会详情
- `GET /api/events/<int:event_id>/tickets` - 获取场次票档信息

### 抢票相关

- `POST /api/rush_ticket` - 抢票
- `GET /api/users/<int:user_id>/orders` - 获取用户订单

### 收藏相关

- `POST /api/favorite_concert` - 收藏演唱会
- `POST /api/unfavorite_concert` - 取消收藏演唱会
- `GET /api/users/<int:user_id>/favorites` - 获取用户收藏列表

### 管理员相关

- `POST /api/admin/concerts` - 添加演唱会
- `PUT /api/admin/concerts/<int:concert_id>` - 更新演唱会
- `DELETE /api/admin/concerts/<int:concert_id>` - 删除演唱会
- `POST /api/admin/events` - 添加场次
- `POST /api/admin/tickets` - 添加票档
- `GET /api/admin/orders` - 获取所有订单
- `GET /api/admin/users` - 获取所有用户
- `POST /api/admin/singers` - 添加歌手
- `GET /api/admin/singers` - 获取所有歌手

## 项目结构

```
EasyCatch/
├── admin.html          # 管理员界面
├── concert_ticketing.db  # SQLite数据库文件
├── index.html          # 用户界面
├── init_db.py          # 数据库初始化脚本
├── server.py           # Flask后端服务器
├── test_api.html       # API测试页面
└── README.md           # 项目说明文档
```

## 注意事项

1. 本项目使用Flask开发服务器，仅用于开发和测试环境，生产环境建议使用WSGI服务器（如Gunicorn）
2. 数据库使用SQLite，适合小型应用，如需扩展可考虑迁移到MySQL或PostgreSQL
3. 抢票功能使用了数据库事务确保并发安全
4. 所有API支持CORS，可以直接从前端页面调用

## 开发说明

如需修改或扩展项目：

1. 修改 `server.py` 文件可以添加新的API或修改现有逻辑
2. 修改 `init_db.py` 文件可以调整数据库结构或测试数据
3. 修改HTML文件可以调整前端界面

## 许可证

本项目采用MIT许可证，可自由使用和修改。
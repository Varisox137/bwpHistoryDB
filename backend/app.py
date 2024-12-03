# -*- coding: utf-8 -*-
# 框架和插件
import flask
from flask import Flask, request, jsonify, render_template
from flask_migrate import Migrate
from sqlalchemy import inspect
# 内置模块
import os
import datetime as dt
from json import load as jlf
from hashlib import sha256
from secrets import token_hex
# 本地模块
from config import Config
from models import db
import models

app=Flask(__name__)
# 加载配置
app.config.from_object(Config())
# 初始化数据库接口对象
db.init_app(app)
# 初始化数据库迁移对象
migrate=Migrate(app, db)

# 定义API接口路径前缀
API_PREFIX='/api/v1'

# 定义用于验证请求的配置字典
CONFIGS=dict()

# 定义用于查询的字段类型映射字典
FIELDS_TYPE_MAPPING={
    'SS': {
        'ssid': (True, True, 'int'), # 是否数据库要求非空，是否在前端编辑时必填，字段类型
        'ss_pack': (True, True, 'str'),
        'from_ssid': (False, False, 'int'), # 可空，非必填
        'ss_name': (True, True, 'str'),
        'ssvid': (True, True, 'int'),
        'Default': {'int': 'ssid', 'str': 'ss_name'},
    },
    'SS_Version': {
        'ssvid': (True, True, 'int'),
        'ss_update_time': (False, False, 'date'), # 可空，非必填
        'ss_type': (True, True, 'str'),
        'ss_color': (True, True, 'str'),
        'ss_atk': (True, True, 'int'),
        'ss_hp': (True, True, 'int'),
        'ss_desc': (True, False, 'str'), # 非空，非必填，由前端改为空字符串
        'Default': {'int': 'ssvid', 'str':'ss_desc'},
    },
    'Card': {
        'cid': (True, True, 'int'),
        'ssid': (False, False, 'int'), # 可空，非必填
        'card_name': (True, True, 'str'),
        'card_rarity': (True, True, 'str'),
        'cvid': (True, True, 'int'),
        'Default': {'int': 'cid', 'str': 'card_name'},
    },
    'Card_Version': {
        'cvid': (True, True, 'int'),
        'card_update_time': (False, False, 'date'), # 可空，非必填
        'card_type': (True, True, 'str'),
        'card_level': (True, True, 'int'),
        'card_desc': (True, False, 'str'), # 非空，非必填，由前端改为空字符串
        'card_has_target': (True, True, 'int'),
        'zd_atk': (True, False, 'int'), # 非空，非必填，由前端改为0
        'zd_shd': (True, False, 'int'), # 非空，非必填，由前端改为0
        'xt_atk': (True, False, 'int'), # 非空，非必填，由前端改为0
        'xt_hp': (True, False, 'int'), # 非空，非必填，由前端改为0
        'hj_dur': (True, False, 'int'), # 非空，非必填，由前端改为0
        'incl_jx': (True, True, 'int'),
        'jx_atk': (True, False, 'int'), # 非空，非必填，由前端改为0
        'jx_hp': (True, False, 'int'), # 非空，非必填，由前端改为0
        'Default': {'int': 'cvid', 'str': 'card_desc'},
    }
}
# 定义用于检查新增或修改的部分字段允许值列表的字典
FIELDS_VALUE_LISTS={
    'SS.ss_pack': [
        '经典', '不夜之火', '月夜幻响', '沧海刀鸣', '吉运缘结',
        '四相琉璃', '善恶无明', '繁花入梦', '浮生方醒', '喧哗烩战',
        '空弦绮话', '振剑归川', '远山遥泽', '鸣雷启蛰', '燃灯志异',
        '尘世轮回', '桃源故里', '祝星启明', '湮灭双生', '千录晴诗'
    ],
    'SS_Version.ss_type': [
        '式神', '召唤物'
    ],
    'SS_Version.ss_color': [
        '红莲', '紫岩', '青岚', '苍叶', '无'
    ],
    'Card.card_rarity': [
        'R', 'SR', 'SSR'
    ],
    'Card_Version.card_type': [
        '法术', '战斗', '形态', '幻境'
    ],
    'Card_Version.card_level': [
        1, 2, 3
    ],
    'Card_Version.card_has_target': [
        0, 1, 2 # 0表示无目标，1表示强制有目标，2表示非强制有目标
    ],
    'Card_Version.incl_jx': [
        True, False
    ]
}

# 以下部分用于浏览器访问
# # 象征性的首页
@app.route('/', methods=['GET', 'POST'], endpoint='index')
def index():
    return render_template('index.html')

# # 选项卡的图标
@app.route('/favicon.ico', methods=['GET'], endpoint='icon')
def get_icon():
    return app.send_static_file('appicon.ico')

# # 用于处理HTTP 404错误并返回自定义的页面
@app.errorhandler(404)
def page_not_found(e):
    if not request.headers.get('User-Agent', '').startswith(CONFIGS.get('user-agent')):
        return render_template('404.html'), 404
    else:
        return make_response(404, 'Not found')

# 定义统一的响应格式
def make_response(status_code=200, message='Success', data=None):
    if data is None: data=dict()
    return jsonify({'message': message, 'data': data}), status_code

# 定义用于验证请求的装饰器
def validate_request(check_user_agent:bool=True,
                     check_login_level:int=1,
                     check_data:bool=True)->callable:
    def decorator(func):
        def wrapper(*args, **kwargs):
            if check_user_agent:
                user_agent=request.headers.get('User-Agent', '')
                if not user_agent.startswith(CONFIGS.get('user-agent')):
                    return make_response(403, 'Forbidden')
            if check_login_level: # 登录级别验证
                user_id=request.headers.get('Authentication', '0')
                if not user_id.isdigit():
                    return make_response(403, 'Invalid authentication')
                user_id=int(user_id)
                user_data=models.User.query.filter_by(uid=user_id).first()
                if not user_data:
                    # 未提供用户信息
                    return make_response(403, 'Unauthenticated')
                elif not user_data.login_status:
                    # 用户不在线
                    return make_response(403, 'Offline')
                else:
                    # 目前已确认提供了在线用户的uid，首先检查是否登录超时
                    last_online_time=user_data.last_online_time
                    current_time=dt.datetime.now(dt.timezone.utc)
                    if not last_online_time or current_time-last_online_time>dt.timedelta(seconds=CONFIGS.get('login_timeout')):
                        # 登录超时，需要重新登录
                        user_data.login_status=False # 设置用户登录状态为False
                        db.session.commit()
                        return make_response(403, 'Timeout')
                    # 对于需要管理员权限的操作，检查用户类型是否符合
                    if check_login_level==2 and user_data.user_type!='admin':
                        return make_response(403, 'Unauthorized')
            if check_data:
                data=request.get_json(silent=True) # 数据为空时返回None，不使用内置的HTTP 415错误
                if not data:
                    return make_response(403, 'Empty data')

            return func(*args, **kwargs)
        return wrapper
    return decorator

@app.route('/get_api_prefix', methods=['GET'], endpoint='get_api_prefix')
@validate_request(check_login_level=0, check_data=False)
def get_api_prefix():
    data={'api_prefix': API_PREFIX}
    return make_response(data=data)

@app.route(f'{API_PREFIX}/register', methods=['POST'], endpoint='register')
@validate_request(check_login_level=0)
def register():
    def check_reg_key(reg_key:str)->bool:
        seq=[1,0,3,7,4,2,5,6] # 用于打乱截取的哈希值的一部分
        host_name=os.getenv('COMPUTERNAME', default='LocalMachine') # 本机计算机名
        admin_data_list=models.User.query.filter_by(user_type='admin').all()
        seeds=[f'{host_name}*']+[f'{host_name}#{admin_data.uid}' for admin_data in admin_data_list]
        hash_pool=[sha256(seed.encode('utf-8')).hexdigest() for seed in seeds]
        pool=list()
        for hash_str in hash_pool:
            pool.append(''.join([hash_str[i] for i in seq]))
        return reg_key in pool

    data=request.get_json()
    username=data.get('username', '')
    pwd_hash=data.get('pwd_hash', '')
    if not username or not pwd_hash:
        return make_response(400, 'Empty fields')
    # 检查用户名是否已存在
    user_data=models.User.query.filter_by(username=username).first()
    if user_data:
        return make_response(400, 'Existing username')
    # 能够正常注册，检查注册邀请码是否合法，以确定注册的用户类型
    reg_key=data.get('reg_key', '')
    if reg_key and check_reg_key(reg_key):
        user_type='admin'
    else:
        user_type='player'
        reg_key='' # 无效的注册邀请码重置为空字符串
    # 使用secrets模块生成盐值
    salt=token_hex(16) # 生成的16进制字符串长度是随机字节数的两倍
    # 使用SHA-256计算密码的加盐哈希值
    pwd_double_hash=sha256((pwd_hash+salt).encode('utf-8')).hexdigest()
    # 创建用户数据对象并保存到数据库
    new_user_data=models.User(user_type=user_type,
                              username=username, pwd_salt=salt, salted_hash=pwd_double_hash,
                              reg_key=reg_key)
    db.session.add(new_user_data)
    db.session.commit()
    # 返回注册成功的响应
    return make_response(data={'new_uid': new_user_data.uid, 'user_type': user_type})

@app.route(f'{API_PREFIX}/login', methods=['POST'], endpoint='login')
@validate_request(check_login_level=0)
def login():
    data=request.get_json()
    username=data.get('username', '')
    pwd_hash=data.get('pwd_hash', '')
    if not username or not pwd_hash:
        return make_response(400, 'Empty fields')
    # 查询用户数据
    user_data=models.User.query.filter_by(username=username).first()
    if not user_data:
        return make_response(400, 'Unknown username')
    # 验证密码
    salt=user_data.pwd_salt
    pwd_double_hash=sha256((pwd_hash+salt).encode('utf-8')).hexdigest()
    if pwd_double_hash!=user_data.salted_hash:
        return make_response(400, 'Unmatched hash')
    # 更新用户登录状态和最后在线时间
    user_data.login_status=True
    user_data.last_online_time=dt.datetime.now(dt.timezone.utc)
    db.session.commit()
    # 返回登录成功的响应
    return make_response(data={'uid': user_data.uid, 'user_type': user_data.user_type})

@app.route(f'{API_PREFIX}/keep_alive', methods=['POST'], endpoint='keep_alive')
@validate_request(check_data=False)
def keep_alive():
    # 这里不必再进行判断，因为validate_request装饰器已经保证了登录状态
    user_id=request.headers.get('Authentication')
    user_data=models.User.query.filter_by(uid=int(user_id)).first()
    user_data.last_online_time=dt.datetime.now(dt.timezone.utc)
    db.session.commit()
    # 无响应内容
    return make_response(204)

@app.route(f'{API_PREFIX}/logout', methods=['POST'], endpoint='logout')
@validate_request(check_data=False)
def logout():
    # 同样不必再进行判断，由validate_request保证用户的登录状态
    user_id=request.headers.get('Authentication')
    user_data=models.User.query.filter_by(uid=int(user_id)).first()
    user_data.login_status=False
    db.session.commit()
    # 无响应内容
    return make_response(204)

@app.route(f'{API_PREFIX}/query', methods=['POST'], endpoint='query')
@validate_request()
def query():
    # 导入Date类，需要用来解析日期字符串
    from datetime import date
    # 解析请求参数
    data=request.get_json()
    item_model=data.get('item_model', '')
    query_field=data.get('query_field', '')
    search_value=data.get('search_value', '')
    print(f'\nQuerying {item_model=} with {query_field=} and {search_value=}')
    if not item_model:
        # 没有指定要查询的表名
        return make_response(400, 'Empty item_model')
    # 保证了表名非空，然后查询数据模型是否存在
    item_class=getattr(models, item_model, None)
    if not item_class:
        # 数据模型不存在
        return make_response(400, 'Unknown item_model')
    # 以下保证了数据模型存在，开始逐步考虑查询请求
    inspector=inspect(item_class)
    primary_key=inspector.primary_key[0].name # 动态获取数据模型的主键字段名
    data_fields=item_class.fields # 获取数据模型的所有字段
    if not search_value:
        # 没有指定搜索值，则返回表中的全部数据
        data_list=(item_class.query
                   .order_by(getattr(item_class, primary_key).asc())
                   .all())
        data_list=[item.to_dict() for item in data_list]
        return make_response(data={'fields': data_fields, 'list': data_list})
    # 以下保证了数据模型存在、且搜索值非空，首先检查搜索值的类型是否为字符串
    print(f'{search_value=}')
    if not isinstance(search_value, str):
        # 搜索值类型错误
        return make_response(400, 'Invalid search_value')
    # 以下保证了数据模型存在、搜索值非空且类型合理，接下来考虑要查询的字段
    if not query_field or query_field=='Default':
        # 搜索值非空，但未指定查询字段，或者指定使用默认字段
        default_fields=FIELDS_TYPE_MAPPING[item_model]['Default']
        # 根据搜索值类型，选择相应的默认字段
        if isinstance(search_value, int):
            query_field=default_fields['int']
        else: # isinstance(search_value, str)
            query_field=default_fields['str']
    # 查询字段非空且不为默认，继续检查查询字段是否存在
    elif query_field not in FIELDS_TYPE_MAPPING[item_model].keys():
        # 无效的查询字段
        return make_response(400, 'Invalid query_field')
    # 查询字段非空、非默认、修改为非默认、存在于模型字段映射字典中，于是获取相应的字段类型和模型字段
    field_type=FIELDS_TYPE_MAPPING[item_model][query_field][2]
    print(f'{field_type=}')
    model_field=getattr(item_class, query_field)
    # 以下保证了数据模型存在、搜索值非空且类型合理、具体模型字段存在，首先检查搜索值的类型与模型字段所要求的类型是否匹配
    # 可能需要进行类型转换
    if FIELDS_TYPE_MAPPING[item_model][query_field][2]!='date' and search_value.isdigit():
        # 待查询字段不为日期类型，且搜索值为整数，则先转换为整数类型（后续字符串类型字段的查询可兼容整数搜索值）
        search_value=int(search_value)
    # 注意到str类型的字段要求可以与已经被转换为int类型的搜索值兼容，反之则不行
    if isinstance(search_value, str) and field_type=='int':
        # 搜索值类型与模型字段所要求的类型不匹配
        return make_response(400, 'Invalid search_value')
    # 以下保证了数据模型存在、搜索值非空且类型合理、模型字段存在、搜索值与模型字段所要求的类型匹配或兼容
    # 预处理，如果搜索值为str类型且模型字段为日期类型，则尝试把搜索值的字符串转换为Date对象
    if isinstance(search_value, str) and field_type=='date':
        try:
            search_value=date.fromisoformat(search_value)
            print(f'{search_value=}')
        except ValueError:
            # 日期字符串格式错误
            return make_response(400, 'Invalid search_value')
    # 以下保证了数据模型存在、搜索值非空且类型合理、模型字段存在、搜索值与模型字段所要求的类型匹配或兼容、日期字符串已恰当转换
    # 正式查询
    if field_type in ('int', 'date'):
        data_list=(item_class.query
                   .filter_by(**{query_field: search_value})
                   .order_by(getattr(item_class, primary_key).asc())
                   .all())
    else: # field_type=='str'
        # 字符串搜索值，则使用like查询，同时兼容被转换为int类型的搜索值
        data_list=(item_class.query
                   .filter(model_field.like(f'%{str(search_value)}%'))
                   .order_by(getattr(item_class, primary_key).asc())
                   .all())
    # 返回查询结果
    data_list=[item.to_dict() for item in data_list]
    return make_response(data={'fields': data_fields, 'list': data_list})

def __parse_item_data(item_model:str, item_data:dict)\
        ->tuple[flask.Response, int]|tuple[type, dict[str, any]]:
    # 导入模型的ORM类
    from sqlalchemy import Integer, Boolean, Date
    # 导入Date类，需要用来解析日期字符串
    from datetime import date
    if not item_data:
        # 没有给出要提交的数据
        return make_response(400, 'Empty item_data')
    # 根据数据模型名称获取数据模型类
    item_class=getattr(models, item_model, None)
    if not item_class:
        # 数据模型不存在
        return make_response(400, 'Unknown item_model')
    # 对数据模型字段进行进一步处理
    for field, value in item_data.items():
        print(f'Processing {field=} with {value=}, {getattr(item_class, field).type=}')
        if isinstance(getattr(item_class, field).type, Integer) and isinstance(value, str) and value.isdigit():
            # 数值文本转换为整数类型
            item_data[field]=int(value)
        if isinstance(getattr(item_class, field).type, Boolean):
            assert value in ('True', 'False')
            # 布尔值文本转换为布尔类型
            item_data[field]=True if value=='True' else False
        if value=='':
            # 处理空字符串
            if getattr(item_class, field).nullable:
                item_data[field]=None
            elif isinstance(getattr(item_class, field).type, Integer):
                item_data[field]=0
        if isinstance(getattr(item_class, field).type, Date) and isinstance(value, str) and field.endswith('_update_time'):
            # 解析日期字符串
            value=date.fromisoformat(value) if value else None
            item_data[field]=value
    return item_class, item_data

@app.route(f'{API_PREFIX}/add_item', methods=['POST'], endpoint='add_item')
@validate_request(check_login_level=2)
def add_item():
    # 解析请求参数
    data=request.get_json()
    print(f'\nParsed submitted {data=}')
    item_model=data.get('item_model', '')
    item_data=data.get('item_data', dict())
    tp=__parse_item_data(item_model, item_data)
    if isinstance(tp[1], int):
        return tp
    item_class, item_data=tp
    # 尝试创建数据模型实例
    try:
        new_item=item_class(**item_data)
    except Exception as e:
        # 数据模型实例创建失败
        print(f'\nError creating {item_class=} with\n{item_data=}:\n{e}')
        return make_response(400, str(e))
    # 尝试保存数据模型实例到数据库
    try:
        db.session.add(new_item)
        db.session.commit()
    except Exception as e:
        # 数据库操作失败
        db.session.rollback()
        print(f'\nError adding {item_class=} with\n{item_data=}:\n{e}')
        return make_response(400, str(e))
    # 无响应内容
    return make_response(204)

@app.route(f'{API_PREFIX}/edit_item', methods=['POST'], endpoint='edit_item')
@validate_request(check_login_level=2)
def edit_item():
    # 解析请求参数
    data=request.get_json()
    print(f'Parsed submitted {data=}')
    item_model=data.get('item_model', '')
    item_data=data.get('item_data', dict())
    tp=__parse_item_data(item_model, item_data)
    if isinstance(tp[1], int):
        return tp
    item_class, item_data=tp
    # 尝试获取要修改的实例的主键ID
    item_id=None
    for field, value in item_data.items():
        if field.endswith('id'):
            item_id=value
            break
    if item_id is None:
        # 没有指定实例ID
        return make_response(400, 'Empty item_id')
    # 尝试获取要修改的实例
    item=item_class.query.filter_by(**{field: item_id}).first()
    if not item:
        # 要修改的实例不存在
        return make_response(400, 'Unknown item_id')
    # 尝试修改数据模型实例
    try:
        for field, value in item_data.items():
            setattr(item, field, value)
    except Exception as e:
        # 数据模型实例修改失败
        print(f'\nError editing {item_class=} with\n{item_data=}:\n{e}')
        return make_response(400, str(e))
    # 尝试保存数据模型实例到数据库
    try:
        db.session.commit()
    except Exception as e:
        # 数据库操作失败
        db.session.rollback()
        print(f'\nError editing {item_class=} with\n{item_data=}:\n{e}')
        return make_response(400, str(e))
    # 无响应内容
    return make_response(204)

@app.route(f'{API_PREFIX}/delete_item', methods=['POST'], endpoint='delete_item')
@validate_request(check_login_level=2)
def delete_item():
    # 解析请求参数
    data=request.get_json()
    item_model=data.get('item_model', '')
    item_data=data.get('item_data', dict())
    tp=__parse_item_data(item_model, item_data)
    if isinstance(tp[1], int):
        return tp
    item_class, item_data=tp
    # 尝试获取要删除的实例的主键ID
    item_id=None
    for field, value in item_data.items():
        if field.endswith('id'):
            item_id=value
            break
    if item_id is None:
        # 没有指定实例ID
        return make_response(400, 'Empty item_id')
    # 尝试获取要删除的实例
    item=item_class.query.filter_by(**{field: item_id}).first()
    if not item:
        # 要删除的实例不存在
        return make_response(400, 'Unknown item_id')
    # 检查目标参数是否匹配
    print(f'Checking:\n{item_data=}\nagainst\n{item.to_dict()=}')
    if not all(getattr(item, field)==value for field, value in item_data.items()):
        # 要删除的实例与请求参数不匹配
        return make_response(400, 'Unmatched item_data')
    # 尝试删除数据模型实例
    try:
        db.session.delete(item)
        db.session.commit()
    except Exception as e:
        # 数据模型实例删除失败
        db.session.rollback()
        print(f'\nError deleting {item_class=} with\n{item_data=}:\n{e}')
        return make_response(400, str(e))
    # 无响应内容
    return make_response(204)

@app.route(f'{API_PREFIX}/batch_update', methods=['POST'], endpoint='batch_update')
@validate_request(check_login_level=2)
def batch_update():
    # 导入Date类
    from datetime import date
    # 解析请求参数
    data=request.get_json()
    print(f'\nParsed submitted batch {data=}')
    item_model=data.get('item_model', '')
    batch_data=data.get('batch_data', list())
    batch_data=[item_data for item_data in batch_data if item_data]
    if not batch_data:
        # 没有给出要提交的数据
        return make_response(400, 'Empty batch_data')
    # 根据数据模型名称获取数据模型类
    item_class=getattr(models, item_model, None)
    if not item_class:
        # 数据模型不存在
        return make_response(400, 'Unknown item_model')
    # 遍历每个被提交的数据条目，并尝试创建或修改数据模型实例
    item_messages={}
    for batch_row_id, item_data in enumerate(batch_data):
        tp=__parse_item_data(item_model, item_data)
        if isinstance(tp[1], int):
            return tp
        item_class, item_data=tp
        print(f'\nprocessed {item_data=}')
        # 尝试获取要修改的实例的主键ID
        item_id=None
        for field, value in item_data.items():
            if field.endswith('id'):
                item_id=value
                break
        if item_id is None:
            # 没有指定实例ID
            item_messages[batch_row_id]='Empty item_id'; continue
        # 尝试获取要修改的实例
        item=item_class.query.filter_by(**{field: item_id}).first()
        if not item:
            # 要更新的实例不存在，则尝试创建新实例
            try:
                new_item=item_class(**item_data)
            except Exception as e:
                # 数据模型实例创建失败
                print(f'\nError creating {item_class=} with {batch_row_id=},\n{item_data=}:\n{e}')
                item_messages[batch_row_id]=f'Error creating'; continue
            # 提交保存该新实例到数据库
            try:
                db.session.add(new_item)
                db.session.commit()
            except Exception as e:
                # 数据库操作失败
                db.session.rollback()
                print(f'\nError adding {item_class=} with {batch_row_id=},\n{item_data=}:\n{e}')
                item_messages[batch_row_id]=f'Error adding after creation'; continue
            # 该新增实例提交保存成功
            item_messages[batch_row_id]='Created'
        else:
            # 要更新的实例存在，则尝试修改原有的数据模型实例
            try:
                for field, value in item_data.items():
                    setattr(item, field, value)
            except Exception as e:
                # 数据模型实例修改失败
                print(f'\nError editing {item_class=} with {batch_row_id=},\n{item_data=}:\n{e}')
                item_messages[batch_row_id]=f'Error modifying'; continue
            # 提交保存该实例到数据库
            try:
                db.session.commit()
            except Exception as e:
                # 数据库操作失败
                db.session.rollback()
                print(f'\nError editing {item_class=} with {batch_row_id=},\n{item_data=}:\n{e}')
                item_messages[batch_row_id]=f'Error committing after modification'; continue
            # 该实例提交保存成功
            item_messages[batch_row_id]='Modified'
    # 返回响应结果
    print(f'\nBatch update result: {item_messages=}')
    return make_response(data={'item_messages': item_messages})

def init_configs():
    global CONFIGS

    with open('server_config.json', 'r') as f:
        CONFIGS=jlf(f)

def init_db():
    with app.app_context(): # 确保在应用程序上下文中
        db.create_all() # 创建所有数据表

def initialize():
    init_configs()
    init_db()

def main():
    initialize()
    app.run(debug=True, host='0.0.0.0', port=1037)

if __name__ == '__main__':
    main()

# -*- coding: utf-8 -*-
import os
from json import load as jlf

basedir=os.path.abspath(os.path.dirname(__file__))

class Config:
    # 数据库目标URI
    SQLALCHEMY_DATABASE_URI='dialect+driver://username:password@host:port/database'
    # 使用随机生成的密钥
    SECRET_KEY=os.urandom(24)
    # 连接池配置
    SQLALCHEMY={
        'pool_size': 20,  # 连接池大小
        'max_overflow': 0,  # 超过连接池大小时不创建额外的连接
        'pool_timeout': 30,  # 连接池获取连接的超时时间，单位秒
    }

    def __init__(self):
        with open(os.path.join(basedir, 'database_config.json'), 'r') as f:
            db_configs=jlf(f)
        host=db_configs.get('host') or input("db service host: ")
        port=db_configs.get('port') or input("db service port: ")
        database=db_configs.get('database') or input("database: ")
        username=db_configs.get('username') or input("username: ")
        password=db_configs.get('password') or input("password: ")
        self.SQLALCHEMY_DATABASE_URI=f'postgresql://{username}:{password}@{host}:{port}/{database}'

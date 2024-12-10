# -*- coding: utf-8 -*-
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import TIMESTAMP

db=SQLAlchemy()

class User(db.Model):
    __tablename__='Users'

    uid=db.Column(db.Integer, primary_key=True)
    user_type=db.Column(db.String(6), nullable=False)
    username=db.Column(db.String(20), unique=True, nullable=False)
    pwd_salt=db.Column(db.String(32), nullable=False)
    salted_hash=db.Column(db.String(64), nullable=False)
    reg_key=db.Column(db.String(8))
    login_status=db.Column(db.Boolean)
    last_online_time=db.Column(TIMESTAMP(timezone=True))

    def __repr__(self):
        return f'<User #{self.uid} ({self.user_type}): {self.username}>'

class SS(db.Model):
    __tablename__='SS'
    fields=('ssid', 'ss_update_time', 'ss_pack','from_ssid','ss_name', 'ssvid')

    ssid=db.Column(db.Integer, primary_key=True)
    ss_update_time=db.Column(db.Date)
    ss_pack=db.Column(db.String(4), nullable=False)
    from_ssid=db.Column(db.Integer, db.ForeignKey('SS.ssid'))
    ss_name=db.Column(db.String(10), nullable=False)
    ssvid=db.Column(db.Integer, db.ForeignKey('SS_Version.ssvid'), nullable=False)

    def to_dict(self):
        d={field: getattr(self, field) for field in self.fields}
        d['ss_update_time']=d['ss_update_time'].strftime('%Y-%m-%d') if d['ss_update_time'] else None
        return d

class SS_Version(db.Model):
    __tablename__='SS_Version'
    fields=('ssvid', 'ssv_update_time', 'ss_type', 'ss_color', 'ss_atk', 'ss_hp', 'ss_desc')

    ssvid=db.Column(db.Integer, primary_key=True)
    ssv_update_time=db.Column(db.Date)
    ss_type=db.Column(db.String(3), nullable=False)
    ss_color=db.Column(db.String(2), nullable=False)
    ss_atk=db.Column(db.Integer, nullable=False)
    ss_hp=db.Column(db.Integer, nullable=False)
    ss_desc=db.Column(db.String(200), nullable=False)

    def to_dict(self):
        d={field: getattr(self, field) for field in self.fields}
        d['ssv_update_time']=d['ssv_update_time'].strftime('%Y-%m-%d') if d['ssv_update_time'] else None
        return d

class Card(db.Model):
    __tablename__='Card'
    fields=('cid', 'card_update_time', 'ssid', 'card_name', 'card_rarity', 'cvid')

    cid=db.Column(db.Integer, primary_key=True)
    card_update_time=db.Column(db.Date)
    ssid=db.Column(db.Integer, db.ForeignKey('SS.ssid'))
    card_name=db.Column(db.String(10), nullable=False)
    card_rarity=db.Column(db.String(3), nullable=False)
    cvid=db.Column(db.Integer, db.ForeignKey('Card_Version.cvid'), nullable=False)

    def to_dict(self):
        d={field: getattr(self, field) for field in self.fields}
        d['card_update_time']=d['card_update_time'].strftime('%Y-%m-%d') if d['card_update_time'] else None
        return d

class Card_Version(db.Model):
    __tablename__='Card_Version'
    fields=('cvid', 'cv_update_time', 'card_type', 'card_level', 'card_desc', 'card_has_target',
            'zd_atk', 'zd_shd', 'xt_atk', 'xt_hp', 'hj_dur', 'incl_jx', 'jx_atk', 'jx_hp')

    cvid=db.Column(db.Integer, primary_key=True)
    cv_update_time=db.Column(db.Date)
    card_type=db.Column(db.String(2), nullable=False)
    card_level=db.Column(db.Integer, nullable=False)
    card_desc=db.Column(db.String(200), nullable=False)
    card_has_target=db.Column(db.Integer, nullable=False)

    zd_atk=db.Column(db.Integer, nullable=False)
    zd_shd=db.Column(db.Integer, nullable=False)
    xt_atk=db.Column(db.Integer, nullable=False)
    xt_hp=db.Column(db.Integer, nullable=False)
    hj_dur=db.Column(db.Integer, nullable=False)

    incl_jx=db.Column(db.Boolean, nullable=False)
    jx_atk=db.Column(db.Integer, nullable=False)
    jx_hp=db.Column(db.Integer, nullable=False)

    def to_dict(self):
        d={field: getattr(self, field) for field in self.fields}
        d['cv_update_time']=d['cv_update_time'].strftime('%Y-%m-%d') if d['cv_update_time'] else None
        return d

if __name__=='__main__':
    pass

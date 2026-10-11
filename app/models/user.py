from datetime import datetime#导入当前时间，用于记录用户创建时间
from flask_login import UserMixin#导入Flask-Login的用户基类，让这个模型支持登录状态管理
from werkzeug.security import generate_password_hash, check_password_hash#导入密码加密、验证工具，保证密码不明文存储
from app import db#导入数据库实例（我项目里的db连接）

class User(UserMixin, db.Model):
    __tablename__ = 'users'#指定数据库表名：users
    
    id = db.Column(db.Integer, primary_key=True)# 用户ID，主键，自增，唯一标识
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)# 用户名，最多存80个字符，唯一，不能为空，建索引（查询更快）
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)# 邮箱，120字符，唯一，不能为空，建索引
    password_hash = db.Column(db.String(255), nullable=False)# 密码哈希（不是明文密码！），255字符，不能为空
    created_at = db.Column(db.DateTime, default=datetime.utcnow)# 创建时间，默认是当前UTC时间
    is_active = db.Column(db.Boolean, default=True)# 用户是否激活，默认True（激活状态）
    
    # 关联二维码记录
    qrcodes = db.relationship('QRCode', backref='user', lazy='dynamic', cascade='all, delete-orphan')#backrf是反向引用 ；让用户与二维码的一对多关联返回动态查询对象，提升查询效率和灵活性；删除用户时，自动删除他的所有二维码 
    
    def set_password(self, password):
        """设置密码"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """验证密码"""
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'created_at': self.created_at.isoformat(),
            'is_active': self.is_active
        }
    
    def __repr__(self):
        return f'<User {self.username}>'#打印用户时，自动显示用户名

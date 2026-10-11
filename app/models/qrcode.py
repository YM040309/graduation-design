from datetime import datetime#导入时间模块，用来记录创建/更新时间
from app import db#导入 Flask 数据库对象，用来操作 MySQL/SQLite 等数据库

class QRCode(db.Model):#定义一个叫 QRCode 的数据库模型（对应数据库里的一张表）
    __tablename__ = 'qrcodes'#数据库表名：qrcodes
    
    id = db.Column(db.Integer, primary_key=True)#主键 ID，唯一标识，自增
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)# 关联用户 ID，外键关联 users 表的 id，不能为空，加索引查询更快
    content = db.Column(db.Text, nullable=False)# 二维码内容：文本、网址、手机号等，不能为空
    content_type = db.Column(db.String(50), default='text')  # text, url, email, phone#内容类型：text / url / email / phone，默认是 text
    filename = db.Column(db.String(255), nullable=False)#二维码图片文件名
    file_path = db.Column(db.String(500), nullable=False)#二维码图片存储路径
    
    # 样式参数
    version = db.Column(db.Integer, default=1)#二维码版本
    box_size = db.Column(db.Integer, default=10)#每个格子大小
    border = db.Column(db.Integer, default=4)#边框大小
    error_correction = db.Column(db.String(20), default='M')  # L, M, Q, H#容错率
    fill_color = db.Column(db.String(50), default='black')#前景色
    back_color = db.Column(db.String(50), default='white')#背景色
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)#创建时间，默认存入当前 UTC 时间
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)#更新时间，创建时自动赋值，修改时自动更新
    
    def to_dict(self):#把数据库对象转成字典，用于接口返回给前端
        """转换为字典"""
        return {
           'id': self.id,
            'user_id': self.user_id,
            'content': self.content,
            'content_type': self.content_type,
            'filename': self.filename,
            'file_path': self.file_path,
            'version': self.version,
            'box_size': self.box_size,
            'border': self.border,
            'error_correction': self.error_correction,
            'fill_color': self.fill_color,
            'back_color': self.back_color,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
    
    def __repr__(self):#打印对象时显示友好信息，方便调试
        return f'<QRCode {self.id}: {self.content[:30]}>'

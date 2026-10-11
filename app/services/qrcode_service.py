import os
import qrcode
from PIL import Image
from datetime import datetime
import hashlib#生成随机字符串，避免文件名重复

class QRCodeService:
    """二维码生成服务"""
    
    ERROR_CORRECTION_MAP = {
        'L': qrcode.constants.ERROR_CORRECT_L,  # 7% 纠错
        'M': qrcode.constants.ERROR_CORRECT_M,  # 15% 纠错
        'Q': qrcode.constants.ERROR_CORRECT_Q,  # 25% 纠错
        'H': qrcode.constants.ERROR_CORRECT_H,  # 30% 纠错
    }
    
    @staticmethod
    def generate_qrcode(content, **kwargs):
        """
        生成二维码
        
        参数:
            content: 二维码内容
            version: 版本 (1-40, None表示自动)
            box_size: 每个格子的像素大小
            border: 边框大小
            error_correction: 纠错级别 (L, M, Q, H)
            fill_color: 前景色
            back_color: 背景色
            logo_path: Logo图片路径 (可选)
        
        返回:
            PIL Image对象
        """
        # 获取参数
        version = kwargs.get('version', None)
        box_size = kwargs.get('box_size', 10)
        border = kwargs.get('border', 4)
        error_correction = kwargs.get('error_correction', 'M')
        fill_color = kwargs.get('fill_color', 'black')
        back_color = kwargs.get('back_color', 'white')
        logo_path = kwargs.get('logo_path', None)
        
        # 创建二维码对象
        qr = qrcode.QRCode(
            version=version,
            error_correction=QRCodeService.ERROR_CORRECTION_MAP.get(error_correction, qrcode.constants.ERROR_CORRECT_M),
            box_size=box_size,
            border=border,
        )
        
        # 添加数据
        qr.add_data(content)
        qr.make(fit=True)
        
        # 生成图片
        img = qr.make_image(fill_color=fill_color, back_color=back_color)
        
        # 如果有Logo,嵌入Logo
        if logo_path and os.path.exists(logo_path):
            img = QRCodeService._add_logo(img, logo_path)
        
        return img
    
    @staticmethod
    def _add_logo(qr_img, logo_path):
        """在二维码中嵌入Logo"""
        # 打开Logo图片
        logo = Image.open(logo_path)
        
        # 计算Logo大小 (二维码的1/5)
        qr_width, qr_height = qr_img.size
        logo_size = min(qr_width, qr_height) // 5
        
        # 调整Logo大小
        logo = logo.resize((logo_size, logo_size), Image.Resampling.LANCZOS)
        
        # 创建白色背景
        logo_bg = Image.new('RGB', (logo_size + 20, logo_size + 20), 'white')
        logo_bg.paste(logo, (10, 10))
        
        # 计算Logo位置 (居中)
        logo_pos = ((qr_width - logo_size - 20) // 2, (qr_height - logo_size - 20) // 2)
        
        # 将二维码转换为RGB模式
        if qr_img.mode != 'RGB':
            qr_img = qr_img.convert('RGB')
        
        # 粘贴Logo
        qr_img.paste(logo_bg, logo_pos)
        
        return qr_img
    
    @staticmethod
    def save_qrcode(img, save_dir, filename=None):
        """
        保存二维码到文件
        
        参数:
            img: PIL Image对象
            save_dir: 保存目录
            filename: 文件名 (可选,不指定则自动生成)
        
        返回:
            (文件名, 完整路径)
        """
        # 确保保存目录存在
        os.makedirs(save_dir, exist_ok=True)
        
        # 生成文件名
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            random_str = hashlib.md5(str(datetime.now().timestamp()).encode()).hexdigest()[:8]
            filename = f'qrcode_{timestamp}_{random_str}.png'
        
        # 确保文件名以.png结尾
        if not filename.endswith('.png'):
            filename += '.png'
        
        # 完整路径
        filepath = os.path.join(save_dir, filename)
        
        # 保存图片
        img.save(filepath)
        
        return filename, filepath
    
    @staticmethod
    def batch_generate(data_list, save_dir, **common_kwargs):
        """
        批量生成二维码
        
        参数:
            data_list: 内容列表
            save_dir: 保存目录
            common_kwargs: 通用参数
        
        返回:
            生成结果列表 [(content, filename, filepath), ...]
        """
        results = []
        
        for content in data_list:
            try:
                # 生成二维码
                img = QRCodeService.generate_qrcode(content, **common_kwargs)
                
                # 保存二维码
                filename, filepath = QRCodeService.save_qrcode(img, save_dir)
                
                results.append({
                    'success': True,
                    'content': content,
                    'filename': filename,
                    'filepath': filepath
                })
            except Exception as e:
                results.append({
                    'success': False,
                    'content': content,
                    'error': str(e)
                })
        
        return results
    
    @staticmethod
    def detect_content_type(content):
        """检测内容类型"""
        content_lower = content.lower().strip()
        
        if content_lower.startswith('http://') or content_lower.startswith('https://'):
            return 'url'
        elif content_lower.startswith('mailto:') or '@' in content:
            return 'email'
        elif content_lower.startswith('tel:') or (content.replace('-', '').replace(' ', '').isdigit() and len(content) >= 8):
            return 'phone'
        else:
            return 'text'

import os#操作文件、文件夹用（保存 / 删除二维码图片）
from flask import Blueprint, render_template, request, jsonify, send_file, current_app, flash, redirect, url_for#把二维码功能打包成一个模块，方便管理;渲染 HTML 网页给用户看;接收用户在表单里填的内容;返回接口数据;下载文件用;弹出提示（成功 / 失败）;页面跳转
from flask_login import login_required, current_user#必须登录才能用;当前登录的用户
from werkzeug.utils import secure_filename#安全处理文件名
from app import db#数据库连接
from app.models import QRCode#从 app 文件夹里的 models 模块中，把 二维码模型（QRCode）导入过来使用
from app.services import QRCodeService#从 app 文件夹的 services 里，把【QRCodeService】导入过来,让我能用它生成二维码。

qrcode_bp = Blueprint('qrcode', __name__, url_prefix='/qrcode')#所有二维码功能网址都以 /qrcode 开头,因为我用了 Flask 的 “蓝图 (Blueprint)”，给整个二维码模块统一加了 /qrcode 前缀。

@qrcode_bp.route('/generate', methods=['GET', 'POST'])#既能看页面（GET），又能提交表单(POST)
@login_required#是登录验证装饰器，用于保护路由接口，只有已登录用户才能访问相关功能，未登录用户会自动重定向到登录页面，保证系统安全性与用户数据隐私。必须登录才能用
def generate():
    """生成单个二维码页面"""
    if request.method == 'POST':#如果用户是提交表单（点了【生成】按钮）就执行下面的代码
        # 获取表单数据
        content = request.form.get('content', '').strip()#拿到用户在网页输入框里填的二维码内容，strip() 是去掉前后空格，避免输入空内容
        
        if not content:#如果用户啥也没输入
            flash('请输入二维码内容', 'error')#就弹出红色提示：请输入二维码内容
            return render_template('qrcode/generate.html')#并重新回到生成页面
        
        # 获取样式参数
        box_size = int(request.form.get('box_size', 10))#大小
        border = int(request.form.get('border', 4))#边框
        error_correction = request.form.get('error_correction', 'M')#容错率
        fill_color = request.form.get('fill_color', 'black')#二维码颜色
        back_color = request.form.get('back_color', 'white')#背景颜色
        
        try:
            # 生成二维码
            img = QRCodeService.generate_qrcode(
                content,
                box_size=box_size,
                border=border,
                error_correction=error_correction,
                fill_color=fill_color,
                back_color=back_color
            )
            
            # 保存二维码
            filename, filepath = QRCodeService.save_qrcode(img, current_app.config['QRCODE_FOLDER'])#把生成好的二维码图片保存到本地文件夹
            
            # 保存到数据库
            content_type = QRCodeService.detect_content_type(content)
            qr_record = QRCode(
                user_id=current_user.id,
                content=content,
                content_type=content_type,
                filename=filename,
                file_path=filepath,
                box_size=box_size,
                border=border,
                error_correction=error_correction,
                fill_color=fill_color,
                back_color=back_color
            )
            
            db.session.add(qr_record)
            db.session.commit()
            
            flash('二维码生成成功', 'success')#弹出提示 生成成功
            return redirect(url_for('qrcode.view', id=qr_record.id))#然后跳转到二维码查看页面
        
        except Exception as e:
            flash(f'生成失败: {str(e)}', 'error')
            return render_template('qrcode/generate.html')#回到生成页面
    
    return render_template('qrcode/generate.html')#加载并返回指定网页页面，展示给浏览器

@qrcode_bp.route('/batch', methods=['GET', 'POST'])
@login_required
def batch():
    """批量生成二维码"""
    if request.method == 'POST':
        # 获取批量内容
        content_text = request.form.get('content_text', '').strip()
        
        # 上传文件
        file = request.files.get('file')
        
        contents = []
        
        # 从文本框获取内容
        if content_text:
            contents = [line.strip() for line in content_text.split('\n') if line.strip()]
        
        # 从文件获取内容
        elif file and file.filename:
            filename = secure_filename(file.filename)
            filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    contents = [line.strip() for line in f.readlines() if line.strip()]
            except Exception as e:
                flash(f'读取文件失败: {str(e)}', 'error')
                return render_template('qrcode/batch.html')
        
        if not contents:
            flash('请输入内容或上传文件', 'error')
            return render_template('qrcode/batch.html')
        
        # 获取样式参数
        box_size = int(request.form.get('box_size', 10))
        border = int(request.form.get('border', 4))
        error_correction = request.form.get('error_correction', 'M')
        fill_color = request.form.get('fill_color', 'black')
        back_color = request.form.get('back_color', 'white')
        
        # 批量生成
        results = QRCodeService.batch_generate(
            contents,
            current_app.config['QRCODE_FOLDER'],
            box_size=box_size,
            border=border,
            error_correction=error_correction,
            fill_color=fill_color,
            back_color=back_color
        )
        
        # 保存到数据库
        success_count = 0
        for result in results:
            if result['success']:
                content_type = QRCodeService.detect_content_type(result['content'])
                qr_record = QRCode(
                    user_id=current_user.id,
                    content=result['content'],
                    content_type=content_type,
                    filename=result['filename'],
                    file_path=result['filepath'],
                    box_size=box_size,
                    border=border,
                    error_correction=error_correction,
                    fill_color=fill_color,
                    back_color=back_color
                )
                db.session.add(qr_record)
                success_count += 1
        
        db.session.commit()
        
        flash(f'成功生成 {success_count}/{len(contents)} 个二维码', 'success')
        return redirect(url_for('qrcode.history'))
    
    return render_template('qrcode/batch.html')

@qrcode_bp.route('/history')
@login_required#是登录验证装饰器，用于保护路由接口，只有已登录用户才能访问相关功能，未登录用户会自动重定向到登录页面，保证系统安全性与用户数据隐私。必须登录才能用
def history():
    """查看生成历史"""
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    # 查询当前用户的二维码记录
    pagination = QRCode.query.filter_by(user_id=current_user.id)\
        .order_by(QRCode.created_at.desc())\
        .paginate(page=page, per_page=per_page, error_out=False)
    
    qrcodes = pagination.items
    
    return render_template('qrcode/history.html', qrcodes=qrcodes, pagination=pagination)

@qrcode_bp.route('/view/<int:id>')
@login_required
def view(id):
    """查看单个二维码"""
    qr = QRCode.query.get_or_404(id)
    
    # 权限检查
    if qr.user_id != current_user.id:
        flash('无权访问此二维码', 'error')
        return redirect(url_for('qrcode.history'))
    
    return render_template('qrcode/view.html', qrcode=qr)

@qrcode_bp.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    """编辑二维码"""
    qr = QRCode.query.get_or_404(id)
    
    # 权限检查
    if qr.user_id != current_user.id:
        flash('无权编辑此二维码', 'error')
        return redirect(url_for('qrcode.history'))
    
    if request.method == 'POST':
        content = request.form.get('content', '').strip()
        
        if not content:
            flash('请输入二维码内容', 'error')
            return render_template('qrcode/edit.html', qrcode=qr)
        
        # 获取样式参数
        box_size = int(request.form.get('box_size', 10))
        border = int(request.form.get('border', 4))
        error_correction = request.form.get('error_correction', 'M')
        fill_color = request.form.get('fill_color', 'black')
        back_color = request.form.get('back_color', 'white')
        
        try:
            # 删除旧文件
            if os.path.exists(qr.file_path):
                os.remove(qr.file_path)
            
            # 重新生成二维码
            img = QRCodeService.generate_qrcode(
                content,
                box_size=box_size,
                border=border,
                error_correction=error_correction,
                fill_color=fill_color,
                back_color=back_color
            )
            
            # 保存新的二维码
            filename, filepath = QRCodeService.save_qrcode(img, current_app.config['QRCODE_FOLDER'])
            
            # 更新数据库记录
            qr.content = content
            qr.content_type = QRCodeService.detect_content_type(content)
            qr.filename = filename
            qr.file_path = filepath
            qr.box_size = box_size
            qr.border = border
            qr.error_correction = error_correction
            qr.fill_color = fill_color
            qr.back_color = back_color
            
            db.session.commit()
            
            flash('二维码更新成功', 'success')
            return redirect(url_for('qrcode.view', id=qr.id))
        
        except Exception as e:
            flash(f'更新失败: {str(e)}', 'error')
            return render_template('qrcode/edit.html', qrcode=qr)
    
    return render_template('qrcode/edit.html', qrcode=qr)

@qrcode_bp.route('/delete/<int:id>', methods=['POST'])
@login_required
def delete(id):
    """删除二维码"""
    qr = QRCode.query.get_or_404(id)
    
    # 权限检查
    if qr.user_id != current_user.id:
        return jsonify({'success': False, 'message': '无权删除此二维码'}), 403
    
    try:
        # 删除文件
        if os.path.exists(qr.file_path):
            os.remove(qr.file_path)
        
        # 删除数据库记录
        db.session.delete(qr)
        db.session.commit()
        
        flash('二维码已删除', 'success')
        return jsonify({'success': True, 'message': '删除成功'})
    
    except Exception as e:
        return jsonify({'success': False, 'message': f'删除失败: {str(e)}'}), 500

@qrcode_bp.route('/download/<int:id>')
@login_required
def download(id):
    """下载二维码"""
    qr = QRCode.query.get_or_404(id)
    
    # 权限检查
    if qr.user_id != current_user.id:
        flash('无权下载此二维码', 'error')
        return redirect(url_for('qrcode.history'))
    
    if not os.path.exists(qr.file_path):
        flash('文件不存在', 'error')
        return redirect(url_for('qrcode.history'))
    
    return send_file(qr.file_path, as_attachment=True, download_name=qr.filename)

@qrcode_bp.route('/api/generate', methods=['POST'])
@login_required
def api_generate():
    """API接口 - 生成二维码"""
    data = request.get_json()
    
    if not data or 'content' not in data:
        return jsonify({'success': False, 'message': '缺少content参数'}), 400
    
    content = data['content'].strip()
    if not content:
        return jsonify({'success': False, 'message': '内容不能为空'}), 400
    
    # 获取参数
    box_size = data.get('box_size', 10)
    border = data.get('border', 4)
    error_correction = data.get('error_correction', 'M')
    fill_color = data.get('fill_color', 'black')
    back_color = data.get('back_color', 'white')
    
    try:
        # 生成二维码
        img = QRCodeService.generate_qrcode(
            content,
            box_size=box_size,
            border=border,
            error_correction=error_correction,
            fill_color=fill_color,
            back_color=back_color
        )
        
        # 保存二维码
        filename, filepath = QRCodeService.save_qrcode(img, current_app.config['QRCODE_FOLDER'])
        
        # 保存到数据库
        content_type = QRCodeService.detect_content_type(content)
        qr_record = QRCode(
            user_id=current_user.id,
            content=content,
            content_type=content_type,
            filename=filename,
            file_path=filepath,
            box_size=box_size,
            border=border,
            error_correction=error_correction,
            fill_color=fill_color,
            back_color=back_color
        )
        
        db.session.add(qr_record)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '生成成功',
            'data': qr_record.to_dict()
        })
    
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

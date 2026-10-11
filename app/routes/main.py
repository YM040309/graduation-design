from flask import Blueprint, render_template
from flask_login import login_required

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
@login_required
def index():
    """首页"""
    return render_template('index.html')

@main_bp.route('/about')
def about():
    """关于页面"""
    return render_template('about.html')

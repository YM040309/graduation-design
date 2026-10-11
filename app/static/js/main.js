// 自动关闭提示消息
document.addEventListener('DOMContentLoaded', function() {
    // 5秒后自动关闭成功消息
    const alerts = document.querySelectorAll('.alert-success');
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.style.opacity = '0';
            setTimeout(() => {
                alert.style.display = 'none';
            }, 300);
        }, 5000);
    });
});

// 颜色选择器实时预览
function setupColorPreview() {
    const fillColorInput = document.getElementById('fill_color');
    const backColorInput = document.getElementById('back_color');
    
    if (fillColorInput) {
        fillColorInput.addEventListener('input', function() {
            console.log('前景色:', this.value);
        });
    }
    
    if (backColorInput) {
        backColorInput.addEventListener('input', function() {
            console.log('背景色:', this.value);
        });
    }
}

// 表单验证
function setupFormValidation() {
    const forms = document.querySelectorAll('form');
    
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            const requiredFields = form.querySelectorAll('[required]');
            let isValid = true;
            
            requiredFields.forEach(field => {
                if (!field.value.trim()) {
                    isValid = false;
                    field.style.borderColor = 'red';
                } else {
                    field.style.borderColor = '#ddd';
                }
            });
            
            if (!isValid) {
                e.preventDefault();
                alert('请填写所有必填字段');
            }
        });
    });
}

// 文件上传大小验证
function setupFileUpload() {
    const fileInputs = document.querySelectorAll('input[type="file"]');
    
    fileInputs.forEach(input => {
        input.addEventListener('change', function() {
            const file = this.files[0];
            if (file) {
                const maxSize = 16 * 1024 * 1024; // 16MB
                if (file.size > maxSize) {
                    alert('文件大小不能超过16MB');
                    this.value = '';
                }
            }
        });
    });
}

// 初始化
document.addEventListener('DOMContentLoaded', function() {
    setupColorPreview();
    setupFormValidation();
    setupFileUpload();
});

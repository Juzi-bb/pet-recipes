// 登录和注册表单

console.log('Auth.js 开始加载...');

document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM 已加载，开始初始化认证功能...');
    
    // 获取表单元素
    const loginForm = document.getElementById('loginForm');
    const registerForm = document.getElementById('registerForm');
    
    console.log('登录表单:', loginForm ? '已找到' : '未找到');
    console.log('注册表单:', registerForm ? '已找到' : '未找到');
    
    // 初始化登录表单
    if (loginForm) {
        initLoginForm(loginForm);
    }
    
    // 初始化注册表单
    if (registerForm) {
        initRegisterForm(registerForm);
    }
});

/**
 * 初始化登录表单
 */
function initLoginForm(form) {
    console.log('初始化登录表单...');
    
    form.addEventListener('submit', function(event) {
        event.preventDefault(); // 阻止默认提交
        console.log('登录表单提交事件触发');
        
        // 获取表单数据
        const formData = new FormData(form);
        const data = {
            username: formData.get('username'),
            password: formData.get('password')
        };
        
        console.log('登录数据:', data);
        
        // 验证数据
        if (!data.username || !data.password) {
            showMessage('请填写用户名和密码', 'error');
            return;
        }
        
        // 提交登录请求
        submitLogin(data);
    });
}

/**
 * 初始化注册表单
 */
function initRegisterForm(form) {
    console.log('初始化注册表单...');
    
    form.addEventListener('submit', function(event) {
        event.preventDefault(); // 阻止默认提交
        console.log('注册表单提交事件触发');
        
        // 获取表单数据
        const formData = new FormData(form);
        const data = {
            username: formData.get('username'),
            nickname: formData.get('nickname'),
            password: formData.get('password'),
            confirm_password: formData.get('confirm_password')
        };
        
        console.log('注册数据:', data);
        
        // 验证数据
        if (!validateRegisterData(data)) {
            return;
        }
        
        // 提交注册请求
        submitRegister(data);
    });
}

/**
 * 验证注册数据
 */
function validateRegisterData(data) {
    // 检查必填字段
    if (!data.username || !data.nickname || !data.password) {
        showMessage('请填写所有必填字段', 'error');
        return false;
    }
    
    // 检查密码长度
    if (data.password.length < 6) {
        showMessage('密码至少需要6个字符', 'error');
        return false;
    }
    
    // 检查密码确认
    if (data.password !== data.confirm_password) {
        showMessage('两次输入的密码不一致', 'error');
        return false;
    }
    
    return true;
}

/**
 * 提交登录请求
 */
function submitLogin(data) {
    console.log('开始提交登录请求...');
    showMessage('正在登录...', 'info');
    
    // --------------- 修改API路径 ---------------
    fetch('/user/login', {  // 改为统一的/user路径
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(data)
    })
    .then(response => {
        console.log('登录响应状态:', response.status);
        return response.json();
    })
    .then(result => {
        console.log('登录响应数据:', result);
        
        if (result.success) {
            showMessage(result.message || '登录成功！', 'success');
            
            // 保存用户信息到localStorage（可选）
            if (result.token) {
                localStorage.setItem('token', result.token);
            }
            if (result.nickname) {
                localStorage.setItem('nickname', result.nickname);
            }
            
            // 延迟跳转，让用户看到成功消息
            setTimeout(() => {
                window.location.href = result.redirect_url || '/user_center';
            }, 1500);
        } else {
            showMessage(result.message || '登录失败', 'error');
        }
    })
    .catch(error => {
        console.error('登录请求错误:', error);
        showMessage('网络错误，请稍后重试', 'error');
    });
}

/**
 * 提交注册请求
 */
function submitRegister(data) {
    console.log('开始提交注册请求...');
    showMessage('正在注册...', 'info');
    
    // 移除确认密码字段，不发送到后端
    const submitData = {
        username: data.username,
        nickname: data.nickname,
        password: data.password
    };
    
    // --------------- 修改API路径 ---------------
    fetch('/user/register', {  // 改为统一的/user路径
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(submitData)
    })
    .then(response => {
        console.log('注册响应状态:', response.status);
        return response.json();
    })
    .then(result => {
        console.log('注册响应数据:', result);
        
        if (result.success) {
            showMessage(result.message || '注册成功！', 'success');
            
            // 延迟跳转到登录页面
            setTimeout(() => {
                window.location.href = '/user/login';
            }, 2000);
        } else {
            showMessage(result.message || '注册失败', 'error');
        }
    })
    .catch(error => {
        console.error('注册请求错误:', error);
        showMessage('网络错误，请稍后重试', 'error');
    });
}

/**
 * 显示消息提示
 */
function showMessage(message, type = 'info') {
    console.log('显示消息:', message, '类型:', type);
    
    // 获取消息容器
    let messageContainer = document.getElementById('message-container');
    
    // 如果没有消息容器，创建一个
    if (!messageContainer) {
        messageContainer = document.createElement('div');
        messageContainer.id = 'message-container';
        
        // 尝试插入到表单容器的开头
        const formContainer = document.querySelector('.form-container');
        if (formContainer) {
            formContainer.insertBefore(messageContainer, formContainer.firstChild);
        } else {
            // 如果没有表单容器，插入到body开头
            document.body.insertBefore(messageContainer, document.body.firstChild);
        }
    }
    
    // 清除之前的消息
    messageContainer.innerHTML = '';
    
    // 创建消息元素
    const messageElement = document.createElement('div');
    messageElement.className = `message ${type}`;
    messageElement.textContent = message;
    
    // 添加消息
    messageContainer.appendChild(messageElement);
    
    // 自动隐藏消息（除了错误消息）
    if (type !== 'error') {
        setTimeout(() => {
            messageElement.style.opacity = '0';
            setTimeout(() => {
                if (messageElement.parentNode) {
                    messageElement.parentNode.removeChild(messageElement);
                }
            }, 300);
        }, 3000);
    }
}

console.log('Auth.js 加载完成');
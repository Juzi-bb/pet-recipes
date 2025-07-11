// 登录和注册表单

console.log('Auth.js loading...');

document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM loaded, initializing authentication functions...');
    
    // 获取表单元素
    const loginForm = document.getElementById('loginForm');
    const registerForm = document.getElementById('registerForm');
    
    console.log('Login Form:', loginForm ? 'Found' : 'Not found');
    console.log('Register Form:', registerForm ? 'Found' : 'Not found');
    
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
    console.log('Initializing login form...');
    
    form.addEventListener('submit', function(event) {
        event.preventDefault(); // 阻止默认提交
        console.log('Login form submission event triggered');
        
        // 获取表单数据
        const formData = new FormData(form);
        const data = {
            username: formData.get('username'),
            password: formData.get('password')
        };
        
        console.log('Login data:', data);
        
        // 验证数据
        if (!data.username || !data.password) {
            showMessage('Please fill in username and password', 'error');
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
    console.log('Initializing register form...');
    
    form.addEventListener('submit', function(event) {
        event.preventDefault(); // 阻止默认提交
        console.log('Register form submission event triggered');
        
        // 获取表单数据
        const formData = new FormData(form);
        const data = {
            username: formData.get('username'),
            nickname: formData.get('nickname'),
            password: formData.get('password'),
            confirm_password: formData.get('confirm_password')
        };
        
        console.log('Register data:', data);
        
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
        showMessage('Please fill in all required fields', 'error');
        return false;
    }
    
    // 检查密码长度
    if (data.password.length < 6) {
        showMessage('Password must be at least 6 characters long', 'error');
        return false;
    }
    
    // 检查密码确认
    if (data.password !== data.confirm_password) {
        showMessage('The two entered passwords do not match', 'error');
        return false;
    }
    
    return true;
}

/**
 * 提交登录请求
 */
function submitLogin(data) {
    console.log('Submitting login request...');
    showMessage('Logging in...', 'info');
    
    fetch('/user/login', {  // 改为统一的/user路径
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(data)
    })
    .then(response => {
        console.log('Login response status:', response.status);
        return response.json();
    })
    .then(result => {
        console.log('Login response data:', result);
        
        if (result.success) {
            showMessage(result.message || 'Login successful！', 'success');
            
            // --------------- 修改登录成功后的处理逻辑 ---------------
            // 保存用户信息到localStorage（可选）
            if (result.token) {
                localStorage.setItem('token', result.token);
            }
            if (result.nickname) {
                localStorage.setItem('nickname', result.nickname);
            }
            
            // 延迟跳转，让用户看到成功消息
            setTimeout(() => {
                // 优先使用后端返回的重定向URL，否则跳转到用户中心
                const redirectUrl = result.redirect_url || '/user_center';
                window.location.href = redirectUrl;
            }, 1000); // 缩短延迟时间
            // --------------- 结束修改 ---------------
        } else {
            showMessage(result.message || 'Login failed', 'error');
        }
    })
    .catch(error => {
        console.error('Login request error:', error);
        showMessage('Network error, please try again later', 'error');
    });
}

/**
 * 提交注册请求
 */
function submitRegister(data) {
    console.log('Submitting registration request...');
    showMessage('Registering...', 'info');
    
    // 移除确认密码字段，不发送到后端
    const submitData = {
        username: data.username,
        nickname: data.nickname,
        password: data.password
    };
    
    //  修改API路径 
    fetch('/user/register', {  // 改为统一的/user路径
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(submitData)
    })
    .then(response => {
        console.log('Registration response status:', response.status);
        return response.json();
    })
    .then(result => {
        console.log('Registration response data:', result);
        
        if (result.success) {
            showMessage(result.message || 'Registration successful！', 'success');
            
            // --------------- 修改注册成功后的处理逻辑 ---------------
            // 延迟跳转到登录页面
            setTimeout(() => {
                window.location.href = '/user/login';
            }, 1500); // 缩短延迟时间
        } else {
            showMessage(result.message || 'Registration failed', 'error');
        }
    })
    .catch(error => {
        console.error('Registration request error:', error);
        showMessage('Network error, please try again later', 'error');
    });
}

/**
 * 显示消息提示
 */
function showMessage(message, type = 'info') {
    console.log('Show message:', message, 'Type:', type);
    
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

    // --------------- 添加消息样式（如果页面没有定义） ---------------
    if (!document.querySelector('style[data-auth-message-styles]')) {
        const styleElement = document.createElement('style');
        styleElement.setAttribute('data-auth-message-styles', 'true');
        styleElement.textContent = `
            .message {
                padding: 1rem;
                margin-bottom: 1.5rem;
                border-radius: 8px;
                text-align: center;
                border: 2px solid;
                font-weight: bold;
                transition: opacity 0.3s ease;
            }
            
            .message.success {
                background-color: #EDBF9D;
                border-color: #A1B4B2;
                color: #510B0B;
            }
            
            .message.error {
                background-color: #EDBF9D;
                border-color: #B82F0D;
                color: #B82F0D;
            }
            
            .message.info {
                background-color: #EDBF9D;
                border-color: #5580AD;
                color: #5580AD;
            }
        `;
        document.head.appendChild(styleElement);
    }
    // --------------- 结束添加 ---------------
    
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

// --------------- 添加全局函数，供其他页面使用 ---------------
/**
 * 检查用户登录状态
 */
window.checkUserLoginStatus = function() {
    return fetch('/api/check_login')
        .then(response => response.json())
        .then(data => data.logged_in)
        .catch(error => {
            console.error('Failed to check login status:', error);
            return false;
        });
};

/**
 * 退出登录
 */
window.logoutUser = function() {
    return fetch('/user/logout', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // 清除本地存储的用户信息
            localStorage.removeItem('token');
            localStorage.removeItem('nickname');
            return true;
        } else {
            throw new Error(data.message || 'Logout failed');
        }
    });
};

/**
 * 显示登录提示并跳转
 */
window.showLoginPrompt = function(message = 'This feature requires login to use') {
    if (confirm(message + '\n\nClick OK to go to the login page, or click Cancel to stay on the current page')) {
        window.location.href = '/user/login';
        return true;
    }
    return false;
};
// --------------- 结束添加 ---------------

console.log('Auth.js loaded');
// 登录和注册表单

document.addEventListener('DOMContentLoaded', function() {
    // 获取登录表单元素
    const loginForm = document.getElementById('loginForm');
    // 获取注册表单元素
    const registerForm = document.getElementById('registerForm');
    // 获取退出登录按钮 (在 base.html 中)
    const logoutBtn = document.getElementById('logoutBtn');
    // 获取导航栏的用户信息显示区域 (在 base.html 中)
    const userInfoSpan = document.getElementById('userInfoSpan'); // 我们需要在 base.html 中添加这个 id

    // 获取登录/注册模态框及其触发按钮
    const loginModal = document.getElementById('loginModal');
    const registerModal = document.getElementById('registerModal');
    const loginModalBtn = document.getElementById('loginBtn'); // base.html 中的登录按钮
    const registerModalBtn = document.getElementById('registerBtn'); // base.html 中的注册按钮
    const quickLoginBtn = document.getElementById('quickLoginBtn'); // index.html 中的快速登录按钮
    const closeButtons = document.querySelectorAll('.close-btn');

    // --------------- 辅助函数：显示消息 ---------------
    function showMessage(message, type = 'success') {
        const flashMessagesDiv = document.querySelector('.flash-messages');
        if (!flashMessagesDiv) {
            console.warn('Flash messages container not found!');
            // 如果没有容器，暂时用 alert 提示
            alert(message);
            return;
        }
        const messageDiv = document.createElement('div');
        messageDiv.classList.add('flash-message');
        if (type === 'error') {
            messageDiv.classList.add('error');
        }
        messageDiv.textContent = message;
        flashMessagesDiv.appendChild(messageDiv);

        // 5秒后自动移除
        setTimeout(() => {
            messageDiv.remove();
        }, 5000);
    }

    // --------------- 模态框控制 ---------------
    if (loginModalBtn) {
        loginModalBtn.addEventListener('click', () => {
            if (loginModal) loginModal.style.display = 'block';
        });
    }
    if (registerModalBtn) {
        registerModalBtn.addEventListener('click', () => {
            if (registerModal) registerModal.style.display = 'block';
        });
    }
    if (quickLoginBtn) { // index.html 中的快速登录按钮
        quickLoginBtn.addEventListener('click', () => {
            if (loginModal) loginModal.style.display = 'block';
        });
    }

    closeButtons.forEach(button => {
        button.addEventListener('click', (event) => {
            const modalId = event.target.dataset.modal;
            const modal = document.getElementById(modalId);
            if (modal) modal.style.display = 'none';
        });
    });

    window.addEventListener('click', function(event) {
        if (event.target == loginModal) {
            loginModal.style.display = 'none';
        }
        if (event.target == registerModal) {
            registerModal.style.display = 'none';
        }
    });

    // --------------- 用户状态检查和 UI 更新 ---------------
    function updateAuthUI() {
        const loggedInSection = document.querySelector('.user-info .logged-in'); // base.html
        const loggedOutSection = document.querySelector('.user-info .logged-out'); // base.html
        const usernameSpan = document.getElementById('usernameDisplay'); // base.html 中的用户昵称显示
        const loginReminder = document.getElementById('loginReminder'); // index.html

        // 从 localStorage 获取 token，如果后端是基于 JWT 认证的
        // 或者直接依赖 Flask session cookie
        const token = localStorage.getItem('jwt_token'); 
        const nickname = localStorage.getItem('user_nickname');

        if (token && nickname) { // 假设成功登录后，我们也会在 localStorage 存储 nickname
            if (loggedInSection) loggedInSection.style.display = 'flex';
            if (loggedOutSection) loggedOutSection.style.display = 'none';
            if (usernameSpan) usernameSpan.textContent = nickname;
            if (loginReminder) loginReminder.style.display = 'none'; // 登录提醒消失
        } else {
            if (loggedInSection) loggedInSection.style.display = 'none';
            if (loggedOutSection) loggedOutSection.style.display = 'flex';
            if (loginReminder) loginReminder.style.display = 'block'; // 登录提醒显示
        }
    }

    // --------------- 注册逻辑 ---------------
    if (registerForm) {
        registerForm.addEventListener('submit', async function(event) {
            event.preventDefault(); // 阻止表单默认提交行为

            const username = this.username.value;
            const nickname = this.nickname.value; // 获取昵称
            const password = this.password.value;
            const confirmPassword = this.confirm_password.value;

            if (password !== confirmPassword) {
                showMessage('两次输入的密码不一致！', 'error');
                return;
            }

            try {
                const response = await fetch('/user/register', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ username, nickname, password }) // 包含昵称
                });

                const data = await response.json();

                if (response.ok) {
                    showMessage(data.message || '注册成功！');
                    if (registerModal) registerModal.style.display = 'none'; // 关闭注册模态框
                    // 注册成功后，可以提示用户去登录，或直接跳转到登录页面
                    // window.location.href = "{{ url_for('user.login') }}"; // 如果有独立登录页
                    // 或者更流畅的体验：直接打开登录模态框
                    if (loginModal) loginModal.style.display = 'block';
                } else {
                    showMessage(data.message || '注册失败！', 'error');
                }
            } catch (error) {
                console.error('注册请求失败:', error);
                showMessage('网络请求错误，请稍后再试。', 'error');
            }
        });
    }

    // --------------- 登录逻辑 ---------------
    if (loginForm) {
        loginForm.addEventListener('submit', async function(event) {
            event.preventDefault(); // 阻止表单默认提交行为

            const username = this.username.value;
            const password = this.password.value;

            try {
                const response = await fetch('/user/login', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ username, password })
                });

                const data = await response.json();

                if (response.ok) {
                    // 登录成功，后端会设置 session cookie，这里可以处理 JWT token
                    if (data.token) {
                        localStorage.setItem('jwt_token', data.token);
                    }
                    // 假设后端登录成功后，能提供用户的昵称，或者我们通过另一个API获取
                    // 但更简单的方法是，后端在设置session时，也返回昵称或在前端直接从session获取
                    // 为了简化，我们假设登录成功后，前端可以从某个地方获取昵称，或者从session
                    // 由于我们修改后端会设置session['nickname']，前端可以依赖后端设置的session
                    // 这里我们假设后端响应中包含了nickname（实际是依靠Flask session）
                    // 为了演示，我们暂时将用户名作为昵称存入localStorage，实际应从后端获取
                    localStorage.setItem('user_nickname', username); // 暂时使用 username 作为 nickname

                    showMessage('登录成功！');
                    if (loginModal) loginModal.style.display = 'none'; // 关闭登录模态框

                    updateAuthUI(); // 更新 UI 状态
                    // 登录成功后跳转到用户中心或添加宠物页面
                    window.location.href = "{{ url_for('main.user_center') }}"; // 或者 'main.add_pet'
                } else {
                    showMessage(data.message || '登录失败！', 'error');
                }
            } catch (error) {
                console.error('登录请求失败:', error);
                showMessage('网络请求错误，请稍后再试。', 'error');
            }
        });
    }

    // --------------- 退出登录逻辑 ---------------
    if (logoutBtn) {
        logoutBtn.addEventListener('click', async function(event) {
            event.preventDefault();
            try {
                // 如果后端有 /api/user/logout 路由来清除 session
                // await fetch('/api/user/logout', { method: 'POST' });

                // 清除本地存储的 token 和昵称
                localStorage.removeItem('jwt_token');
                localStorage.removeItem('user_nickname');

                showMessage('您已成功退出登录。');
                updateAuthUI(); // 更新 UI 状态
                // 跳转回首页
                window.location.href = "{{ url_for('main.home') }}";
            } catch (error) {
                console.error('退出登录失败:', error);
                showMessage('退出登录时发生错误。', 'error');
            }
        });
    }

    // 页面加载时检查登录状态并更新UI
    updateAuthUI();
});

// 在这里定义全局函数，以便在 Jinja2 模板中直接调用
// 尽管直接在 DOMContentLoaded 中注册监听器是更好的实践
// 但为了兼容旧有结构，这里留空或根据需要添加
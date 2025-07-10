// 宠物食谱网站 - 主要JavaScript功能
document.addEventListener('DOMContentLoaded', function() {
    // 获取应用数据
    const appData = document.getElementById('app-data');
    
    // 应用状态管理
    const AppState = {
        isLoggedIn: appData.getAttribute('data-logged-in') === 'true',
        userId: appData.getAttribute('data-user-id'),
        userNickname: appData.getAttribute('data-user-nickname'),
        urls: {
            login: appData.getAttribute('data-login-url'),
            register: appData.getAttribute('data-register-url'),
            home: appData.getAttribute('data-home-url'),
            userCenter: appData.getAttribute('data-user-center-url')
        }
    };

    // 工具函数
    const Utils = {
        // 检查登录状态
        checkLoginStatus() {
            return AppState.isLoggedIn;
        },

        // 显示登录提示
        showLoginPrompt(message) {
            const fullMessage = message + '\n\n点击确定前往登录页面，点击取消留在当前页面。';
            if (confirm(fullMessage)) {
                window.location.href = AppState.urls.login;
            }
        },

        // 显示开发中提示
        showComingSoon(feature = '此功能') {
            alert(feature + '开发中，敬请期待！');
        }
    };

    // 导航栏功能
    const NavHandler = {
        init() {
            this.bindCreateRecipeBtn();
            this.bindLogoutBtn();
        },

        // 绑定创建食谱按钮
        bindCreateRecipeBtn() {
            const createRecipeNavBtn = document.getElementById('createRecipeNavBtn');
            if (createRecipeNavBtn) {
                createRecipeNavBtn.addEventListener('click', function(e) {
                    e.preventDefault();
                    if (!Utils.checkLoginStatus()) {
                        Utils.showLoginPrompt('请先登录后再创建食谱');
                    } else {
                        Utils.showComingSoon('创建食谱功能');
                    }
                });
            }
        },

        // 绑定退出登录按钮
        bindLogoutBtn() {
            const logoutBtn = document.getElementById('logoutBtn');
            if (logoutBtn) {
                logoutBtn.addEventListener('click', function(e) {
                    e.preventDefault();
                    if (confirm('确定要退出登录吗？')) {
                        NavHandler.performLogout();
                    }
                });
            }
        },

        // 执行退出登录
        async performLogout() {
            try {
                const response = await fetch('/user/logout', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    }
                });
                
                const data = await response.json();
                
                if (data.success) {
                    alert('退出登录成功');
                    window.location.href = AppState.urls.home;
                } else {
                    alert('退出登录失败');
                }
            } catch (error) {
                console.error('退出登录错误:', error);
                alert('网络错误，请稍后重试');
            }
        }
    };

    // 首页功能（如果在首页才初始化）
    const HomePageHandler = {
        init() {
            this.bindStartCreateBtn();
            this.bindFeatureCards();
            this.bindScrollToFeatures();
        },

        // 绑定立即创建食谱按钮
        bindStartCreateBtn() {
            const startCreateBtn = document.getElementById('startCreateBtn');
            if (startCreateBtn) {
                startCreateBtn.addEventListener('click', function() {
                    if (!Utils.checkLoginStatus()) {
                        Utils.showLoginPrompt('创建食谱需要先登录，请先登录您的账户。');
                    } else {
                        Utils.showComingSoon('创建食谱功能');
                    }
                });
            }
        },

        // 绑定功能卡片点击事件
        bindFeatureCards() {
            // 为功能卡片添加全局点击处理函数
            window.handleFeatureClick = function(feature) {
                const isLoggedIn = Utils.checkLoginStatus();
                
                switch(feature) {
                    case 'pet-info':
                        if (!isLoggedIn) {
                            Utils.showLoginPrompt('查看宠物信息功能需要先登录');
                        } else {
                            window.location.href = AppState.urls.userCenter;
                        }
                        break;
                    case 'ingredients':
                    case 'nutrition':
                    case 'recipes':
                        if (!isLoggedIn) {
                            Utils.showLoginPrompt('使用此功能需要先登录您的账户');
                        } else {
                            Utils.showComingSoon('此功能');
                        }
                        break;
                    case 'encyclopedia':
                        Utils.showComingSoon('食材百科功能');
                        break;
                    case 'community':
                        Utils.showComingSoon('社区功能');
                        break;
                    default:
                        Utils.showComingSoon();
                }
            };
        },

        // 绑定滚动到功能介绍
        bindScrollToFeatures() {
            window.scrollToFeatures = function() {
                const featuresSection = document.getElementById('features');
                if (featuresSection) {
                    featuresSection.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });
                }
            };
        }
    };

    // 初始化应用
    function initApp() {
        // 总是初始化导航栏功能
        NavHandler.init();
        
        // 如果在首页，初始化首页功能
        if (document.getElementById('home-page')) {
            HomePageHandler.init();
        }
        
        console.log('宠物食谱网站初始化完成', {
            isLoggedIn: AppState.isLoggedIn,
            userId: AppState.userId
        });
    }

    // 启动应用
    initApp();

    // 全局错误处理
    window.addEventListener('error', function(e) {
        console.error('JavaScript错误:', e.error);
    });

    // 暴露一些全局函数供其他页面使用
    window.PetRecipeApp = {
        Utils,
        AppState,
        NavHandler,
        HomePageHandler
    };
});
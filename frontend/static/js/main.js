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
            const fullMessage = message + '\n\nClick OK to go to the login page, or click Cancel to stay on the current page.';
            if (confirm(fullMessage)) {
                window.location.href = AppState.urls.login;
            }
        },

        // 显示开发中提示
        showComingSoon(feature = 'This feature') {
            alert(feature + ' is under development, stay tuned!');
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
                        Utils.showLoginPrompt('Please log in before creating a recipe');
                    } else {
                        Utils.showComingSoon('Create Recipe feature');
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
                    if (confirm('Are you sure you want to log out?')) {
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
                    alert('Logged out successfully');
                    window.location.href = AppState.urls.home;
                } else {
                    alert('Logout failed');
                }
            } catch (error) {
                console.error('Logout error:', error);
                alert('Network error, please try again later');
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
                        Utils.showLoginPrompt('Creating a recipe requires logging in first. Please log in to your account.');
                    } else {
                        Utils.showComingSoon('Create Recipe feature');
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
                            Utils.showLoginPrompt('Viewing pet information requires logging in first');
                        } else {
                            window.location.href = AppState.urls.userCenter;
                        }
                        break;
                    case 'ingredients':
                    case 'nutrition':
                    case 'recipes':
                        if (!isLoggedIn) {
                            Utils.showLoginPrompt('Using this feature requires logging in to your account first');
                        } else {
                            Utils.showComingSoon('This feature');
                        }
                        break;
                    case 'encyclopedia':
                        Utils.showComingSoon('Ingredient Encyclopedia feature');
                        break;
                    case 'community':
                        Utils.showComingSoon('Community feature');
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
        
        console.log('Pet Recipe Website initialization complete', {
            isLoggedIn: AppState.isLoggedIn,
            userId: AppState.userId
        });
    }

    // 启动应用
    initApp();

    // 全局错误处理
    window.addEventListener('error', function(e) {
        console.error('JavaScript error:', e.error);
    });

    // 暴露一些全局函数供其他页面使用
    window.PetRecipeApp = {
        Utils,
        AppState,
        NavHandler,
        HomePageHandler
    };
});
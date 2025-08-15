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
        }
    };

    // 模态框管理
    const ModalManager = {
        currentNavigateUrl: null,

        // 显示功能信息模态框
        showFeatureModal(featureData) {
            const modal = document.getElementById('featureModal');
            const title = document.getElementById('modalFeatureTitle');
            const description = document.getElementById('modalFeatureDescription');
            const highlights = document.getElementById('modalFeatureHighlights');
            const navigateBtn = document.getElementById('modalNavigateBtn');

            // 设置模态框内容
            title.textContent = featureData.title;
            description.textContent = featureData.description;

            // 设置功能亮点（移除图标相关代码）
            if (featureData.highlights && featureData.highlights.length > 0) {
                highlights.innerHTML = featureData.highlights.map(highlight => `
                    <div class="highlight-item">
                        <div class="highlight-text">${highlight.text}</div>
                    </div>
                `).join('');
            } else {
                highlights.innerHTML = '';
            }

            // 设置导航按钮
            if (featureData.navigateUrl) {
                this.currentNavigateUrl = featureData.navigateUrl;
                navigateBtn.style.display = 'inline-flex';
            } else {
                this.currentNavigateUrl = null;
                navigateBtn.style.display = 'none';
            }

            // 显示模态框
            modal.style.display = 'flex';
            setTimeout(() => modal.classList.add('show'), 10);
            document.body.style.overflow = 'hidden';
        },

        // 关闭模态框
        closeModal() {
            const modal = document.getElementById('featureModal');
            modal.classList.remove('show');
            setTimeout(() => {
                modal.style.display = 'none';
                document.body.style.overflow = '';
                this.currentNavigateUrl = null;
            }, 300);
        },

        // 导航到功能页面
        navigate() {
            if (this.currentNavigateUrl) {
                this.closeModal();
                setTimeout(() => {
                    window.location.href = this.currentNavigateUrl;
                }, 200);
            }
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
                        window.location.href = '/recipe/create_recipe';
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
                        window.location.href = '/recipe/create_recipe';
                    }
                });
            }
        },

        // 绑定功能卡片点击事件 - 使用模态框显示（移除图标）
        bindFeatureCards() {
            // 为功能卡片添加全局点击处理函数
            window.handleFeatureClick = function(feature) {
                const featureConfigs = {
                    'pet-info': {
                        title: 'Pet Information Management',
                        description: 'Create comprehensive profiles for your pets to enable personalized nutrition recommendations. Record essential information including species, breed, weight, age, and special dietary requirements to get the most accurate recipe suggestions for your furry friends.',
                        highlights: [
                            { text: 'Multi-pet support with individual profiles for each of your pets' },
                            { text: 'Weight and age tracking for accurate portion calculations' },
                            { text: 'Special needs and health condition records for customized diets' },
                            { text: 'Growth and health monitoring over time to track progress' },
                            { text: 'Easy profile editing and management from your user center' }
                        ],
                        navigateUrl: Utils.checkLoginStatus() ? AppState.urls.userCenter : null
                    },
                    'ingredients': {
                        title: 'Ingredient Selection System',
                        description: 'Access our comprehensive ingredient database with detailed nutritional information. Choose from a wide variety of fresh meats, vegetables, fruits, grains, and supplements to create perfectly balanced meals tailored to your pet\'s specific needs.',
                        highlights: [
                            { text: 'Extensive ingredient library with complete nutritional data for each item' },
                            { text: 'Pet safety information and allergen warnings for all ingredients' },
                            { text: 'Precise portion calculation and automatic scaling based on pet size' },
                            { text: 'Seasonal availability guides to help you choose the freshest options' },
                            { text: 'Custom ingredient combinations with real-time nutrition analysis' }
                        ]
                    },
                    'nutrition': {
                        title: 'Advanced Nutritional Analysis',
                        description: 'Get real-time nutritional analysis with professional-grade accuracy. View detailed breakdowns of proteins, fats, carbohydrates, vitamins, and minerals with interactive visual charts and personalized recommendations based on your pet\'s profile.',
                        highlights: [
                            { text: 'Interactive charts and visual nutrition breakdown for easy understanding' },
                            { text: 'Detailed micronutrient analysis including vitamins and minerals' },
                            { text: 'Nutritional deficiency and excess warnings with recommendations' },
                            { text: 'Professional veterinary standards compliance for optimal pet health' },
                            { text: 'Comparison with recommended daily values for your specific pet' }
                        ]
                    },
                    'recipes': {
                        title: 'Smart Recipe Recommendations',
                        description: 'Discover personalized recipe recommendations powered by advanced algorithms that consider your pet\'s unique profile, dietary needs, and preferences. Save your favorites, share successful recipes with the community, and build a collection of tried-and-tested meals.',
                        highlights: [
                            { text: 'AI-powered personalized recommendations based on your pet\'s profile' },
                            { text: 'Save and organize your favorite recipes in a personal collection' },
                            { text: 'Community-rated recipes with reviews from other pet owners' },
                            { text: 'Meal planning tools and feeding schedule suggestions' },
                            { text: 'Recipe modification suggestions for dietary restrictions or preferences' }
                        ]
                    },
                    'encyclopedia': {
                        title: 'Comprehensive Ingredient Encyclopedia',
                        description: 'Explore our extensive database of pet-safe ingredients with detailed information about nutritional benefits, preparation methods, and safety guidelines specifically designed for dogs and cats. Learn about ingredient interactions and optimal preparation techniques.',
                        highlights: [
                            { text: 'Detailed ingredient profiles with complete nutritional and safety information' },
                            { text: 'Preparation tips and cooking methods for optimal nutrient retention' },
                            { text: 'Advanced search and filtering options by category, nutrition, or safety' },
                            { text: 'Educational content and expert nutrition guides for informed decisions' },
                            { text: 'Regular updates with new ingredients and latest research findings' }
                        ],
                        navigateUrl: '/encyclopedia'
                    },
                    'community': {
                        title: 'Pet Owner Community Hub',
                        description: 'Connect with fellow pet owners from around the world, share your favorite recipes, get advice from experienced owners, and discover new feeding ideas from our growing community of dedicated pet lovers who prioritize their pets\' health and happiness.',
                        highlights: [
                            { text: 'Share recipes and feeding experiences with a supportive community' },
                            { text: 'Get expert advice from experienced pet owners and professionals' },
                            { text: 'Rate and review community recipes with detailed feedback systems' },
                            { text: 'Join discussions about pet nutrition, health, and feeding challenges' },
                            { text: 'Build connections with like-minded pet lovers in your area or globally' }
                        ],
                        navigateUrl: '/community'
                    }
                };

                const config = featureConfigs[feature];
                if (config) {
                    ModalManager.showFeatureModal(config);
                } else {
                    // 兜底配置
                    ModalManager.showFeatureModal({
                        title: 'Pet Nutrition Feature',
                        description: 'This feature provides comprehensive tools for managing your pet\'s nutrition and health with professional-grade accuracy and personalized recommendations.',
                        highlights: [
                            { text: 'Professional-grade nutrition management tools' },
                            { text: 'Personalized recommendations for your pet' },
                            { text: 'Easy-to-use interface with comprehensive features' }
                        ]
                    });
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

    // 全局模态框控制函数
    window.closeFeatureModal = function(event) {
        if (event && event.target !== event.currentTarget) return;
        ModalManager.closeModal();
    };

    window.navigateToFeature = function() {
        ModalManager.navigate();
    };

    // ESC键关闭模态框
    document.addEventListener('keydown', function(event) {
        if (event.key === 'Escape') {
            const modal = document.getElementById('featureModal');
            if (modal && modal.classList.contains('show')) {
                ModalManager.closeModal();
            }
        }
    });

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
        HomePageHandler,
        ModalManager
    };
});
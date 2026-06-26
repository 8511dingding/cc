// 平滑滚动和导航高亮
document.addEventListener('DOMContentLoaded', () => {
    // 导航高亮
    const sections = document.querySelectorAll('.section');
    const navItems = document.querySelectorAll('.nav-item');

    // 滚动时更新高亮
    const observer = new IntersectionObserver(
        (entries) => {
            entries.forEach((entry) => {
                if (entry.isIntersecting) {
                    navItems.forEach((item) => {
                        item.classList.remove('active');
                        if (item.getAttribute('href') === `#${entry.target.id}`) {
                            item.classList.add('active');
                        }
                    });
                }
            });
        },
        { threshold: 0.3 }
    );

    sections.forEach((section) => observer.observe(section));

    // 导航点击平滑滚动
    navItems.forEach((item) => {
        item.addEventListener('click', (e) => {
            e.preventDefault();
            const targetId = item.getAttribute('href');
            const targetSection = document.querySelector(targetId);
            if (targetSection) {
                targetSection.scrollIntoView({ behavior: 'smooth' });
            }
        });
    });
});

"""
自动登录并点击营销业务看板（2026年度）- 改进版
根据实际页面结构调整
"""
from oa_scraper import OAScraper
import time
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def click_marketing_dashboard():
    """登录并点击营销业务看板"""
    scraper = OAScraper()
    
    try:
        logger.info("=== 开始执行任务 ===")
        
        # 1. 启动浏览器
        logger.info("1. 启动浏览器...")
        scraper.start(headless=False)  # 显示浏览器窗口
        
        # 2. 登录
        logger.info("2. 登录系统...")
        if not scraper.login():
            logger.error("登录失败，任务终止")
            return False
        
        logger.info("登录成功，等待页面完全加载...")
        time.sleep(8)  # 增加等待时间，让页面完全加载
        
        # 截图当前状态
        scraper.screenshot('step1_after_login.png')
        logger.info("已截图：step1_after_login.png")
        
        # 3. 尝试多种方式查找"选择"按钮或"营销业务看板"
        logger.info("3. 查找并点击目标元素...")
        
        clicked = False
        
        # 方法1: 查找包含"选择"文本的按钮
        logger.info("方法1: 查找'选择'按钮...")
        select_button_selectors = [
            'button:has-text("选择")',
            'a:has-text("选择")',
            'div:has-text("选择")',
            'span:has-text("选择")',
            ':text("选择")'
        ]
        
        for selector in select_button_selectors:
            try:
                logger.info(f"尝试选择器: {selector}")
                elements = scraper.page.locator(selector).all()
                
                if elements:
                    logger.info(f"找到 {len(elements)} 个匹配'选择'的元素")
                    # 尝试点击每一个，看哪个是正确的
                    for i, element in enumerate(elements):
                        try:
                            if element.is_visible():
                                # 检查这个元素附近是否有"营销业务看板"文本
                                parent = element.locator('xpath=ancestor::*[contains(., "营销业务看板")]').first
                                if parent:
                                    logger.info(f"找到与'营销业务看板'相关的'选择'按钮 (第{i+1}个)")
                                    element.click()
                                    clicked = True
                                    break
                        except:
                            # 如果找不到父元素，直接尝试点击
                            try:
                                if element.is_visible():
                                    logger.info(f"尝试点击第 {i+1} 个'选择'按钮")
                                    element.click()
                                    time.sleep(2)
                                    # 检查是否跳转成功
                                    if '营销业务看板' in scraper.page.content() or 'dashboard' in scraper.page.url.lower():
                                        clicked = True
                                        break
                                    else:
                                        logger.info("点击后未跳转到目标页面，继续尝试")
                            except Exception as e:
                                logger.debug(f"点击失败: {e}")
                                continue
                
                if clicked:
                    break
            except Exception as e:
                logger.debug(f"选择器 {selector} 失败: {e}")
                continue
        
        # 方法2: 直接查找"营销业务看板（2026年度）"并点击
        if not clicked:
            logger.info("方法2: 直接查找'营销业务看板（2026年度）'...")
            dashboard_selectors = [
                ':text("营销业务看板（2026年度）")',
                ':text("营销业务看板")',
                'div:has-text("营销业务看板（2026年度）")',
                'span:has-text("营销业务看板（2026年度）")',
                'a:has-text("营销业务看板（2026年度）")'
            ]
            
            for selector in dashboard_selectors:
                try:
                    logger.info(f"尝试选择器: {selector}")
                    elements = scraper.page.locator(selector).all()
                    
                    if elements:
                        logger.info(f"找到 {len(elements)} 个匹配元素")
                        for i, element in enumerate(elements):
                            try:
                                if element.is_visible():
                                    logger.info(f"点击第 {i+1} 个元素")
                                    element.click()
                                    clicked = True
                                    break
                            except Exception as e:
                                logger.debug(f"元素 {i+1} 点击失败: {e}")
                                continue
                    
                    if clicked:
                        break
                except Exception as e:
                    logger.debug(f"选择器 {selector} 失败: {e}")
                    continue
        
        # 方法3: 使用JavaScript查找并点击
        if not clicked:
            logger.info("方法3: 使用JavaScript查找...")
            try:
                clicked = scraper.page.evaluate('''
                    () => {
                        // 查找所有包含"营销业务看板"或"选择"的元素
                        const allElements = Array.from(document.querySelectorAll('*'));
                        
                        for (const elem of allElements) {
                            const text = elem.innerText || elem.textContent || '';
                            
                            // 查找"选择"按钮，且附近有"营销业务看板"
                            if (text.includes('选择')) {
                                const parent = elem.closest('*');
                                const parentText = parent ? (parent.innerText || parent.textContent || '') : '';
                                
                                if (parentText.includes('营销业务看板')) {
                                    const style = window.getComputedStyle(elem);
                                    if (style.display !== 'none' && style.visibility !== 'hidden') {
                                        elem.click();
                                        return true;
                                    }
                                }
                            }
                            
                            // 或者直接点击"营销业务看板"
                            if (text.includes('营销业务看板（2026年度）') || text.includes('营销业务看板')) {
                                const style = window.getComputedStyle(elem);
                                if (style.display !== 'none' && style.visibility !== 'hidden') {
                                    elem.click();
                                    return true;
                                }
                            }
                        }
                        return false;
                    }
                ''')
                
                if clicked:
                    logger.info("通过JavaScript成功点击")
            except Exception as e:
                logger.error(f"JavaScript方法失败: {e}")
        
        if not clicked:
            logger.error("未找到可点击的元素")
            scraper.screenshot('element_not_found.png')
            
            # 保存页面HTML
            with open('page_debug.html', 'w', encoding='utf-8') as f:
                f.write(scraper.page.content())
            logger.info("页面内容已保存到 page_debug.html")
            
            return False
        
        # 4. 等待新页面加载
        logger.info("4. 等待页面加载...")
        time.sleep(5)
        scraper.page.wait_for_load_state('networkidle', timeout=20000)
        
        # 5. 截图保存
        logger.info("5. 截图保存...")
        timestamp = time.strftime('%Y%m%d_%H%M%S')
        screenshot_path = scraper.screenshot(f'marketing_dashboard_{timestamp}.png')
        
        logger.info(f"✓ 任务完成！截图已保存: {screenshot_path}")
        logger.info(f"当前页面URL: {scraper.page.url}")
        
        # 等待一下让用户查看
        logger.info("\n等待10秒后自动关闭浏览器...")
        time.sleep(10)
        
        return True
        
    except Exception as e:
        logger.error(f"任务执行失败: {e}")
        import traceback
        traceback.print_exc()
        scraper.screenshot('error.png')
        return False
        
    finally:
        scraper.close()
        logger.info("=== 任务结束 ===")


if __name__ == '__main__':
    click_marketing_dashboard()

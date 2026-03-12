"""
自动登录并点击营销业务看板（2026年度）- 最终版
处理登录后打开新窗口的情况
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
        scraper.start(headless=False)
        
        # 2. 登录
        logger.info("2. 登录系统...")
        if not scraper.login():
            logger.error("登录失败，任务终止")
            return False
        
        logger.info("登录成功，等待新窗口打开...")
        
        # 3. 等待新窗口打开
        time.sleep(5)
        
        # 获取所有页面（包括新打开的窗口）
        pages = scraper.context.pages
        logger.info(f"当前共有 {len(pages)} 个页面/窗口")
        
        # 切换到最新打开的窗口（通常是主窗口）
        if len(pages) > 1:
            logger.info("检测到新窗口，切换到新窗口...")
            scraper.page = pages[-1]  # 最后一个是最新打开的
            scraper.page.bring_to_front()
        
        # 等待主页面加载
        logger.info("等待主页面加载...")
        time.sleep(5)
        scraper.page.wait_for_load_state('networkidle', timeout=20000)
        
        logger.info(f"当前页面URL: {scraper.page.url}")
        logger.info(f"页面标题: {scraper.page.title()}")
        
        # 截图
        scraper.screenshot('step1_main_page.png')
        logger.info("主页面截图已保存")
        
        # 4. 先点击"营销业务看板（2026年度）"
        logger.info("3. 查找营销业务看板（2026年度）...")
        
        clicked_dashboard = False
        
        # 先检查所有frame
        frames = scraper.page.frames
        logger.info(f"主页面共有 {len(frames)} 个frame")
        for i, frame in enumerate(frames):
            logger.info(f"  Frame {i}: name='{frame.name}', url='{frame.url[:80] if frame.url else ''}'")
        
        # 第一步：点击"营销业务看板（2026年度）"文本
        logger.info("第一步: 点击'营销业务看板（2026年度）'...")
        dashboard_selectors = [
            ':text("营销业务看板（2026年度）")',
            ':text("营销业务看板")',
            'div:has-text("营销业务看板（2026年度）")',
            'span:has-text("营销业务看板（2026年度）")'
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
                                clicked_dashboard = True
                                time.sleep(1)  # 等待一下
                                break
                        except Exception as e:
                            logger.debug(f"元素 {i+1} 点击失败: {e}")
                            continue
                
                if clicked_dashboard:
                    break
            except Exception as e:
                logger.debug(f"选择器 {selector} 失败: {e}")
                continue
        
        if not clicked_dashboard:
            logger.error("未找到'营销业务看板（2026年度）'")
            scraper.screenshot('dashboard_text_not_found.png')
            return False
        
        logger.info("成功点击'营销业务看板（2026年度）'")
        scraper.screenshot('step2_after_click_dashboard.png')
        
        # 第二步：点击"选择"按钮
        logger.info("第二步: 查找并点击'选择'按钮...")
        time.sleep(1)
        
        clicked_select = False
        select_selectors = [
            'button:has-text("选择")',
            'a:has-text("选择")',
            'div:has-text("选择")',
            'span:has-text("选择")',
            ':text("选择")'
        ]
        
        for selector in select_selectors:
            try:
                logger.info(f"尝试选择器: {selector}")
                elements = scraper.page.locator(selector).all()
                
                if elements:
                    logger.info(f"找到 {len(elements)} 个'选择'按钮")
                    for i, element in enumerate(elements):
                        try:
                            if element.is_visible():
                                logger.info(f"点击第 {i+1} 个'选择'按钮")
                                element.click()
                                clicked_select = True
                                break
                        except Exception as e:
                            logger.debug(f"按钮 {i+1} 点击失败: {e}")
                            continue
                
                if clicked_select:
                    break
            except Exception as e:
                logger.debug(f"选择器 {selector} 失败: {e}")
                continue
        
        if not clicked_select:
            logger.error("未找到'选择'按钮")
            scraper.screenshot('select_button_not_found.png')
            return False
        
        logger.info("成功点击'选择'按钮")
        clicked = True
        

        
        if not clicked:
            logger.error("未能完成操作")
            scraper.screenshot('operation_failed.png')
            return False
        
        # 5. 等待页面加载
        logger.info("4. 等待目标页面加载...")
        time.sleep(5)
        scraper.page.wait_for_load_state('networkidle', timeout=20000)
        
        # 6. 截图保存
        logger.info("5. 截图保存...")
        timestamp = time.strftime('%Y%m%d_%H%M%S')
        screenshot_path = scraper.screenshot(f'marketing_dashboard_{timestamp}.png')
        
        logger.info(f"✓ 任务完成！截图已保存: {screenshot_path}")
        logger.info(f"当前页面URL: {scraper.page.url}")
        
        # 等待查看
        logger.info("\n等待10秒后自动关闭...")
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

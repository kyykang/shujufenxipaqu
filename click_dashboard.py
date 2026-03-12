"""
自动登录并点击营销业务看板（2026年度）
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
        time.sleep(5)  # 增加等待时间
        scraper.page.wait_for_load_state('networkidle', timeout=20000)
        
        # 等待frame加载
        logger.info("等待frame加载...")
        time.sleep(3)
        
        # 打印所有frame信息
        frames = scraper.page.frames
        logger.info(f"当前页面共有 {len(frames)} 个frame")
        for i, frame in enumerate(frames):
            logger.info(f"Frame {i}: name='{frame.name}', url='{frame.url}'")
        
        # 截图当前状态
        scraper.screenshot('after_login_full.png')
        
        # 3. 查找并点击"营销业务看板（2026年度）"
        logger.info("3. 查找营销业务看板（2026年度）...")
        
        # 尝试多种可能的选择器
        dashboard_selectors = [
            ':text("营销业务看板（2026年度）")',
            ':text("营销业务看板")',
            ':text("2026年度")',
            'a:has-text("营销业务看板（2026年度）")',
            'a:has-text("营销业务看板")',
            'span:has-text("营销业务看板（2026年度）")',
            'div:has-text("营销业务看板（2026年度）")',
            '*:has-text("营销业务看板（2026年度）")',
            '*:has-text("营销业务看板")'
        ]
        
        clicked = False
        
        # 先在主页面查找
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
        
        # 如果主页面没找到，尝试在各个frame中查找
        if not clicked:
            logger.info("在主页面未找到，尝试在frame中查找...")
            frames = scraper.page.frames
            logger.info(f"共有 {len(frames)} 个frame")
            
            for frame_idx, frame in enumerate(frames):
                if clicked:
                    break
                    
                logger.info(f"检查frame {frame_idx}: name='{frame.name}', url='{frame.url[:100] if frame.url else ''}'")
                
                # 先尝试用JavaScript在frame中查找
                try:
                    frame_html = frame.content()
                    if '营销业务看板' in frame_html:
                        logger.info(f"在frame {frame.name} 中发现'营销业务看板'文本")
                        
                        # 保存这个frame的HTML用于调试
                        with open(f'frame_{frame_idx}_{frame.name}.html', 'w', encoding='utf-8') as f:
                            f.write(frame_html)
                        logger.info(f"Frame内容已保存到 frame_{frame_idx}_{frame.name}.html")
                except Exception as e:
                    logger.debug(f"无法获取frame {frame_idx} 的内容: {e}")
                
                for selector in dashboard_selectors:
                    try:
                        elements = frame.locator(selector).all()
                        if elements:
                            logger.info(f"在frame {frame.name} 中找到 {len(elements)} 个匹配元素")
                            for i, element in enumerate(elements):
                                try:
                                    if element.is_visible():
                                        logger.info(f"点击frame中的第 {i+1} 个元素")
                                        element.click()
                                        clicked = True
                                        break
                                except Exception as e:
                                    logger.debug(f"元素 {i+1} 点击失败: {e}")
                                    continue
                        
                        if clicked:
                            break
                    except Exception as e:
                        logger.debug(f"frame {frame.name} 中选择器 {selector} 失败: {e}")
                        continue
        
        if not clicked:
            logger.error("未找到营销业务看板（2026年度）")
            scraper.screenshot('dashboard_not_found.png')
            
            # 保存页面HTML用于调试
            with open('page_content.html', 'w', encoding='utf-8') as f:
                f.write(scraper.page.content())
            logger.info("页面内容已保存到 page_content.html")
            
            return False
        
        # 4. 等待新页面加载
        logger.info("4. 等待页面加载...")
        time.sleep(3)
        scraper.page.wait_for_load_state('networkidle', timeout=15000)
        
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

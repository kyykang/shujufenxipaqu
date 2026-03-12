"""
手动导航辅助工具
登录后暂停，让用户手动导航到目标页面，然后分析页面结构
"""
from oa_scraper import OAScraper
import time
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def manual_navigate():
    """手动导航辅助"""
    scraper = OAScraper()
    
    try:
        logger.info("=== 手动导航辅助工具 ===")
        
        # 1. 启动浏览器
        logger.info("1. 启动浏览器...")
        scraper.start(headless=False)
        
        # 2. 登录
        logger.info("2. 登录系统...")
        if not scraper.login():
            logger.error("登录失败")
            return
        
        logger.info("登录成功！")
        time.sleep(3)
        
        print("\n" + "="*60)
        print("请在浏览器中手动操作：")
        print("1. 找到并点击'营销业务看板（2026年度）'")
        print("2. 点击'选择'按钮")
        print("3. 进入目标页面后")
        print("4. 回到这个终端，按 Enter 键继续")
        print("="*60 + "\n")
        
        input("按 Enter 继续...")
        
        # 分析当前页面
        logger.info("\n=== 分析当前页面 ===")
        logger.info(f"当前URL: {scraper.page.url}")
        logger.info(f"页面标题: {scraper.page.title()}")
        
        # 截图
        timestamp = time.strftime('%Y%m%d_%H%M%S')
        screenshot_path = scraper.screenshot(f'manual_target_page_{timestamp}.png')
        logger.info(f"截图已保存: {screenshot_path}")
        
        # 保存HTML
        html_file = f'manual_target_page_{timestamp}.html'
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(scraper.page.content())
        logger.info(f"页面HTML已保存: {html_file}")
        
        # 检查frame
        frames = scraper.page.frames
        logger.info(f"\n页面共有 {len(frames)} 个frame:")
        for i, frame in enumerate(frames):
            logger.info(f"  Frame {i}: name='{frame.name}', url='{frame.url}'")
            
            # 保存frame的HTML
            try:
                frame_html = frame.content()
                frame_file = f'manual_frame_{i}_{frame.name}_{timestamp}.html'
                with open(frame_file, 'w', encoding='utf-8') as f:
                    f.write(frame_html)
                logger.info(f"    Frame HTML已保存: {frame_file}")
            except Exception as e:
                logger.debug(f"    无法保存frame HTML: {e}")
        
        print("\n" + "="*60)
        print("分析完成！")
        print(f"- 截图: {screenshot_path}")
        print(f"- HTML: {html_file}")
        print("请将这些文件发给我，我可以帮你编写自动化脚本")
        print("="*60 + "\n")
        
        input("按 Enter 关闭浏览器...")
        
    except Exception as e:
        logger.error(f"出错: {e}")
        import traceback
        traceback.print_exc()
    finally:
        scraper.close()


if __name__ == '__main__':
    manual_navigate()

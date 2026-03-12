"""
测试登录功能
用于验证登录流程是否正常
"""
from oa_scraper import OAScraper
import time


def test_login():
    """测试登录"""
    print("=== 致远Seeyon OA登录测试 ===\n")
    
    scraper = OAScraper()
    
    try:
        print("1. 启动浏览器（显示窗口以便观察）...")
        scraper.start(headless=False)
        
        print("2. 尝试登录...")
        if scraper.login():
            print("✓ 登录成功！")
            
            # 显示当前URL
            print(f"\n当前页面: {scraper.page.url}")
            
            # 显示页面标题
            print(f"页面标题: {scraper.page.title()}")
            
            # 等待一下让用户观察
            print("\n等待5秒以便观察页面...")
            time.sleep(5)
            
            # 尝试获取一些基本信息
            print("\n3. 尝试获取页面信息...")
            
            # 检查是否有frame结构（Seeyon常用）
            frames = scraper.page.frames
            print(f"页面frame数量: {len(frames)}")
            for i, frame in enumerate(frames):
                print(f"  Frame {i}: {frame.name} - {frame.url}")
            
            print("\n✓ 测试完成！")
            print("\n截图已保存到 screenshots/ 目录")
            print("- before_login.png: 登录前")
            print("- after_login.png: 登录后")
            
        else:
            print("✗ 登录失败")
            print("\n请检查:")
            print("1. .env 文件中的用户名密码是否正确")
            print("2. 网络连接是否正常")
            print("3. 查看 screenshots/ 目录中的截图")
            print("4. 查看 oa_scraper.log 日志文件")
        
    except Exception as e:
        print(f"\n✗ 测试出错: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        print("\n按Enter键关闭浏览器...")
        input()
        scraper.close()


if __name__ == '__main__':
    test_login()

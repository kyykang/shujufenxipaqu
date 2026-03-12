"""
选择器查找辅助工具
用于帮助识别致远OA页面的元素选择器
"""
from playwright.sync_api import sync_playwright
import os
from dotenv import load_dotenv

load_dotenv()


def find_selectors():
    """交互式查找页面元素选择器"""
    oa_url = os.getenv('OA_URL')
    
    if not oa_url:
        print("错误: 请先在 .env 文件中配置 OA_URL")
        return
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        
        print(f"\n正在打开页面: {oa_url}")
        page.goto(oa_url)
        
        print("\n=== 选择器查找工具 ===")
        print("浏览器已打开，请按照以下步骤操作：")
        print("\n1. 在浏览器中右键点击要定位的元素")
        print("2. 选择 '检查' 或 'Inspect'")
        print("3. 在开发者工具中右键该元素")
        print("4. 选择 Copy -> Copy selector")
        print("\n常见元素选择器示例：")
        print("-" * 50)
        
        # 尝试自动识别常见元素
        common_selectors = {
            "用户名输入框": [
                'input[name="loginid"]',
                'input[name="username"]', 
                'input[id="username"]',
                'input[type="text"]',
                '#loginid',
                '#username'
            ],
            "密码输入框": [
                'input[name="userpassword"]',
                'input[name="password"]',
                'input[type="password"]',
                '#password',
                '#userpassword'
            ],
            "登录按钮": [
                'button[type="submit"]',
                'input[type="submit"]',
                'button.login-btn',
                '#loginBtn',
                '.login-button'
            ]
        }
        
        found_selectors = {}
        
        for element_name, selectors in common_selectors.items():
            for selector in selectors:
                try:
                    element = page.query_selector(selector)
                    if element and element.is_visible():
                        found_selectors[element_name] = selector
                        print(f"✓ {element_name}: {selector}")
                        break
                except:
                    continue
            
            if element_name not in found_selectors:
                print(f"✗ {element_name}: 未找到（需要手动确认）")
        
        print("-" * 50)
        print("\n按 Enter 继续，或输入 'q' 退出...")
        
        # 等待用户操作
        input()
        
        # 保存找到的选择器
        if found_selectors:
            print("\n找到的选择器已保存到 selectors.txt")
            with open('selectors.txt', 'w', encoding='utf-8') as f:
                f.write("# 致远OA页面选择器\n")
                f.write(f"# 生成时间: {page.evaluate('new Date().toLocaleString()')}\n\n")
                for name, selector in found_selectors.items():
                    f.write(f"{name}: {selector}\n")
        
        browser.close()


if __name__ == '__main__':
    find_selectors()

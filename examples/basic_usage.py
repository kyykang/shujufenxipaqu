"""
基本使用示例
"""
import sys
sys.path.append('..')

from oa_scraper import OAScraper


def example_basic():
    """基本使用示例"""
    scraper = OAScraper()
    
    try:
        # 启动浏览器（调试时设置headless=False）
        scraper.start(headless=False)
        
        # 登录
        if not scraper.login():
            print("登录失败")
            return
        
        # 截图保存登录后的页面
        scraper.screenshot('after_login.png')
        
        # 示例1: 抓取特定元素的文本
        print("\n=== 示例1: 抓取文本内容 ===")
        data = scraper.fetch_data(
            data_url=f"{scraper.oa_url}/main",  # 替换为实际URL
            selector='body'  # 替换为实际选择器
        )
        if data:
            print(f"抓取到的数据长度: {len(data)} 字符")
        
        # 示例2: 抓取表格数据
        print("\n=== 示例2: 抓取表格数据 ===")
        table_data = scraper.fetch_table_data(
            table_url=f"{scraper.oa_url}/table-page",  # 替换为实际URL
            table_selector='table'  # 替换为实际选择器
        )
        
        if table_data:
            print(f"抓取到 {len(table_data)} 行数据")
            # 保存为CSV
            scraper.save_to_csv(table_data, 'table_data.csv')
            # 保存为JSON
            scraper.save_to_json(table_data, 'table_data.json')
        
    finally:
        scraper.close()


if __name__ == '__main__':
    example_basic()

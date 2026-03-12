"""
高级使用示例
"""
import sys
sys.path.append('..')

from oa_scraper import OAScraper
import time


def example_multiple_pages():
    """抓取多个页面的数据"""
    scraper = OAScraper()
    
    try:
        scraper.start(headless=True)
        
        if not scraper.login():
            return
        
        # 要抓取的页面列表
        pages = [
            {'url': '/page1', 'name': '页面1'},
            {'url': '/page2', 'name': '页面2'},
            {'url': '/page3', 'name': '页面3'},
        ]
        
        all_data = {}
        
        for page_info in pages:
            print(f"正在抓取: {page_info['name']}")
            data = scraper.fetch_data(
                data_url=f"{scraper.oa_url}{page_info['url']}",
                selector='.content'
            )
            all_data[page_info['name']] = data
            time.sleep(2)  # 延迟
        
        # 保存所有数据
        scraper.save_to_json(all_data, 'all_pages_data.json')
        print("所有数据已保存")
        
    finally:
        scraper.close()


def example_with_pagination():
    """处理分页数据"""
    scraper = OAScraper()
    
    try:
        scraper.start(headless=True)
        
        if not scraper.login():
            return
        
        all_rows = []
        page_num = 1
        max_pages = 10  # 最多抓取10页
        
        while page_num <= max_pages:
            print(f"正在抓取第 {page_num} 页...")
            
            # 访问分页URL
            table_data = scraper.fetch_table_data(
                table_url=f"{scraper.oa_url}/list?page={page_num}",
                table_selector='table.data-table'
            )
            
            if not table_data or len(table_data) <= 1:  # 只有表头或没有数据
                print("没有更多数据")
                break
            
            # 跳过表头（如果需要）
            if page_num == 1:
                all_rows.extend(table_data)
            else:
                all_rows.extend(table_data[1:])  # 跳过表头
            
            # 检查是否有下一页
            has_next = scraper.page.query_selector('.next-page:not(.disabled)')
            if not has_next:
                break
            
            page_num += 1
            time.sleep(2)
        
        # 保存数据
        scraper.save_to_csv(all_rows, 'paginated_data.csv')
        print(f"共抓取 {len(all_rows)} 行数据")
        
    finally:
        scraper.close()


def example_with_filters():
    """使用筛选条件抓取数据"""
    scraper = OAScraper()
    
    try:
        scraper.start(headless=False)
        
        if not scraper.login():
            return
        
        # 访问列表页面
        scraper.page.goto(f"{scraper.oa_url}/list")
        scraper.page.wait_for_load_state('networkidle')
        
        # 设置筛选条件
        print("设置筛选条件...")
        
        # 选择日期范围
        scraper.page.fill('input[name="start_date"]', '2024-01-01')
        scraper.page.fill('input[name="end_date"]', '2024-12-31')
        
        # 选择下拉框
        scraper.page.select_option('select[name="status"]', 'approved')
        
        # 点击查询按钮
        scraper.wait_and_click('button.search-btn')
        scraper.page.wait_for_load_state('networkidle')
        
        # 抓取筛选后的数据
        table_data = scraper.fetch_table_data(
            table_url=scraper.page.url,
            table_selector='table.result-table'
        )
        
        if table_data:
            scraper.save_to_csv(table_data, 'filtered_data.csv')
            print(f"筛选后共 {len(table_data)} 行数据")
        
    finally:
        scraper.close()


if __name__ == '__main__':
    print("选择示例:")
    print("1. 抓取多个页面")
    print("2. 处理分页数据")
    print("3. 使用筛选条件")
    
    choice = input("请输入选项 (1-3): ")
    
    if choice == '1':
        example_multiple_pages()
    elif choice == '2':
        example_with_pagination()
    elif choice == '3':
        example_with_filters()
    else:
        print("无效选项")

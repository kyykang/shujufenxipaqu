"""
致远Seeyon系统专用辅助函数
"""
from oa_scraper import OAScraper
import time
import logging

logger = logging.getLogger(__name__)


class SeeyonHelper(OAScraper):
    """致远Seeyon系统专用辅助类"""
    
    def switch_to_frame(self, frame_name):
        """
        切换到指定的frame
        Seeyon系统通常使用frame结构
        
        Args:
            frame_name: frame的name属性，如 'top', 'left', 'main'
        """
        try:
            frame = self.page.frame(frame_name)
            if frame:
                logger.info(f"已切换到frame: {frame_name}")
                return frame
            else:
                logger.error(f"未找到frame: {frame_name}")
                return None
        except Exception as e:
            logger.error(f"切换frame失败: {e}")
            return None
    
    def get_frame_content(self, frame_name, selector=None):
        """
        获取指定frame中的内容
        
        Args:
            frame_name: frame名称
            selector: CSS选择器（可选）
        """
        try:
            frame = self.page.frame(frame_name)
            if not frame:
                logger.error(f"未找到frame: {frame_name}")
                return None
            
            if selector:
                frame.wait_for_selector(selector, timeout=5000)
                return frame.inner_text(selector)
            else:
                return frame.content()
        except Exception as e:
            logger.error(f"获取frame内容失败: {e}")
            return None
    
    def navigate_menu(self, menu_path):
        """
        导航到指定菜单
        
        Args:
            menu_path: 菜单路径列表，如 ['协同工作', '新建协同']
        """
        try:
            logger.info(f"导航到菜单: {' -> '.join(menu_path)}")
            
            # 通常菜单在left frame中
            left_frame = self.page.frame('left')
            if not left_frame:
                logger.error("未找到left frame")
                return False
            
            for menu_item in menu_path:
                # 尝试多种选择器
                selectors = [
                    f'a:has-text("{menu_item}")',
                    f'span:has-text("{menu_item}")',
                    f'div:has-text("{menu_item}")'
                ]
                
                clicked = False
                for selector in selectors:
                    try:
                        element = left_frame.query_selector(selector)
                        if element and element.is_visible():
                            element.click()
                            time.sleep(1)
                            clicked = True
                            break
                    except:
                        continue
                
                if not clicked:
                    logger.error(f"未找到菜单项: {menu_item}")
                    return False
            
            logger.info("菜单导航成功")
            return True
            
        except Exception as e:
            logger.error(f"菜单导航失败: {e}")
            return False
    
    def get_work_list(self, list_type='pending'):
        """
        获取待办/已办列表
        
        Args:
            list_type: 'pending' (待办) 或 'done' (已办)
        """
        try:
            logger.info(f"获取{list_type}列表")
            
            # 导航到相应页面
            if list_type == 'pending':
                menu_path = ['待办事宜']
            else:
                menu_path = ['已办事宜']
            
            if not self.navigate_menu(menu_path):
                return None
            
            # 等待main frame加载
            time.sleep(2)
            main_frame = self.page.frame('main')
            if not main_frame:
                logger.error("未找到main frame")
                return None
            
            # 查找列表表格
            table_selectors = [
                'table.listTable',
                'table[id*="list"]',
                'table.dataTable',
                'table'
            ]
            
            for selector in table_selectors:
                try:
                    if main_frame.query_selector(selector):
                        # 提取表格数据
                        table_data = main_frame.evaluate(f'''
                            () => {{
                                const table = document.querySelector('{selector}');
                                if (!table) return null;
                                const rows = Array.from(table.querySelectorAll('tr'));
                                return rows.map(row => {{
                                    const cells = Array.from(row.querySelectorAll('td, th'));
                                    return cells.map(cell => cell.innerText.trim());
                                }});
                            }}
                        ''')
                        
                        if table_data:
                            logger.info(f"成功获取列表，共{len(table_data)}行")
                            return table_data
                except:
                    continue
            
            logger.error("未找到列表表格")
            return None
            
        except Exception as e:
            logger.error(f"获取列表失败: {e}")
            return None
    
    def search_documents(self, keyword, date_from=None, date_to=None):
        """
        搜索文档
        
        Args:
            keyword: 搜索关键词
            date_from: 开始日期 (格式: YYYY-MM-DD)
            date_to: 结束日期 (格式: YYYY-MM-DD)
        """
        try:
            logger.info(f"搜索文档: {keyword}")
            
            # 导航到搜索页面
            # 这里需要根据实际系统调整
            
            # 填写搜索条件
            # ...
            
            # 点击搜索
            # ...
            
            # 获取搜索结果
            # ...
            
            logger.info("搜索完成")
            return None
            
        except Exception as e:
            logger.error(f"搜索失败: {e}")
            return None


def main():
    """示例用法"""
    helper = SeeyonHelper()
    
    try:
        helper.start(headless=False)
        
        if not helper.login():
            print("登录失败")
            return
        
        print("登录成功，等待3秒...")
        time.sleep(3)
        
        # 示例：获取待办列表
        pending_list = helper.get_work_list('pending')
        if pending_list:
            print(f"\n待办事项 ({len(pending_list)}条):")
            for i, item in enumerate(pending_list[:5], 1):  # 只显示前5条
                print(f"{i}. {item}")
            
            # 保存数据
            helper.save_to_csv(pending_list, 'pending_list.csv')
            print("\n数据已保存到 output/pending_list.csv")
        
    finally:
        input("\n按Enter键退出...")
        helper.close()


if __name__ == '__main__':
    main()

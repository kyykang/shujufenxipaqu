"""
致远OA数据抓取工具
使用Playwright进行Web自动化
"""
import os
import time
import logging
import json
import csv
from datetime import datetime
from pathlib import Path
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
from dotenv import load_dotenv

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('oa_scraper.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class OAScraper:
    """致远OA数据抓取器"""
    
    def __init__(self):
        """初始化配置"""
        load_dotenv()
        
        # 从环境变量读取配置
        self.oa_url = os.getenv('OA_URL')
        self.username = os.getenv('OA_USERNAME')
        self.password = os.getenv('OA_PASSWORD')
        self.request_delay = float(os.getenv('REQUEST_DELAY', '2.0'))
        
        # 验证必需配置
        if not all([self.oa_url, self.username, self.password]):
            raise ValueError("缺少必需的环境变量配置，请检查 .env 文件")
        
        self.browser = None
        self.context = None
        self.page = None
        
        logger.info("OA抓取器初始化完成")
    
    def start(self, headless=True):
        """启动浏览器"""
        try:
            playwright = sync_playwright().start()
            self.browser = playwright.chromium.launch(headless=headless)
            self.context = self.browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            )
            self.page = self.context.new_page()
            logger.info("浏览器启动成功")
        except Exception as e:
            logger.error(f"浏览器启动失败: {e}")
            raise
    
    def login(self):
        """登录致远Seeyon OA系统"""
        try:
            logger.info(f"正在访问登录页面: {self.oa_url}")
            self.page.goto(self.oa_url, timeout=30000)
            
            # 等待登录表单加载
            self.page.wait_for_load_state('networkidle')
            time.sleep(2)
            
            # 致远Seeyon系统常见的登录表单选择器
            # 尝试多种可能的选择器
            username_selectors = [
                'input[name="loginName"]',
                'input[id="loginName"]',
                'input[name="userName"]',
                'input#userName',
                'input[type="text"]'
            ]
            
            password_selectors = [
                'input[name="password"]',
                'input[id="password"]',
                'input[type="password"]'
            ]
            
            login_button_selectors = [
                'input[type="submit"]',
                'button[type="submit"]',
                'a.login_btn',
                'input.login_btn',
                'button.login_btn',
                '#loginBtn',
                '#login_btn',
                'input[value*="登录"]',
                'button:has-text("登录")',
                'a:has-text("登录")',
                'input[id*="login"]',
                'button[id*="login"]',
                'input[class*="login"]',
                'button[class*="login"]'
            ]
            
            # 填写用户名
            logger.info("正在填写登录信息")
            username_filled = False
            for selector in username_selectors:
                try:
                    if self.page.query_selector(selector):
                        self.page.fill(selector, self.username)
                        logger.info(f"用户名输入框选择器: {selector}")
                        username_filled = True
                        break
                except:
                    continue
            
            if not username_filled:
                logger.error("未找到用户名输入框")
                self.screenshot('login_error_username.png')
                return False
            
            time.sleep(0.5)
            
            # 填写密码
            password_filled = False
            for selector in password_selectors:
                try:
                    if self.page.query_selector(selector):
                        self.page.fill(selector, self.password)
                        logger.info(f"密码输入框选择器: {selector}")
                        password_filled = True
                        break
                except:
                    continue
            
            if not password_filled:
                logger.error("未找到密码输入框")
                self.screenshot('login_error_password.png')
                return False
            
            time.sleep(0.5)
            
            # 截图登录前状态
            self.screenshot('before_login.png')
            
            # 点击登录按钮 - 使用JavaScript直接调用onclick函数
            logger.info("点击登录按钮...")
            login_clicked = False
            
            try:
                # 方法1: 直接调用loginButtonOnClickHandler函数
                logger.info("尝试调用loginButtonOnClickHandler()...")
                self.page.evaluate('loginButtonOnClickHandler()')
                login_clicked = True
                logger.info("成功调用登录函数")
            except Exception as e:
                logger.debug(f"调用loginButtonOnClickHandler失败: {e}")
                
                # 方法2: 点击#login_button
                try:
                    logger.info("尝试点击#login_button...")
                    self.page.click('#login_button')
                    login_clicked = True
                    logger.info("成功点击登录按钮")
                except Exception as e2:
                    logger.debug(f"点击#login_button失败: {e2}")
                    
                    # 方法3: 使用JavaScript点击
                    try:
                        logger.info("尝试使用JavaScript点击...")
                        self.page.evaluate('document.getElementById("login_button").click()')
                        login_clicked = True
                        logger.info("JavaScript点击成功")
                    except Exception as e3:
                        logger.error(f"所有登录方法都失败了: {e3}")
            
            if not login_clicked:
                logger.error("未能点击登录按钮")
                self.screenshot('login_error_button.png')
                with open('login_page.html', 'w', encoding='utf-8') as f:
                    f.write(self.page.content())
                logger.info("登录页面HTML已保存到 login_page.html")
                return False
            
            # 等待登录完成和页面跳转
            logger.info("等待登录完成...")
            time.sleep(5)  # 增加等待时间
            
            # 等待页面跳转或新窗口打开
            try:
                # 等待URL变化或新窗口
                for i in range(10):  # 最多等待10秒
                    time.sleep(1)
                    current_url = self.page.url
                    pages = self.context.pages
                    
                    # 检查是否有新窗口打开
                    if len(pages) > 1:
                        logger.info(f"检测到新窗口打开，共{len(pages)}个窗口")
                        # 切换到新窗口
                        self.page = pages[-1]
                        self.page.bring_to_front()
                        time.sleep(2)
                        break
                    
                    # 检查URL是否变化
                    if 'login' not in current_url.lower() or 'main' in current_url.lower():
                        logger.info(f"页面已跳转: {current_url}")
                        break
                        
            except Exception as e:
                logger.debug(f"等待跳转时出错: {e}")
            
            time.sleep(2)
            self.page.wait_for_load_state('networkidle', timeout=15000)
            
            # 截图登录后状态
            self.screenshot('after_login.png')
            
            # 验证登录是否成功
            if self._check_login_success():
                logger.info("登录成功")
                return True
            else:
                logger.error("登录失败，请检查用户名密码")
                self.screenshot('login_failed.png')
                return False
                
        except PlaywrightTimeout:
            logger.error("登录超时")
            self.screenshot('login_timeout.png')
            return False
        except Exception as e:
            logger.error(f"登录过程出错: {e}")
            self.screenshot('login_exception.png')
            return False
    
    def _check_login_success(self):
        """检查登录是否成功"""
        try:
            current_url = self.page.url
            logger.info(f"当前URL: {current_url}")
            
            # 方法1: 检查URL是否包含main或home
            if 'main' in current_url.lower() or 'home' in current_url.lower():
                # 进一步检查是否有登录错误提示
                error_selectors = [
                    '.error-message',
                    '.login-error',
                    '#errorMsg',
                    'div:has-text("用户名或密码错误")',
                    'div:has-text("登录失败")'
                ]
                
                for selector in error_selectors:
                    try:
                        error_elem = self.page.query_selector(selector)
                        if error_elem and error_elem.is_visible():
                            logger.error(f"发现错误提示: {error_elem.inner_text()}")
                            return False
                    except:
                        continue
                
                return True
            
            # 方法2: 检查是否存在登录后才有的元素
            success_indicators = [
                'frame[name="top"]',  # Seeyon系统常用frame
                'frame[name="left"]',
                'frame[name="main"]',
                '.user-info',
                '#userInfo',
                'a:has-text("退出")',
                'a:has-text("注销")'
            ]
            
            for selector in success_indicators:
                try:
                    element = self.page.query_selector(selector)
                    if element:
                        logger.info(f"找到登录成功标识: {selector}")
                        return True
                except:
                    continue
            
            # 方法3: 检查页面标题
            title = self.page.title()
            logger.info(f"页面标题: {title}")
            if '登录' not in title and title:
                return True
            
            return False
        except Exception as e:
            logger.error(f"检查登录状态失败: {e}")
            return False
    
    def fetch_data(self, data_url, selector=None):
        """
        抓取指定页面的数据
        
        Args:
            data_url: 数据页面URL
            selector: CSS选择器，用于定位数据元素
        
        Returns:
            抓取到的数据
        """
        try:
            logger.info(f"正在访问数据页面: {data_url}")
            
            # 请求延迟，避免频繁访问
            time.sleep(self.request_delay)
            
            self.page.goto(data_url, timeout=30000)
            self.page.wait_for_load_state('networkidle')
            
            if selector:
                # 等待数据元素加载
                self.page.wait_for_selector(selector, timeout=10000)
                data = self.page.inner_text(selector)
            else:
                # 获取整个页面内容
                data = self.page.content()
            
            logger.info("数据抓取成功")
            return data
            
        except PlaywrightTimeout:
            logger.error(f"访问页面超时: {data_url}")
            return None
        except Exception as e:
            logger.error(f"抓取数据失败: {e}")
            return None
    
    def fetch_table_data(self, table_url, table_selector='table'):
        """
        抓取表格数据
        
        Args:
            table_url: 表格页面URL
            table_selector: 表格的CSS选择器
        
        Returns:
            表格数据列表
        """
        try:
            logger.info(f"正在抓取表格数据: {table_url}")
            time.sleep(self.request_delay)
            
            self.page.goto(table_url, timeout=30000)
            self.page.wait_for_selector(table_selector, timeout=10000)
            
            # 提取表格数据
            table_data = self.page.evaluate(f'''
                () => {{
                    const table = document.querySelector('{table_selector}');
                    const rows = Array.from(table.querySelectorAll('tr'));
                    return rows.map(row => {{
                        const cells = Array.from(row.querySelectorAll('td, th'));
                        return cells.map(cell => cell.innerText.trim());
                    }});
                }}
            ''')
            
            logger.info(f"成功抓取 {len(table_data)} 行数据")
            return table_data
            
        except Exception as e:
            logger.error(f"抓取表格数据失败: {e}")
            return None
    
    def screenshot(self, filename=None):
        """截图保存"""
        if not filename:
            filename = f"screenshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        
        screenshot_dir = Path('screenshots')
        screenshot_dir.mkdir(exist_ok=True)
        filepath = screenshot_dir / filename
        
        self.page.screenshot(path=str(filepath))
        logger.info(f"截图已保存: {filepath}")
        return str(filepath)
    
    def save_to_json(self, data, filename=None):
        """保存数据为JSON格式"""
        if not filename:
            filename = f"data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        output_dir = Path('output')
        output_dir.mkdir(exist_ok=True)
        filepath = output_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"数据已保存为JSON: {filepath}")
        return str(filepath)
    
    def save_to_csv(self, data, filename=None, headers=None):
        """
        保存数据为CSV格式
        
        Args:
            data: 二维列表数据
            filename: 文件名
            headers: 表头列表（可选）
        """
        if not filename:
            filename = f"data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        output_dir = Path('output')
        output_dir.mkdir(exist_ok=True)
        filepath = output_dir / filename
        
        with open(filepath, 'w', encoding='utf-8-sig', newline='') as f:
            writer = csv.writer(f)
            if headers:
                writer.writerow(headers)
            writer.writerows(data)
        
        logger.info(f"数据已保存为CSV: {filepath}")
        return str(filepath)
    
    def wait_and_click(self, selector, timeout=10000):
        """等待元素并点击"""
        try:
            self.page.wait_for_selector(selector, timeout=timeout)
            self.page.click(selector)
            time.sleep(0.5)
            return True
        except Exception as e:
            logger.error(f"点击元素失败 {selector}: {e}")
            return False
    
    def get_element_text(self, selector, timeout=5000):
        """获取元素文本"""
        try:
            self.page.wait_for_selector(selector, timeout=timeout)
            return self.page.inner_text(selector)
        except Exception as e:
            logger.error(f"获取元素文本失败 {selector}: {e}")
            return None
    
    def get_all_elements_text(self, selector):
        """获取所有匹配元素的文本"""
        try:
            elements = self.page.query_selector_all(selector)
            return [elem.inner_text() for elem in elements]
        except Exception as e:
            logger.error(f"获取元素列表失败 {selector}: {e}")
            return []
    
    def close(self):
        """关闭浏览器"""
        try:
            if self.context:
                self.context.close()
            if self.browser:
                self.browser.close()
            logger.info("浏览器已关闭")
        except Exception as e:
            logger.error(f"关闭浏览器时出错: {e}")


def main():
    """主函数示例"""
    scraper = OAScraper()
    
    try:
        # 启动浏览器
        scraper.start(headless=False)  # 调试时设置为False可以看到浏览器
        
        # 登录
        if not scraper.login():
            logger.error("登录失败，程序退出")
            return
        
        # 抓取数据示例
        # 方式1: 抓取特定元素的文本
        data = scraper.fetch_data(
            data_url=f"{scraper.oa_url}/data-page",
            selector='.data-container'
        )
        if data:
            print(f"抓取到的数据:\n{data}")
        
        # 方式2: 抓取表格数据
        table_data = scraper.fetch_table_data(
            table_url=f"{scraper.oa_url}/table-page",
            table_selector='table.data-table'
        )
        if table_data:
            print(f"表格数据: {table_data}")
        
    except Exception as e:
        logger.error(f"程序执行出错: {e}")
    finally:
        scraper.close()


if __name__ == '__main__':
    main()

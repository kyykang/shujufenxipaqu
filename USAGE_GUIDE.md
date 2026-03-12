# 使用指南

## 快速开始

### 第一步：找到页面选择器

运行选择器查找工具，它会帮你自动识别登录页面的元素：

```bash
python selector_finder.py
```

这个工具会：
- 自动打开OA登录页面
- 尝试识别用户名、密码输入框和登录按钮
- 将找到的选择器保存到 `selectors.txt`

如果自动识别失败，你可以：
1. 在打开的浏览器中右键点击元素
2. 选择"检查"
3. 在开发者工具中右键该元素
4. 选择 Copy -> Copy selector

### 第二步：更新代码中的选择器

根据 `selectors.txt` 中的内容，修改 `oa_scraper.py` 中的 `login()` 方法：

```python
# 示例：如果你的选择器是
self.page.fill('input#loginName', self.username)  # 用户名
self.page.fill('input#loginPwd', self.password)   # 密码
self.page.click('button#loginBtn')                # 登录按钮
```

### 第三步：运行基本示例

```bash
python examples/basic_usage.py
```

## 常用场景

### 场景1：抓取单个表格

```python
from oa_scraper import OAScraper

scraper = OAScraper()
scraper.start(headless=True)
scraper.login()

# 抓取表格
data = scraper.fetch_table_data(
    table_url="http://oa/approval-list",
    table_selector="table.approval-table"
)

# 保存为CSV
scraper.save_to_csv(data, "approvals.csv")
scraper.close()
```

### 场景2：定时自动抓取

编辑 `scheduler.py` 中的 `scheduled_task()` 函数，然后运行：

```bash
python scheduler.py
```

选择执行频率：
- 每天固定时间（如每天早上9点）
- 每隔N小时
- 每隔N分钟

### 场景3：抓取多页数据

参考 `examples/advanced_usage.py` 中的 `example_with_pagination()` 函数。

### 场景4：使用筛选条件

参考 `examples/advanced_usage.py` 中的 `example_with_filters()` 函数。

## 调试技巧

### 1. 查看浏览器操作过程

```python
scraper.start(headless=False)  # 显示浏览器窗口
```

### 2. 在关键步骤截图

```python
scraper.screenshot('step1.png')
# ... 执行操作 ...
scraper.screenshot('step2.png')
```

### 3. 查看页面HTML

```python
html = scraper.page.content()
with open('page.html', 'w', encoding='utf-8') as f:
    f.write(html)
```

### 4. 测试选择器

```python
# 测试元素是否存在
element = scraper.page.query_selector('your-selector')
if element:
    print("找到元素")
    print(element.inner_text())
else:
    print("未找到元素")
```

## 常见问题解决

### 问题1：登录后立即跳转回登录页

可能原因：
- Cookie未正确保存
- 需要处理验证码
- 登录按钮点击后需要等待

解决方法：
```python
# 在login()方法中增加等待时间
self.page.click('button[type="submit"]')
time.sleep(3)  # 增加等待时间
self.page.wait_for_load_state('networkidle')
```

### 问题2：找不到元素

可能原因：
- 页面还在加载
- 选择器不正确
- 元素在iframe中

解决方法：
```python
# 增加等待时间
scraper.page.wait_for_selector('your-selector', timeout=15000)

# 或者等待页面完全加载
scraper.page.wait_for_load_state('networkidle')

# 如果元素在iframe中
frame = scraper.page.frame_locator('iframe[name="mainFrame"]')
frame.locator('your-selector').click()
```

### 问题3：数据抓取不完整

可能原因：
- 数据是动态加载的
- 需要滚动页面才能加载

解决方法：
```python
# 滚动到页面底部
scraper.page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
time.sleep(2)

# 或者多次滚动
for i in range(5):
    scraper.page.evaluate(f'window.scrollTo(0, {(i+1)*1000})')
    time.sleep(1)
```

### 问题4：会话过期

解决方法：
```python
# 在抓取前检查登录状态
if not scraper._check_login_success():
    scraper.login()
```

## 性能优化

### 1. 使用无头模式

```python
scraper.start(headless=True)  # 不显示浏览器，速度更快
```

### 2. 禁用图片加载

```python
context = browser.new_context(
    viewport={'width': 1920, 'height': 1080},
    # 禁用图片
    bypass_csp=True,
    java_script_enabled=True
)
```

### 3. 复用浏览器会话

```python
# 不要每次都关闭浏览器
scraper.start()
scraper.login()

# 抓取多个页面
for url in urls:
    data = scraper.fetch_data(url)
    # 处理数据

# 最后才关闭
scraper.close()
```

## 数据导出格式

### CSV格式（推荐用于Excel）

```python
scraper.save_to_csv(data, 'output.csv')
```

### JSON格式（推荐用于程序处理）

```python
scraper.save_to_json(data, 'output.json')
```

### Excel格式（需要额外处理）

```python
import pandas as pd

# 将数据转换为DataFrame
df = pd.DataFrame(data[1:], columns=data[0])
df.to_excel('output.xlsx', index=False)
```

## 安全提醒

- ✅ 定期更改OA密码
- ✅ 不要在公共电脑上运行
- ✅ 不要分享 `.env` 文件
- ✅ 定期检查日志文件
- ✅ 抓取的数据要妥善保管

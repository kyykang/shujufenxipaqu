# 快速开始指南

## 针对致远Seeyon系统的配置

你的OA系统地址：`https://sales.antiy.cn/seeyon/main.do?method=index`

### 第一步：安装环境

```bash
# 安装Python依赖
pip install -r requirements.txt

# 安装Playwright浏览器
playwright install chromium
```

### 第二步：配置登录信息

1. 复制配置文件模板：
```bash
cp .env.example .env
```

2. 编辑 `.env` 文件，填入你的账号信息：
```env
OA_URL=https://sales.antiy.cn/seeyon/main.do?method=index
OA_USERNAME=你的用户名
OA_PASSWORD=你的密码
REQUEST_DELAY=2.0
```

### 第三步：测试登录

运行登录测试脚本：

```bash
python test_login.py
```

这个脚本会：
- 打开浏览器窗口（你可以看到整个过程）
- 尝试自动登录
- 显示登录结果和页面信息
- 自动截图保存到 `screenshots/` 目录

如果登录成功，你会看到：
```
✓ 登录成功！
当前页面: https://sales.antiy.cn/seeyon/...
页面标题: ...
```

如果登录失败，请检查：
1. 用户名密码是否正确
2. 查看 `screenshots/` 目录中的截图
3. 查看 `oa_scraper.log` 日志文件

### 第四步：开始抓取数据

#### 方式1：使用Seeyon专用辅助工具

```bash
python seeyon_helper.py
```

这个工具提供了Seeyon系统的专用功能：
- 自动处理frame结构
- 获取待办/已办列表
- 菜单导航
- 文档搜索

#### 方式2：使用基础抓取工具

```bash
python examples/basic_usage.py
```

#### 方式3：自定义抓取逻辑

```python
from oa_scraper import OAScraper

scraper = OAScraper()
scraper.start(headless=True)
scraper.login()

# 你的抓取逻辑
data = scraper.fetch_data(
    data_url="https://sales.antiy.cn/seeyon/你的页面路径",
    selector="你的选择器"
)

scraper.save_to_csv(data, "output.csv")
scraper.close()
```

## 常见场景

### 场景1：获取待办事项

```python
from seeyon_helper import SeeyonHelper

helper = SeeyonHelper()
helper.start(headless=True)
helper.login()

# 获取待办列表
pending = helper.get_work_list('pending')
helper.save_to_csv(pending, 'pending.csv')

helper.close()
```

### 场景2：定时自动抓取

```bash
python scheduler.py
```

选择执行频率，比如每天早上9点自动抓取。

### 场景3：抓取特定页面的表格

```python
from oa_scraper import OAScraper

scraper = OAScraper()
scraper.start(headless=True)
scraper.login()

# 抓取表格数据
table_data = scraper.fetch_table_data(
    table_url="https://sales.antiy.cn/seeyon/具体页面",
    table_selector="table"
)

scraper.save_to_csv(table_data, "table.csv")
scraper.close()
```

## 调试技巧

### 1. 查看浏览器操作

```python
scraper.start(headless=False)  # 显示浏览器窗口
```

### 2. 查看截图

所有截图保存在 `screenshots/` 目录：
- `before_login.png` - 登录前
- `after_login.png` - 登录后
- `login_failed.png` - 登录失败时
- 其他自定义截图

### 3. 查看日志

```bash
tail -f oa_scraper.log
```

### 4. 处理Frame结构

Seeyon系统通常使用frame，如果找不到元素，可能需要切换frame：

```python
from seeyon_helper import SeeyonHelper

helper = SeeyonHelper()
helper.start(headless=False)
helper.login()

# 切换到main frame
main_frame = helper.switch_to_frame('main')

# 在frame中查找元素
if main_frame:
    data = main_frame.inner_text('.content')
```

## 下一步

1. 告诉我你需要抓取什么数据（待办事项、审批记录、报表等）
2. 我可以帮你编写具体的抓取代码
3. 如果遇到问题，提供截图和日志，我来帮你解决

## 注意事项

- ✅ 首次使用建议用 `headless=False` 观察过程
- ✅ 登录成功后会自动截图
- ✅ 所有数据保存在 `output/` 目录
- ✅ 日志记录在 `oa_scraper.log`
- ⚠️ 不要频繁访问，建议设置2秒以上延迟
- ⚠️ 妥善保管 `.env` 文件，不要分享

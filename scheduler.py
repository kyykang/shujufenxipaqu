"""
定时任务调度器
使用schedule库实现定时抓取
"""
import schedule
import time
from datetime import datetime
from oa_scraper import OAScraper
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def scheduled_task():
    """定时执行的任务"""
    logger.info("开始执行定时任务")
    
    scraper = OAScraper()
    
    try:
        scraper.start(headless=True)
        
        if not scraper.login():
            logger.error("登录失败，任务终止")
            return
        
        # 执行数据抓取
        table_data = scraper.fetch_table_data(
            table_url=f"{scraper.oa_url}/data-page",
            table_selector='table'
        )
        
        if table_data:
            # 使用时间戳命名文件
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            scraper.save_to_csv(table_data, f'scheduled_data_{timestamp}.csv')
            logger.info(f"任务完成，抓取 {len(table_data)} 行数据")
        else:
            logger.warning("未抓取到数据")
            
    except Exception as e:
        logger.error(f"任务执行失败: {e}")
    finally:
        scraper.close()


def main():
    """主函数"""
    print("=== OA数据定时抓取器 ===")
    print("\n可用的调度选项:")
    print("1. 每天指定时间执行")
    print("2. 每隔N小时执行")
    print("3. 每隔N分钟执行")
    print("4. 立即执行一次")
    
    choice = input("\n请选择 (1-4): ")
    
    if choice == '1':
        time_str = input("请输入执行时间 (格式: HH:MM，如 09:00): ")
        schedule.every().day.at(time_str).do(scheduled_task)
        print(f"已设置每天 {time_str} 执行任务")
        
    elif choice == '2':
        hours = int(input("请输入小时间隔: "))
        schedule.every(hours).hours.do(scheduled_task)
        print(f"已设置每 {hours} 小时执行任务")
        
    elif choice == '3':
        minutes = int(input("请输入分钟间隔: "))
        schedule.every(minutes).minutes.do(scheduled_task)
        print(f"已设置每 {minutes} 分钟执行任务")
        
    elif choice == '4':
        print("立即执行任务...")
        scheduled_task()
        return
    else:
        print("无效选项")
        return
    
    print("\n调度器已启动，按 Ctrl+C 停止")
    print(f"下次执行时间: {schedule.next_run()}")
    
    try:
        while True:
            schedule.run_pending()
            time.sleep(60)  # 每分钟检查一次
    except KeyboardInterrupt:
        print("\n调度器已停止")


if __name__ == '__main__':
    main()

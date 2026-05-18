import subprocess
import logging
from datetime import datetime
from apscheduler.schedulers.blocking import BlockingScheduler

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("logs/scheduler.log"),
        logging.StreamHandler()
    ]
)
log = logging.getLogger(__name__)

SCRAPY_PROJECT_DIR = "jobtracker"   # folder containing scrapy.cfg


def run_spider(spider_name: str):
    log.info(f"Starting spider: {spider_name}")
    result = subprocess.run(
        ["scrapy", "crawl", spider_name],
        cwd=SCRAPY_PROJECT_DIR,
        capture_output=True,
        text=True
    )
    if result.returncode == 0:
        log.info(f"Spider {spider_name} finished successfully")
    else:
        log.error(f"Spider {spider_name} failed:\n{result.stderr}")


def run_all_spiders():
    log.info("=" * 50)
    log.info(f"Daily run started at {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    run_spider("rekrute")
    run_spider("emploima")
    log.info("Daily run complete")
    log.info("=" * 50)


if __name__ == "__main__":
    # Create logs folder if it doesn't exist
    import os
    os.makedirs("logs", exist_ok=True)

    scheduler = BlockingScheduler()

    # Run every day at 08:00 AM
    scheduler.add_job(
        run_all_spiders,
        trigger="cron",
        hour=8,
        minute=0,
        id="daily_scrape",
        name="Daily Moroccan Job Scrape"
    )

    log.info("Scheduler started — spiders will run daily at 08:00 AM")
    log.info("Press Ctrl+C to stop")

    # Run immediately on first launch so you don't wait until tomorrow
    run_all_spiders()

    try:
        scheduler.start()
    except KeyboardInterrupt:
        log.info("Scheduler stopped")
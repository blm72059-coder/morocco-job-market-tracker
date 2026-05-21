import os
from dotenv import load_dotenv
load_dotenv()

BOT_NAME = "jobtracker"
SPIDER_MODULES = ["jobtracker.spiders"]
NEWSPIDER_MODULE = "jobtracker.spiders"

# Sources: rekrute.com, emploi.ma
DOWNLOAD_DELAY = 10
RANDOMIZE_DOWNLOAD_DELAY = True
CONCURRENT_REQUESTS = 1
AUTOTHROTTLE_ENABLED = True
ROBOTSTXT_OBEY = False

USER_AGENT = os.getenv("SCRAPER_USER_AGENT")

FEEDS = {
    "data/raw/%(name)s_%(time)s.json": {   # one file per spider
        "format": "json",
        "encoding": "utf8",
        "indent": 2,
    }
}

DUPEFILTER_CLASS = "scrapy.dupefilters.BaseDupeFilter"
LOG_LEVEL = "INFO"
ITEM_PIPELINES = {
    "jobtracker.pipelines.DeduplicationPipeline": 100,  # runs first
    "jobtracker.pipelines.PostgreSQLPipeline":    200,  # runs second
    "jobtracker.pipelines.NLPPipeline":           300,
}
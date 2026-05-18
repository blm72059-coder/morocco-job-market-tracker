import scrapy

class JobItem(scrapy.Item):
    # Core fields
    job_title     = scrapy.Field()
    company       = scrapy.Field()
    location      = scrapy.Field()
    salary        = scrapy.Field()
    job_type      = scrapy.Field()      # Full-time, Part-time, Contract
    remote        = scrapy.Field()      # True / False / Hybrid
    seniority     = scrapy.Field()      # Junior, Mid, Senior, Lead
    description   = scrapy.Field()     # Full job description text
    skills_raw    = scrapy.Field()      # We'll extract skills in Week 4

    # Metadata
    job_url       = scrapy.Field()
    source        = scrapy.Field()      # "indeed", "linkedin", etc.
    date_posted   = scrapy.Field()
    date_scraped  = scrapy.Field()
    job_id        = scrapy.Field()      # Hash for deduplication
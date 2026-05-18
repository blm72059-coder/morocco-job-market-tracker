import os
import psycopg2
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()


class DeduplicationPipeline:
    """Drop items we have already stored — based on job_id hash."""

    def __init__(self):
        self.seen_ids = set()

    def open_spider(self, spider):
        # Pre-load existing job_ids from DB so we skip duplicates
        conn = self._get_conn()
        cur = conn.cursor()
        cur.execute("SELECT job_id FROM jobs;")
        rows = cur.fetchall()
        self.seen_ids = {row[0] for row in rows}
        spider.logger.info(f"[Dedup] Loaded {len(self.seen_ids)} existing job IDs")
        cur.close()
        conn.close()

    def process_item(self, item, spider):
        if item["job_id"] in self.seen_ids:
            spider.logger.debug(f"[Dedup] Skipping duplicate: {item['job_title']}")
            from scrapy.exceptions import DropItem
            raise DropItem(f"Duplicate job_id: {item['job_id']}")
        self.seen_ids.add(item["job_id"])
        return item

    @staticmethod
    def _get_conn():
        return psycopg2.connect(
            host=os.getenv("DB_HOST", "localhost"),
            port=os.getenv("DB_PORT", "5432"),
            dbname=os.getenv("DB_NAME", "morocco_jobs"),
            user=os.getenv("DB_USER", "postgres"),
            password=os.getenv("DB_PASSWORD"),
        )


class PostgreSQLPipeline:
    """Insert every item into the jobs table."""

    def __init__(self):
        self.conn = None
        self.cur  = None
        self.inserted = 0

    def open_spider(self, spider):
        self.conn = psycopg2.connect(
            host=os.getenv("DB_HOST", "localhost"),
            port=os.getenv("DB_PORT", "5432"),
            dbname=os.getenv("DB_NAME", "morocco_jobs"),
            user=os.getenv("DB_USER", "postgres"),
            password=os.getenv("DB_PASSWORD"),
        )
        self.cur = self.conn.cursor()
        spider.logger.info("[DB] Connected to PostgreSQL")

    def process_item(self, item, spider):
        try:
            self.cur.execute("""
                INSERT INTO jobs (
                    job_id, job_title, company, location,
                    salary, job_type, remote, seniority,
                    description, skills_raw, job_url,
                    source, date_posted, date_scraped
                ) VALUES (
                    %s, %s, %s, %s,
                    %s, %s, %s, %s,
                    %s, %s, %s,
                    %s, %s, %s
                )
                ON CONFLICT (job_id) DO NOTHING;
            """, (
                item.get("job_id"),
                item.get("job_title"),
                item.get("company"),
                item.get("location"),
                item.get("salary"),
                item.get("job_type"),
                item.get("remote"),
                item.get("seniority"),
                item.get("description"),
                item.get("skills_raw"),
                item.get("job_url"),
                item.get("source"),
                item.get("date_posted"),
                item.get("date_scraped"),
            ))
            self.conn.commit()
            self.inserted += 1
        except Exception as e:
            self.conn.rollback()
            spider.logger.error(f"[DB] Insert error: {e}")
        return item

    def close_spider(self, spider):
        self.cur.close()
        self.conn.close()
        spider.logger.info(f"[DB] Closed connection — {self.inserted} new jobs inserted")
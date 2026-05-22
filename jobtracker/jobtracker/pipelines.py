import os
import psycopg2
from dotenv import load_dotenv
from datetime import datetime
import spacy
from jobtracker.skills_list import SKILLS

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
            port=os.getenv("DB_PORT", "5433"),
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

# Load French spaCy model once (not per item — that would be slow)
nlp = spacy.load("fr_core_news_sm")

# Lowercase skills list for case-insensitive matching
SKILLS_LOWER = {skill.lower(): skill for skill in SKILLS}


class NLPPipeline:

    def open_spider(self, spider):
        try:
            self.conn = psycopg2.connect(
                host=os.getenv("DB_HOST", "localhost"),
                port=os.getenv("DB_PORT", "5433"),  
                dbname=os.getenv("DB_NAME", "morocco_jobs"),
                user=os.getenv("DB_USER", "postgres"),
                password=os.getenv("DB_PASSWORD"),
            )
            self.cur = self.conn.cursor()
            spider.logger.info("[NLP] Connected to PostgreSQL")
        except Exception as e:
            spider.logger.error(f"[NLP] Connection failed: {e}")
            self.conn = None
            self.cur = None

    def process_item(self, item, spider):
        description = item.get("description", "")
        job_url     = item.get("job_url", "")

        if not description:
            return item

        # Find the job's id in the database using its URL
        self.cur.execute("SELECT id FROM jobs WHERE job_url = %s", (job_url,))
        row = self.cur.fetchone()

        if not row:
            return item  # job not found, skip

        job_id = row[0]

        # Tokenize with spaCy
        doc = nlp(description.lower())

        # Check which skills appear in the description
        found_skills = set()
        text_lower = description.lower()

        for skill_lower, skill_original in SKILLS_LOWER.items():
            if skill_lower in text_lower:
                found_skills.add(skill_original)

        # Insert each found skill into job_skills table
        for skill in found_skills:
            try:
                self.cur.execute("""
                    INSERT INTO job_skills (job_id, skill, date_scraped)
                    VALUES (%s, %s, %s)
                    ON CONFLICT DO NOTHING
                """, (job_id, skill, item.get("date_scraped")))
            except Exception as e:
                self.conn.rollback()
                spider.logger.error(f"[NLP] Insert error: {e}")
                continue

        self.conn.commit()
        spider.logger.info(f"[NLP] {len(found_skills)} skills found for job_id {job_id}")
        return item

    def close_spider(self, spider):
        if hasattr(self, 'cur') and self.cur:
            self.cur.close()
        if hasattr(self, 'conn') and self.conn:
            self.conn.close()
        spider.logger.info("[NLP] Pipeline closed")
import scrapy
import hashlib
from datetime import datetime
from jobtracker.items import JobItem


class RekruteSpider(scrapy.Spider):
    name = "rekrute"
    allowed_domains = ["rekrute.com"]

    KEYWORDS  = "data"
    MAX_PAGES = 5

    async def start(self):
        for page in range(1, self.MAX_PAGES + 1):
            url = (
                f"https://www.rekrute.com/offres.html"
                f"?s=3&p={page}&o=1"
                f"&query={self.KEYWORDS}"
                f"&keyword={self.KEYWORDS}"
            )
            yield scrapy.Request(url, callback=self.parse_listing)

    def parse_listing(self, response):
        jobs = response.css("li.post-id")
        self.logger.info(f"Found {len(jobs)} jobs on {response.url}")

        for job in jobs:
            # Job URL
            job_url = job.css("a.titreJob::attr(href)").get()
            if not job_url:
                continue

            # Title — strip the "| City (Country)" suffix
            raw_title = job.css("a.titreJob::text").get(default="").strip()
            job_title = raw_title.split("|")[0].strip()

            # Location — everything after the "|"
            location = ""
            if "|" in raw_title:
                location = raw_title.split("|")[-1].strip()

            # Company — the img alt attribute is the most reliable company name
            company = job.css("img.photo::attr(alt)").get(default="").strip()

            # Date posted — text inside <em class="date"> <span> tags
            date_spans = job.css("em.date span::text").getall()
            date_posted = " ".join(d.strip() for d in date_spans if d.strip())

            # Contract type & remote — inside div.info ul li
            job_type = ""
            remote   = ""
            for li in job.css("div.info ul li"):
                li_text = " ".join(li.css("::text").getall())
                if "contrat" in li_text.lower():
                    job_type = li.css("a::text").get(default="").strip()
                    # Remote is plain text in same li: "CDI - Télétravail : Oui 100%"
                    for chunk in li.css("::text").getall():
                        if "Télétravail" in chunk:
                            remote = chunk.split(":")[-1].strip()

            # Seniority — from experience level li
            seniority = "Mid"
            for li in job.css("div.info ul li"):
                li_text = " ".join(li.css("::text").getall())
                if "Expérience" in li_text:
                    exp_text = li.css("a::text").get(default="")
                    seniority = self._map_seniority(exp_text)
                    break

            # Description — the AI summary block (aiiconrose line)
            description = job.css(
                "div.info span[style*='line-height: 18px']::text"
            ).get(default="").strip()

            # Fallback to the search snippet if summary is empty
            if not description:
                description = job.css(
                    "div.info span[style*='font-style : italic']::text"
                ).get(default="").strip()

            unique_str = job_title + company + response.urljoin(job_url)
            job_id = hashlib.md5(unique_str.encode()).hexdigest()

            yield JobItem(
                job_title    = job_title,
                company      = company,
                location     = location,
                salary       = "",
                job_type     = job_type,
                remote       = remote,
                seniority    = seniority,
                description  = description,
                skills_raw   = "",
                job_url      = response.urljoin(job_url),
                source       = "rekrute",
                date_posted  = date_posted,
                date_scraped = datetime.utcnow().isoformat(),
                job_id       = job_id,
            )

    @staticmethod
    def _map_seniority(text):
        mapping = {
            "Débutant":      "Intern",
            "Junior":        "Junior",
            "Intermédiaire": "Mid",
            "Confirmé":      "Senior",
            "Expert":        "Expert",
        }
        for key, value in mapping.items():
            if key in text:
                return value
        return "Mid"
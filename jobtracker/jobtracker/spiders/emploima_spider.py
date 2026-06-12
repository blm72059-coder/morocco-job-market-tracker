import scrapy
import hashlib
from datetime import datetime
from jobtracker.items import JobItem


class EmploiMaSpider(scrapy.Spider):
    name = "emploima"
    allowed_domains = ["emploi.ma"]

    KEYWORDS_LIST = [
        "data scientist",
        "data analyst",
        "machine learning",
        "intelligence artificielle",
        "big data",
        "data engineer",
        "python",
        "power bi",
        "business intelligence",
    ]
    MAX_PAGES = 3

    async def start(self):
        for keyword in self.KEYWORDS_LIST:
            for page in range(0, self.MAX_PAGES):
                url = (
                    f"https://www.emploi.ma/recherche-jobs-maroc/"
                    f"?{keyword.replace(' ', '+')}"
                    f"&page={page}"
                )
                yield scrapy.Request(
                    url,
                    callback=self.parse_listing,
                    headers={"Accept-Language": "fr-FR,fr;q=0.9"}
                )

    def parse_listing(self, response):
        jobs = response.css("div.card.card-job")
        self.logger.info(f"Found {len(jobs)} jobs on {response.url}")

        for job in jobs:
            job_url = job.attrib.get("data-href", "")
            if not job_url:
                continue

            job_title   = job.css("div.card-job-detail h3 a::text").get(default="").strip()
            company     = job.css("a.card-job-company::text").get(default="").strip()
            description = job.css("div.card-job-description p::text").get(default="").strip()
            date_posted = job.css("time::text").get(default="").strip()

            list_items  = job.css("ul li strong::text").getall()
            education   = list_items[0].strip() if len(list_items) > 0 else ""
            experience  = list_items[1].strip() if len(list_items) > 1 else ""
            job_type    = list_items[2].strip() if len(list_items) > 2 else ""
            location    = list_items[3].strip() if len(list_items) > 3 else ""
            skills_raw  = list_items[4].strip() if len(list_items) > 4 else ""

            seniority  = self._map_seniority(experience)
            unique_str = job_title + company + job_url
            job_id     = hashlib.md5(unique_str.encode()).hexdigest()

            yield JobItem(
                job_title    = job_title,
                company      = company,
                location     = location,
                salary       = "",
                job_type     = job_type,
                remote       = "",
                seniority    = seniority,
                description  = description,
                skills_raw   = skills_raw,
                job_url      = job_url,
                source       = "emploima",
                date_posted  = date_posted,
                date_scraped = datetime.utcnow().isoformat(),
                job_id       = job_id,
            )

    @staticmethod
    def _map_seniority(text):
        text = text.lower()
        if "débutant" in text:
            return "Junior"
        if "2 ans" in text or "3 ans" in text:
            return "Junior"
        if "5 ans" in text or "6 ans" in text:
            return "Mid"
        if "10 ans" in text or "15 ans" in text:
            return "Senior"
        return "Mid"
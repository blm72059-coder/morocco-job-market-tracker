import scrapy
import hashlib
import os
from datetime import datetime
from dotenv import load_dotenv
from jobtracker.items import JobItem

load_dotenv()


class AdzunaSpider(scrapy.Spider):
    name = "adzuna"

    APP_ID  = os.getenv("ADZUNA_APP_ID")
    APP_KEY = os.getenv("ADZUNA_APP_KEY")

    KEYWORDS  = "data engineer"
    COUNTRY   = "us"        # us, gb, ca, au, de, fr ...
    MAX_PAGES = 10          # 50 results/page → 500 jobs per run

    async def start(self):
        for page in range(1, self.MAX_PAGES + 1):
            url = (
                f"https://api.adzuna.com/v1/api/jobs/{self.COUNTRY}/search/{page}"
                f"?app_id={self.APP_ID}"
                f"&app_key={self.APP_KEY}"
                f"&results_per_page=50"
                f"&what={self.KEYWORDS.replace(' ', '+')}"
                f"&content-type=application/json"
            )
            yield scrapy.Request(url, callback=self.parse)

    def parse(self, response):
        data = response.json()
        jobs = data.get("results", [])

        self.logger.info(f"Page received — {len(jobs)} jobs")

        for job in jobs:
            description = job.get("description", "")
            title       = job.get("title", "")
            location    = job.get("location", {}).get("display_name", "")

            remote = self._detect_field(
                description.lower() + location.lower(), {
                    "Remote":  ["remote", "work from home", "wfh"],
                    "Hybrid":  ["hybrid"],
                    "On-site": ["on-site", "onsite", "in-office"],
                }
            )

            seniority = self._detect_field(
                title.lower() + " " + description.lower(), {
                    "Intern":  ["intern", "internship"],
                    "Junior":  ["junior", "jr.", "entry level", "entry-level", "graduate"],
                    "Senior":  ["senior", "sr.", "lead", "principal", "staff"],
                    "Manager": ["manager", "director", "head of"],
                    "Mid":     [],
                }
            )

            job_type = self._detect_field(description.lower(), {
                "Full-time":  ["full-time", "full time"],
                "Part-time":  ["part-time", "part time"],
                "Contract":   ["contract", "contractor", "freelance"],
                "Internship": ["internship", "intern"],
                "Full-time":  [],   # default
            })

            # Salary — Adzuna gives min/max directly
            sal_min = job.get("salary_min")
            sal_max = job.get("salary_max")
            if sal_min and sal_max:
                salary = f"${int(sal_min):,} - ${int(sal_max):,}"
            elif sal_min:
                salary = f"${int(sal_min):,}+"
            else:
                salary = ""

            unique_str = title + job.get("company", {}).get("display_name", "") + job.get("redirect_url", "")
            job_id = hashlib.md5(unique_str.encode()).hexdigest()

            yield JobItem(
                job_title    = title,
                company      = job.get("company", {}).get("display_name", ""),
                location     = location,
                salary       = salary,
                job_type     = job_type,
                remote       = remote,
                seniority    = seniority,
                description  = description,
                skills_raw   = "",
                job_url      = job.get("redirect_url", ""),
                source       = "adzuna",
                date_posted  = job.get("created", ""),
                date_scraped = datetime.utcnow().isoformat(),
                job_id       = job_id,
            )

    @staticmethod
    def _detect_field(text, mapping):
        for label, keywords in mapping.items():
            if any(kw in text for kw in keywords):
                return label
        return list(mapping.keys())[-1]
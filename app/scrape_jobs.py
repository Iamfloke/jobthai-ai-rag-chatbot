# app/scrape_jobs.py

import asyncio
import math
import json
from playwright.async_api import async_playwright
import re
import textwrap
from datetime import date
from recommender import get_embedding, translate_thai_to_english
from langdetect import detect

KEYWORD = "Data+Engineer"
BASE_URL = f"https://www.jobthai.com/th/jobs?keyword={KEYWORD}"
DOMAIN = "https://www.jobthai.com"
today_str = date.today().isoformat()

def split_description(text, max_len=1000):
    text = text.strip()
    text = re.sub(r'\s+', ' ', text)

    parts = textwrap.wrap(text, width=max_len, break_long_words=False, break_on_hyphens=False)

    while len(parts) < 3:
        parts.append("")

    return parts[:3]

async def scrape_jobthai():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto(BASE_URL, timeout=60000)

        await page.wait_for_selector("#count-position")
        count_text = await page.inner_text("#count-position")
        job_count = int("".join(filter(str.isdigit, count_text)))
        total_pages = math.ceil(job_count / 20)
        
        #for testing
        # total_pages = 2

        print(f"Total jobs: {job_count}, total pages: {total_pages}")

        results = []

        for page_number in range(1, total_pages + 1):
            url = f"{BASE_URL}&page={page_number}"
            await page.goto(url)
            await page.wait_for_selector("a.msklqa-12.edfvgA")

            job_cards = await page.query_selector_all("a.msklqa-12.edfvgA")

            for card in job_cards:
                url_suffix = await card.get_attribute("href")
                url = DOMAIN + url_suffix if url_suffix else ""

                title_el = await card.query_selector("h2.ohgq7e-0.hHthyd")
                title = await title_el.inner_text() if title_el else ""

                company_el = await card.query_selector("h2.ohgq7e-0.eecanG")
                company = await company_el.inner_text() if company_el else ""

                location_els = await card.query_selector_all("#location-text")
                locations = [await el.inner_text() for el in location_els if el]
                location = ", ".join(loc.strip() for loc in locations if loc)

                salary_el = await card.query_selector("span#salary-text")
                salary = await salary_el.inner_text() if salary_el else ""

                date_el = await card.query_selector("span.hbrCCy")
                date_posted = await date_el.inner_text() if date_el else ""
                
                url = url.replace("/company","")
                
                detail_page = await browser.new_page()
                await detail_page.goto(url, timeout=60000, wait_until="domcontentloaded")
                
                try:
                    desc_el = await detail_page.query_selector("#job-detail")
                    description = await desc_el.inner_text() if desc_el else ""
                except:
                    description = ""
                    
                try:
                    qual_el = await detail_page.query_selector("#job-properties-wrapper ol")
                    qualifications_list = await qual_el.query_selector_all("li") if qual_el else []
                    qualifications = [await li.inner_text() for li in qualifications_list]
                except:
                    qualifications = []

                await detail_page.close()
                
                description_part1, description_part2, description_part3 = split_description(description)

                results.append({
                    "title": title.strip(),
                    "company": company.strip(),
                    "location": location.strip(),
                    "salary": salary.strip(),
                    "date_posted": date_posted.strip(),
                    "url": url,
                    "description_part1": description_part1,
                    "description_part2": description_part2,
                    "description_part3": description_part3,
                    "qualifications": qualifications
                })

        await browser.close()

        raw_path  = f"data/jobs_{today_str}.json"
        with open(raw_path , "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        print(f"Saved {len(results)} jobs to {raw_path}")
        
        embeddings = []
        for job in results:
            qualifications = " ".join(job["qualifications"])
            combined_text = f"{job['title']} {job['description_part1']} {job['description_part2']} {job['description_part3']} {qualifications}"
            combined_text = combined_text[:10000]
            try:
                lang = detect(combined_text)
            except:
                lang = "en"
            if lang == "th":
                print("Detected Thai. Translating...")
                translated_text = translate_thai_to_english(combined_text)
            else:
                translated_text = combined_text
            embedding = get_embedding(translated_text)
            if embedding:
                embeddings.append({"job": job, "embedding": embedding})

        embed_path = f"data/jobs_{today_str}_embeddings.json"
        with open(embed_path, "w", encoding="utf-8") as f:
            json.dump(embeddings, f, ensure_ascii=False)
        print(f"Saved {len(embeddings)} job embeddings to {embed_path}")
        

if __name__ == "__main__":
    asyncio.run(scrape_jobthai())
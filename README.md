# 🔍 JobThai AI Recommender

A project that scrapes job listings for **Data Engineer** roles from [JobThai.com](https://www.jobthai.com/), generates **OpenAI embeddings**, and performs **job recommendations via a Flask API plus ui interface** called "JobThai AI Chatbot".

---

## 📁 Project Structure

├── app/
│ ├── templates/
│ │  ├──index.html # for ui web page
│ ├── main.py 
│ ├── recommender.py # Embedding-based recommender logic
│ └── scrape_jobs.py # job scraper with embedding storage
├── data/ # Output folder
├── .env
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── README.md

---

## 🔧 Setup

### 1. Clone the repo

git clone https://github.com/Iamfloke/jobthai-ai-recommender.git
cd jobthai-ai-recommender

### 2. Create .env file. the api key is from openai. you can create it from https://platform.openai.com/api-keys

OPENAI_API_KEY=sk-xxxxxx

### 3. Build the Docker image

docker-compose build

### 4. Run the scraper to fetch job listings + generate embeddings

docker-compose run --rm jobthai-app python app/scrape_jobs.py

This generates:

    data/jobs_<date>.json

    data/jobs_<date>_embeddings.json

### 5. Run the Flask recommendation API

docker-compose up

🔍 Example API Usage

entering http://localhost:8080

**you can type in both Thai and English**

![pic1](assets/Screenshot%202025-06-14%20215724.png)
![pic2](assets/Screenshot%202025-06-14%20215805.png)
![pic3](assets/Screenshot%202025-06-14%20220110.png)

**Or using curl**

POST /recommend

curl -X POST http://localhost:8080/recommend \
  -H "Content-Type: application/json" \
  -d '{"query": "data engineer bangkok which can work from home (wfh)"}'

Response:

[
  {
    "title": "Data Engineer - WFH",
    "company": "THiNKNET",
    "location": "BTS ช่องนนทรี, MRT สีลม",
    "salary": "25,000 - 70,000 บาท",
    "url": "https://www.jobthai.com/th/job/563448",
    "score": 0.872
  },
  ...
]

### 6. stop container

Use Ctrl+C in the terminal, or run docker compose down

## 📝 License

This project is licensed under the [MIT License](LICENSE).
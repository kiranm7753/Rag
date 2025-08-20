## ⚠️ Notes

- The app is in development — prefer smaller PDFs initially
- All files (FAISS + PDFs) are **deleted after logout**
- This app is designed for dev/testing — enable HTTPS and database hardening before going to production.
- Do not upload large PDF files initially. Start with small PDFs to avoid crashes.
- Ensure your `.env` file is correctly configured before building/running Docker.
- EC2 instances should have at least 20 GB of storage.


# 🧠 PDF RAG Chatbot
_Built with Flask + AWS + Docker + OpenAI API

A lightweight **PDF-based RAG chatbot** system that allows users to upload PDFs, chat with them using OpenAI's embeddings, and store everything securely using AWS S3 and FAISS — all packed inside a Dockerized Flask app.

---

## 🔍 About the Project

**Retrieval-Augmented Generation (RAG)** is a powerful approach that combines traditional information retrieval with modern generative AI. Instead of relying solely on the limited context of a language model, a RAG system **retrieves relevant external data (like documents or PDFs)** and feeds it into the model to generate more accurate, grounded, and up-to-date answers.

This project implements a **lightweight PDF-based RAG chatbot** that allows users to:

- Upload and index custom PDF files using **OpenAI Embeddings**.
- Retrieve relevant content via **FAISS**, a vector similarity search engine.
- Chat naturally with the content using **retrieval-augmented prompts**.
- Store and manage user documents securely with **AWS S3**, including auto-cleanup on logout.

This system demonstrates how anyone can combine LLMs, vector search, cloud storage, and basic authentication into a complete **document-aware AI assistant**, deployed securely using **Docker and AWS EC2**.

---


## 📊 Architecture

![architecture_diagram](https://github.com/user-attachments/assets/1b9947ac-1a55-4d02-91f9-46888a545984)



## 🔐 Features

- User login & registration (Flask-Login + Bcrypt)
- Upload multiple PDFs
- Automatically splits, embeds and indexes documents (OpenAI + FAISS)
- Chat with the documents
- Deletes user data (from S3 + local) on logout
- Dockerized & production-ready
- Deployable to EC2

## 💼 Real-World Applications

This PDF RAG Chatbot can be adapted for a variety of **real-world use cases**:

- 📚 **Academic Research Assistant**  
  Upload research papers and ask contextual questions across multiple documents.

- 🏢 **Enterprise Knowledge Base**  
  Upload internal company documents, SOPs, and reports to enable intelligent document querying.

- 🧾 **Legal & Compliance Chatbot**  
  Ingest legal contracts, policy documents, or compliance manuals for quick reference.

- 💰 **Financial Reports Assistant**  
  Chat with earnings reports, market analysis, and investment PDFs to extract insights.

- 🏥 **Healthcare Documentation Support**  
  Upload clinical guidelines, medical articles, and patient documentation for contextual assistance.

- 📖 **E-Book/Document Summarizer**  
  Upload long documents and ask for summaries, highlights, or explanations.

- 👨‍💻 **Developer Documentation Bot**  
  Provide quick answers from PDFs of APIs, SDKs, and technical manuals.

## 🧪 Technologies Used

- **Flask** (Backend + Auth)
- **SQLAlchemy** (User DB)
- **FAISS** (Vector DB)
- **OpenAI Embeddings** (via `text-embedding-3-small`)
- **Docker** (for containerization)
- **AWS S3** (user document storage)
- **HTML/CSS/JS** (UI with Dark Mode toggle, error/status UX)

## ⚙️ Setup Instructions (Local)

```bash
# Clone repo
$ git clone https://github.com/kiranm7753/Rag.git
$ cd rag-chatbot

# Create virtual env and activate
$ python -m venv rag_env
$ source rag_env/bin/activate  # Windows: rag_env\Scripts\activate

# Install dependencies
$ pip install -r requirements.txt

# Add your .env file
$ touch .env
```

`.env` should contain:
```env
SECRET_KEY=your_flask_secret_key
OPENAI_API_KEY=your_openai_key
AWS_ACCESS_KEY_ID=your_aws_access_key
AWS_SECRET_ACCESS_KEY=your_aws_secret
AWS_REGION=your_aws_region
S3_BUCKET_NAME=your_bucket_name
```

Then:
```bash
python main.py
```

## 🐳 Docker Instructions

```bash
# Build image
$ docker build -t rag-chatbot .

# Run container with .env (no need for docker-compose)
$ docker run -d -p 5000:5000 --env-file .env rag-chatbot
```

## ☁️ Deploy to AWS EC2

1. Launch EC2 (Ubuntu 24.04 LTS)
2. Install Docker
3. Create `.env` file on the EC2 instance (manually or using `scp`)
4. Pull image from DockerHub:
```bash
docker pull <your-dockerhub-username>/rag-chatbot-aws
```
5. Run:
```bash
docker run -d -p 80:5000 --env-file .env <your-dockerhub-username>/rag-chatbot-aws
```
6. Access app via EC2 Public IP (`http://<EC2-IP>`)

> ⚠️ If using Docker Desktop or testing locally, Docker will also respect `.env` via `--env-file` as shown.


## 🛠️ Planned Improvements
- Add persistent DB storage (PostgreSQL/RDS)
- Add HTTPS support with certbot or Cloudflare
- Add file size & format validation UI-side
- Improve UI/UX (e.g., better error handling, mobile layout)

## 🤝 Contributing

Have ideas to improve this RAGbot? Found a bug or want to extend it?

Feel free to open an issue or submit a pull request. Contributions are welcome and appreciated!

Please ensure:
- Code is clean, tested, and documented
- PRs are scoped to one enhancement/fix at a time



## 📄 License
This project is licensed under the [MIT License](LICENSE).
---

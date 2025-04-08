import os
import faiss
import numpy as np
import pickle
import openai
from dotenv import load_dotenv
from utils.s3_utils import upload_file_to_s3
from utils.pdf_loader import load_and_split_pdf
from utils.cleaner import clean_text

# Load API key from .env
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")
EMBEDDING_MODEL = "text-embedding-3-small"

# Get embedding from OpenAI API
def get_openai_embedding(text: str) -> list:
    response = openai.embeddings.create(input=[text], model=EMBEDDING_MODEL)
    return response.data[0].embedding


# Build vectorstore for a specific user and upload to S3
def build_vectorstore(file_paths: list, user_id: str):
    print("📄 Loading and chunking PDFs...")
    documents = []
    for path in file_paths:
        documents.extend(load_and_split_pdf(path))

    print("🧹 Cleaning and embedding documents...")
    texts = []
    vectors = []

    for doc in documents:
        cleaned = clean_text(doc.page_content)
        try:
            embedding = get_openai_embedding(cleaned)
            texts.append(cleaned)
            vectors.append(embedding)
        except Exception as e:
            print(f"❌ Embedding failed for a chunk: {e}")

    if not vectors:
        raise ValueError("No embeddings were created — aborting vectorstore creation.")

    # Create FAISS index
    print("💾 Creating FAISS index...")
    dimension = len(vectors[0])
    index = faiss.IndexFlatL2(dimension)
    index.add(np.array(vectors).astype("float32"))

    # Save locally
    local_path = f"vectorstores/{user_id}/"
    os.makedirs(local_path, exist_ok=True)

    faiss.write_index(index, os.path.join(local_path, "index.index"))
    with open(os.path.join(local_path, "docs.pkl"), "wb") as f:
        pickle.dump(texts, f)

    print("☁️ Uploading vectorstore to S3...")
    for fname in os.listdir(local_path):
        local_file = os.path.join(local_path, fname)
        s3_key = f"users/{user_id}/faiss/{fname}"
        upload_file_to_s3(local_file, s3_key)

    print(f"✅ Vectorstore for {user_id} successfully uploaded to S3.")

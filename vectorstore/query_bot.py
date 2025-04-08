import os
import faiss
import pickle
import numpy as np
import openai
from utils.s3_utils import download_file_from_s3
from dotenv import load_dotenv
from utils.cleaner import clean_text

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")
EMBEDDING_MODEL = "text-embedding-3-small"

def get_openai_embedding(text: str) -> list:
    response = openai.embeddings.create(input=[text], model=EMBEDDING_MODEL)
    return response.data[0].embedding


def query_rag(query: str, user_id: str, top_k: int = 5) -> dict:
    print("⬇️ Downloading FAISS index from S3...")
    base_path = f"vectorstores/{user_id}/"
    os.makedirs(base_path, exist_ok=True)

    index_file = os.path.join(base_path, "index.index")
    docs_file = os.path.join(base_path, "docs.pkl")

    download_file_from_s3(f"users/{user_id}/faiss/index.index", index_file)
    download_file_from_s3(f"users/{user_id}/faiss/docs.pkl", docs_file)

    # Load vectorstore
    index = faiss.read_index(index_file)
    with open(docs_file, "rb") as f:
        documents = pickle.load(f)

    print("🔎 Embedding query and searching...")
    cleaned_query = clean_text(query)
    query_vec = np.array(get_openai_embedding(cleaned_query)).astype("float32").reshape(1, -1)
    D, I = index.search(query_vec, top_k)

    context = "\n\n".join([documents[i] for i in I[0] if i < len(documents)])

    print("💬 Sending to OpenAI for generation...")
    system_prompt = "Answer the question based only on the provided context."
    user_prompt = f"Context:\n{context}\n\nQuestion:\n{query}"

    completion = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
    )

    return {
        "answer": completion.choices[0].message.content.strip()
    }

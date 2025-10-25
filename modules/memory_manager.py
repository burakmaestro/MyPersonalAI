import os
import datetime
import uuid
import chromadb
from chromadb.utils import embedding_functions

# Ortam değişkenlerinden API anahtarını al
from dotenv import load_dotenv
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# ChromaDB ayarları
CHROMA_DB_PATH = os.path.join(os.getcwd(), "data/chroma_memory")
COLLECTION_NAME = "echo_chat_memory"

# OpenAI embedding fonksiyonu
openai_ef = embedding_functions.OpenAIEmbeddingFunction(
    api_key=OPENAI_API_KEY,
    model_name="text-embedding-ada-002"
)

# Chroma istemcisi
chroma_client = chromadb.PersistentClient(path=CHROMA_DB_PATH)

# Koleksiyonu oluştur veya mevcut olanı yükle
collection = chroma_client.get_or_create_collection(
    name=COLLECTION_NAME,
    embedding_function=openai_ef
)

def add_to_memory(role, content):
    """Bir mesajı ChromaDB'ye ekler."""
    try:
        collection.add(
            documents=[f"{role}: {content}"],
            metadatas=[{"role": role, "timestamp": datetime.datetime.now().isoformat()}],
            ids=[f"{role}_{uuid.uuid4()}"]
        )
    except Exception as e:
        print(f"[HATA] Hafızaya ekleme başarısız: {e}")

def query_memory(query_text, n_results=5):
    """Kullanıcının yeni girdisine göre geçmişi sorgular."""
    try:
        results = collection.query(
            query_texts=[query_text],
            n_results=n_results,
            include=['documents', 'metadatas']
        )

        if results and results["documents"] and results["documents"][0]:
            docs = []
            for doc, meta in zip(results["documents"][0], results["metadatas"][0]):
                docs.append(f"{doc} (Tarih: {meta.get('timestamp')})")
            return docs
        else:
            return []
    except Exception as e:
        print(f"[HATA] Hafıza sorgusu başarısız: {e}")
        return []

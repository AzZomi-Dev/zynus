from langchain_huggingface.embeddings import HuggingFaceEmbeddings
from config import EMB_MODEL, OFFLINE_HF_EMB
import threading

_emb_lock = threading.Lock()
_hf_embeddings: HuggingFaceEmbeddings | None = None

def get_huggingface_embeddings():
    global _hf_embeddings

    if _hf_embeddings is not None:
        return _hf_embeddings

    with _emb_lock:
        if _hf_embeddings is not None:
            return _hf_embeddings
        
        _hf_embeddings = HuggingFaceEmbeddings(
            model_name=EMB_MODEL,
            model_kwargs={"local_files_only": OFFLINE_HF_EMB}
        )
        return _hf_embeddings
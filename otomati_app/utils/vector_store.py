from langchain_community.embeddings.spacy_embeddings import SpacyEmbeddings
from langchain_community.vectorstores import FAISS

embeddings = SpacyEmbeddings(model_name="en_core_web_sm")


def vector_store(text_chunks):
    vs = FAISS.from_texts(text_chunks, embedding=embeddings)
    vs.save_local("faiss_db")


def load_vector_store():
    return FAISS.load_local(
        "faiss_db",
        embeddings,
        allow_dangerous_deserialization=True
    )

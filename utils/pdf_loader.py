from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter


def load_and_split_pdf(file_path: str, chunk_size=500, chunk_overlap=100):
    """
    Loads a PDF and splits it into smaller overlapping chunks.
    Returns a list of Document objects.
    """
    loader = PyPDFLoader(file_path)
    documents = loader.load()

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size, chunk_overlap=chunk_overlap
    )

    chunks = splitter.split_documents(documents)
    return chunks

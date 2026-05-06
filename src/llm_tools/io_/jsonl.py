import jsonlines
from langchain_core.documents import Document


def save_docs_to_jsonl(documents: list[Document], file_path: str) -> None:
    with jsonlines.open(file_path, mode="w") as writer:
        for doc in documents:
            writer.write(doc.model_dump())


def load_docs_from_jsonl(file_path: str) -> list[Document]:
    docs = []
    with jsonlines.open(file_path, mode="r") as reader:
        for obj in reader:
            docs.append(Document(**obj))
    return docs

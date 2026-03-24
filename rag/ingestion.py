import os

from dotenv import load_dotenv
load_dotenv()
from langchain_community.document_loaders import TextLoader
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

from state.MeetingState import MeetingState

from langchain_pinecone import PineconeVectorStore
from pinecone import Pinecone


embeddings = GoogleGenerativeAIEmbeddings(
    model="text-embedding-005",
    project="project-411429ce-48ab-4ae8-aab",
    location="us-central1"
)
INDEX_NAME = "ai-meeting-summarizer"

def ingestion(state: MeetingState) -> dict:
    parts = []

    # structured output from the graph
    if state.get("summary"):
        parts.append(f"SUMMARY:\n{state['summary']}")
    if state.get("action_items"):
        lines = []
        for item in state["action_items"]:
            if isinstance(item, dict):
                lines.append(
                    f"- [{item.get('id','')}] {item.get('task','')} "
                    f"| Owner: {item.get('owner','')} | Due: {item.get('due','')}"
                    f"| Priority: {item.get('priority','')} "
                )
            else:
                lines.append(f"- {item}")
        parts.append("ACTION ITEMS:\n" + "\n".join(lines))
    if state.get("decisions"):
        parts.append("DECISIONS:\n" + "\n".join(state["decisions"]))

    # ✅ also index the raw transcript itself
    parts.append(f"RAW TRANSCRIPT:\n{state['raw_transcript']}")
    namespace = state.get("pinecone_namespace")
    corpus = "\n\n".join(parts)

    chunks = RecursiveCharacterTextSplitter(
        chunk_size=500, chunk_overlap=80
    ).create_documents([corpus])

    # clear old vectors for this namespace before upserting
    # pc = Pinecone()
    # index = pc.Index(INDEX_NAME)
    # index.delete(delete_all=True, namespace=namespace)

    PineconeVectorStore.from_documents(
        documents=chunks,
        embedding=embeddings,
        index_name=INDEX_NAME,
        namespace=namespace,
    )
    return {
        "pinecone_index": INDEX_NAME,
        "pinecone_namespace": namespace,
        "chat_history": [],
        "user_question": None,
    }
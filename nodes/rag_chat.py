from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_pinecone import PineconeVectorStore

from state.MeetingState import MeetingState
from utils.llm import llm

embeddings = GoogleGenerativeAIEmbeddings(
    model="text-embedding-005",
    project="project-411429ce-48ab-4ae8-aab",
    location="us-central1"
)

def rag_chat(state: MeetingState) -> dict:
    question = state["user_question"]

    vs = PineconeVectorStore(
        index_name=state["pinecone_index"],
        embedding=embeddings,
        namespace=state["pinecone_namespace"]
    )

    docs = vs.max_marginal_relevance_search(
        question,
        k=20,
        fetch_k=20
    )
    if not docs:
        answer = "I couldn't find relevant content for that question."
    else:
        context = "\n---\n".join(
            f"[chunk {i + 1}]\n{d.page_content}"
            for i, d in enumerate(docs)
        )

        history_messages = []

        for msg in state["chat_history"]:
            if msg["role"] == "user":
                history_messages.append(HumanMessage(content=msg["content"]))
            elif msg["role"] == "assistant":
                history_messages.append(AIMessage(content=msg["content"]))

        messages = [
            SystemMessage(content="You are a meeting assistant. Answer only from the provided context. Be concise."),
            *history_messages,
            HumanMessage(content=f"Context:\n{context}\n\nQuestion: {question}"),
        ]

        response = llm.invoke(messages)

        answer = response.content

    new_history = state["chat_history"] + [
        {"role": "user", "content": question},
        {"role": "assistant", "content": answer},
    ]
    return {"chat_history": new_history, "user_question": None}


from dotenv import load_dotenv
load_dotenv()
import os

from langchain_google_genai import ChatGoogleGenerativeAI

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    project=os.getenv("GOOGLE_PROJECT_ID"),
    location=os.getenv("GOOGLE_LOCATION")
)
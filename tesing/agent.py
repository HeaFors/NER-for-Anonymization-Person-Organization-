import os
import json
from typing import List, Optional
from pydantic import BaseModel, Field
from dotenv import load_dotenv

from langchain_community.document_loaders import TextLoader
from langchain_community.vectorstores import FAISS
from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from transformers import AutoModelForTokenClassification, AutoTokenizer, pipeline

load_dotenv()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_PATH = os.path.join(BASE_DIR, "ner_model")
TOKENIZER_PATH = os.path.join(BASE_DIR, "tokenizer")
DATA_PATH = os.path.join(BASE_DIR, "data", "student_info.txt")

class EntityItem(BaseModel):
    word: str = Field(description="Витягнута сутність (наприклад, ім'я або назва компанії)")
    category: str = Field(description="Категорія сутності: суворо 'PER' або 'ORG'")


class NERToolResponse(BaseModel):
    has_entities: bool = Field(description="Чи знайдено хоча б одну сутність PER/ORG")
    entities: List[EntityItem] = Field(default_factory=list, description="Список знайдених сутностей")


class RAGDocumentItem(BaseModel):
    content: str = Field(description="Текст знайденого фрагмента")


class RAGToolResponse(BaseModel):
    found: bool = Field(description="Чи знайдено інформацію в базі даних")
    results: List[RAGDocumentItem] = Field(default_factory=list, description="Знайдені фрагменти")

model = AutoModelForTokenClassification.from_pretrained(MODEL_PATH)
tokenizer = AutoTokenizer.from_pretrained(TOKENIZER_PATH)
ner_pipeline = pipeline(
    "ner", model=model, tokenizer=tokenizer, aggregation_strategy="simple"
)

loader = TextLoader(DATA_PATH, encoding="utf-8")
raw_documents = loader.load()
text_splitter = RecursiveCharacterTextSplitter(chunk_size=300, chunk_overlap=50)
documents = text_splitter.split_documents(raw_documents)

embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
vectorstore = FAISS.from_documents(documents, embeddings)
retriever = vectorstore.as_retriever(search_kwargs={"k": 3})


@tool
def fine_tuned_ner_tool(text: str) -> str:
    """Аналізує текст та витягує сутності людей (PER) та організацій (ORG). Повертає JSON."""
    raw_entities = ner_pipeline(text)
    allowed_labels = {"PER", "ORG", "B-PER", "I-PER", "B-ORG", "I-ORG"}

    extracted_items = []
    for ent in raw_entities:
        label = ent.get("entity_group") or ent.get("entity")
        if label in allowed_labels:
            clean_category = "PER" if "PER" in label else "ORG"
            extracted_items.append(EntityItem(word=ent["word"], category=clean_category))

    # ФОЛБЕК: Якщо локальний BERT (англомовний) нічого не знайшов у кириличному тексті
    if not extracted_items and any('\u0400' <= char <= '\u04FF' for char in text):
        fallback_llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
        structured_llm = fallback_llm.with_structured_output(NERToolResponse)

        fallback_response = structured_llm.invoke(
            f"Extract ONLY Person (PER) and Organization (ORG) entities from this text: '{text}'. "
            f"Ignore locations (LOC), dates, and misc."
        )
        return fallback_response.model_dump_json()

    response = NERToolResponse(
        has_entities=len(extracted_items) > 0,
        entities=extracted_items
    )
    return response.model_dump_json()

@tool
def student_rag_tool(query: str) -> str:
    """Шукає інформацію про студентів, їхні оцінки, теми курсових та факультети. Повертає JSON."""
    docs = retriever.invoke(query)
    if not docs:
        return RAGToolResponse(found=False, results=[]).model_dump_json()

    results = [RAGDocumentItem(content=doc.page_content) for doc in docs]
    return RAGToolResponse(found=True, results=results).model_dump_json()


tools = [fine_tuned_ner_tool, student_rag_tool]
tools_by_name = {t.name: t for t in tools}

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
llm_with_tools = llm.bind_tools(tools)

SYSTEM_PROMPT = SystemMessage(
    content=(
        "You are an intelligent AI Router and Assistant specializing in privacy-aware text analysis and student information retrieval.\n\n"
        "CORE DUTIES & TOOL ROUTING:\n"
        "1. ENTITY EXTRACTION: When asked to find/extract entities, ALWAYS invoke 'fine_tuned_ner_tool' first.\n"
        "2. STUDENT DATA RETRIEVAL: When asked about students, grades, or faculty, invoke 'student_rag_tool'.\n\n"
        "RESPONSE RULES FOR NER:\n"
        "- Parse the JSON returned by 'fine_tuned_ner_tool'.\n"
        "- If 'fine_tuned_ner_tool' fails to identify Ukrainian/Cyrillic entities (returns empty results), use your internal knowledge to identify missing PER and ORG entities from the user prompt.\n"
        "- STRICTLY EXCLUDE Locations (LOC) and MISC entities.\n"
        "- ALWAYS reply in the exact same language as the user's input."
    )
)


def process_query(user_input: str) -> str:
    messages = [SYSTEM_PROMPT, HumanMessage(content=user_input)]
    ai_msg = llm_with_tools.invoke(messages)

    if not ai_msg.tool_calls:
        return ai_msg.content

    messages.append(ai_msg)
    for tool_call in ai_msg.tool_calls:
        selected_tool = tools_by_name[tool_call["name"]]
        tool_output = selected_tool.invoke(tool_call["args"])
        messages.append(
            ToolMessage(content=str(tool_output), tool_call_id=tool_call["id"])
        )

    final_response = llm.invoke(messages)
    return final_response.content


if __name__ == "__main__":
    print("\n=== Agent Terminal Ready ===")
    while True:
        user_input = input("\nВи: ").strip()
        if not user_input or user_input.lower() in ["exit", "quit", "вихід"]:
            break
        print(f"\nАгент: {process_query(user_input)}")
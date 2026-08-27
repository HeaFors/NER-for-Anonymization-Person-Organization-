import os
from dotenv import load_dotenv
from langchain_community.document_loaders import TextLoader
from langchain_community.vectorstores import FAISS
from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from transformers import AutoModelForTokenClassification, AutoTokenizer, pipeline

# ключі з .env файлу
load_dotenv()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_PATH = os.path.join(BASE_DIR, "ner_model")
TOKENIZER_PATH = os.path.join(BASE_DIR, "tokenizer")
DATA_PATH = os.path.join(BASE_DIR, "data", "student_info.txt")

model = AutoModelForTokenClassification.from_pretrained(MODEL_PATH)
tokenizer = AutoTokenizer.from_pretrained(TOKENIZER_PATH)
ner_pipeline = pipeline(
    "ner", model=model, tokenizer=tokenizer, aggregation_strategy="simple"
)


@tool
def fine_tuned_ner_tool(text: str) -> str:
    """Аналізує текст та знаходить сутності (імена PER, організації ORG, локації LOC)."""
    raw_entities = ner_pipeline(text)
    entities = [(ent["word"], ent["entity_group"]) for ent in raw_entities]
    return f"Extracted raw entities: {entities}" if entities else "No entities found."


# RAG Tool
loader = TextLoader(DATA_PATH, encoding="utf-8")
documents = loader.load()
embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
vectorstore = FAISS.from_documents(documents, embeddings)
retriever = vectorstore.as_retriever(search_kwargs={"k": 3})


@tool
def student_rag_tool(query: str) -> str:
    """Шукає інформацію про студентів, їхні оцінки, теми курсових та факультети."""
    docs = retriever.invoke(query)
    return "\n".join([doc.page_content for doc in docs])


tools = [fine_tuned_ner_tool, student_rag_tool]
tools_by_name = {t.name: t for t in tools}

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
llm_with_tools = llm.bind_tools(tools)

# системний промпт
SYSTEM_PROMPT = SystemMessage(
    content=(
        "You are an AI conversational assistant.\n\n"
        "STRICT LANGUAGE RULES:\n"
        "1. Automatically detect the user's input language.\n"
        "2. ALWAYS respond strictly in the SAME LANGUAGE as the user query (if user writes in English -> reply in English; if in Ukrainian -> reply in Ukrainian).\n"
        "3. Do NOT translate standard entity classification labels (PER, ORG, LOC) in your output.\n\n"
        "TOOL USAGE:\n"
        "- For questions about students, grades, coursework topics, or faculties, ALWAYS call 'student_rag_tool'.\n"
        "- For analyzing text entities, call 'fine_tuned_ner_tool'."
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
        if not user_input:
            continue
        if user_input.lower() in ["exit", "quit", "вихід"]:
            break

        response = process_query(user_input)
        print(f"\nАгент: {response}")
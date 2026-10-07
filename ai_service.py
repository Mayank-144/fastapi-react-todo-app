import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Initialize Groq LLM (qwen/qwen3.8-27b provides high speed and multilingual comprehension)
llm = ChatGroq(
    groq_api_key=GROQ_API_KEY,
    model_name="qwen/qwen3.8-27b",
    temperature=0.2
)

output_parser = StrOutputParser()


# ==========================================
# Feature 1: Task Summary Generator
# ==========================================
def generate_task_summary(tasks: list[dict]) -> str:
    """
    Generates a structured, motivating task summary.
    Accepts tasks in English, Hindi, or Hinglish, and outputs clean, structured English.
    """
    if not tasks:
        return "You currently have no tasks in your list! Add a new task using the input box above."
    
    total = len(tasks)
    done_count = sum(1 for t in tasks if t['is_done'])
    pending_count = total - done_count

    tasks_text = "\n".join([
        f"- {t['title']} [{'COMPLETED' if t['is_done'] else 'PENDING'}]"
        for t in tasks
    ])
    
    prompt = ChatPromptTemplate.from_messages([
        (
            "system",
            "You are a smart, friendly Task Manager AI assistant.\n"
            "LANGUAGE SUPPORT:\n"
            "- The user input, task titles, or questions may be in English, Hindi (Devanagari), or Hinglish (Roman Hindi/Urdu).\n"
            "- Accurately understand whatever language is provided and return a professional, structured response in English.\n\n"
            "CRITICAL FORMATTING RULES:\n"
            "1. Do NOT use markdown tables (no '|---', no '| col |').\n"
            "2. Do NOT use markdown headers like '###' or '##'.\n"
            "3. Do NOT use bold markdown stars like '**text**'.\n"
            "4. Use clean, readable bullet points (•, 📊, ⚡, 📌, ✅, ⏳).\n"
            "5. Structure the response as follows:\n"
            "   📊 Overall Status: Total, Completed, and Pending count.\n"
            "   ⚡ Progress Overview: 1-2 encouraging, actionable sentences.\n"
            "   📌 Next Steps: Key focus recommendations for remaining pending tasks."
        ),
        (
            "human",
            "User task list:\n{tasks_text}\n\nTask Statistics: Total: {total}, Completed: {done_count}, Pending: {pending_count}\n\nProvide a clean summary:"
        )
    ])
    
    chain = prompt | llm | output_parser
    return chain.invoke({
        "tasks_text": tasks_text,
        "total": total,
        "done_count": done_count,
        "pending_count": pending_count
    }).strip()


# ==========================================
# Feature 2: Task Priority Suggestions
# ==========================================
def suggest_task_priorities(tasks: list[dict]) -> str:
    """
    Analyzes pending tasks and categorizes them into High, Medium, and Low priorities.
    Accepts inputs in English, Hindi, or Hinglish, and returns clean English recommendations.
    """
    pending_tasks = [t for t in tasks if not t['is_done']]
    if not pending_tasks:
        return "🎉 Great job! All your tasks are completed. Enjoy your day!"
    
    tasks_text = "\n".join([f"- {t['title']}" for t in pending_tasks])
    
    prompt = ChatPromptTemplate.from_messages([
        (
            "system",
            "You are an expert Productivity Coach AI.\n"
            "LANGUAGE SUPPORT:\n"
            "- The user input or tasks may be provided in English, Hindi, or Hinglish.\n"
            "- Understand the input context completely in any language and deliver clear priority recommendations in English.\n\n"
            "CRITICAL FORMATTING RULES:\n"
            "1. Do NOT use markdown tables (no '|---', no '| col |').\n"
            "2. Do NOT use markdown headers like '###' or '##'.\n"
            "3. Do NOT use bold markdown stars like '**text**'.\n"
            "4. Structure output cleanly into distinct sections with emojis:\n\n"
            "🔴 HIGH PRIORITY (Do First):\n"
            "• [Task Name] -> [Brief reason in English]\n\n"
            "🟡 MEDIUM PRIORITY (Do Next):\n"
            "• [Task Name] -> [Brief reason in English]\n\n"
            "🟢 LOW PRIORITY (Later / Leisure):\n"
            "• [Task Name] -> [Brief reason in English]\n\n"
            "💡 Pro Tip: [1 short actionable productivity advice]"
        ),
        (
            "human",
            "Here are the user's pending tasks:\n{tasks_text}\n\nCategorize and prioritize them:"
        )
    ])
    
    chain = prompt | llm | output_parser
    return chain.invoke({"tasks_text": tasks_text}).strip()


# ==========================================
# Feature 3: Natural Language Task Extraction
# ==========================================
def extract_task_from_natural_language(user_text: str) -> str:
    """
    Extracts a concise, actionable Todo Title from natural language text.
    Handles input in English, Hindi, or Hinglish seamlessly.
    Example: 'Mujhe kal shaam 6 baje gym jana hai' -> 'Gym workout at 6:00 PM tomorrow'
    """
    prompt = ChatPromptTemplate.from_messages([
        (
            "system",
            "You are an intelligent Todo Title Extractor.\n"
            "LANGUAGE SUPPORT:\n"
            "- The user may express their task in English, Hindi, or Hinglish.\n"
            "- Accurately interpret the task intent, dates, times, and activities in any of these languages.\n"
            "- Output a clean, concise, actionable task title in clear English.\n\n"
            "CRITICAL RULES:\n"
            "1. Return ONLY the extracted task title.\n"
            "2. Do NOT include quotes, asterisks, prefixes, or explanations."
        ),
        (
            "human",
            "User text: '{user_text}'\n\nClean Task Title:"
        )
    ])
    
    chain = prompt | llm | output_parser
    res = chain.invoke({"user_text": user_text})
    # Sanitize any accidental quotes or asterisks
    clean_title = res.strip().strip('"').strip("'").replace("**", "").replace("*", "")
    return clean_title

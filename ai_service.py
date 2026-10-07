import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Groq LLM Initialize (qwen/qwen3.8-27b)
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
    User ke saare tasks lekar clean, structured AI summary banata hai.
    No raw markdown tables, no triple hashes, no asterisks clutter.
    """
    if not tasks:
        return "Abhi aapke paas koi task nahi hai! Upar diye box se naya task add karein."
    
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
            "Aap ek friendly Task Manager AI assistant ho.\n"
            "CRITICAL FORMATTING RULES:\n"
            "1. Do NOT use markdown tables (no '|---', no '| col |').\n"
            "2. Do NOT use markdown headers like '###' or '##'.\n"
            "3. Do NOT use bold markdown stars like '**text**'.\n"
            "4. Hinglish me clean, readable bullet points (•, 📌, ✅, ⏳) use karo.\n"
            "5. Structure:\n"
            "   📊 Overall Status: Total, Completed, aur Pending count.\n"
            "   ⚡ Progress Review: 1-2 motivating lines.\n"
            "   📌 Next Focus: Jo pending hain unke liye quick recommendation."
        ),
        (
            "human",
            "User ke tasks:\n{tasks_text}\n\nTotal: {total}, Completed: {done_count}, Pending: {pending_count}\n\nClean Hinglish summary do:"
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
    Pending tasks ko analyze karke High, Medium, Low priority suggest karta hai.
    No raw markdown tables or stars.
    """
    pending_tasks = [t for t in tasks if not t['is_done']]
    if not pending_tasks:
        return "🎉 Shabash! Aapke saare tasks already completed hain. Enjoy your free time!"
    
    tasks_text = "\n".join([f"- {t['title']}" for t in pending_tasks])
    
    prompt = ChatPromptTemplate.from_messages([
        (
            "system",
            "Aap ek smart Productivity Coach AI ho.\n"
            "CRITICAL FORMATTING RULES:\n"
            "1. Do NOT use markdown tables (no '|---', no '| col |').\n"
            "2. Do NOT use markdown headers like '###' or '##'.\n"
            "3. Do NOT use bold markdown stars like '**text**'.\n"
            "4. Clear, clean sections me output do with emojis:\n\n"
            "🔴 HIGH PRIORITY (Pehle Ye Karo):\n"
            "• [Task Name] -> [Short reason in Hinglish]\n\n"
            "🟡 MEDIUM PRIORITY (Iske Baad):\n"
            "• [Task Name] -> [Short reason in Hinglish]\n\n"
            "🟢 LOW PRIORITY (Fursat Me):\n"
            "• [Task Name] -> [Short reason in Hinglish]\n\n"
            "💡 Pro Tip: [1 short motivational line]"
        ),
        (
            "human",
            "Ye mere pending tasks hain:\n{tasks_text}\n\nInhe categorize karke clean Hinglish me priority recommendation do:"
        )
    ])
    
    chain = prompt | llm | output_parser
    return chain.invoke({"tasks_text": tasks_text}).strip()


# ==========================================
# Feature 3: Natural Language Task Extraction
# ==========================================
def extract_task_from_natural_language(user_text: str) -> str:
    """
    User ke casual text se clean Todo Title nikalta hai.
    Example: 'Mujhe kal shaam 6 baje gym jana hai' -> 'Kal shaam 6:00 PM Gym jana'
    """
    prompt = ChatPromptTemplate.from_messages([
        (
            "system",
            "Aap ek Todo Title Extractor ho.\n"
            "User casual Hinglish ya English me apna task bolega.\n"
            "Aapko sirf aur sirf ek clean, crisp Todo Title return karna hai.\n"
            "Do NOT include quotes, do NOT include stars, do NOT include explanations."
        ),
        (
            "human",
            "User text: '{user_text}'\n\nClean Todo Title:"
        )
    ])
    
    chain = prompt | llm | output_parser
    res = chain.invoke({"user_text": user_text})
    # Extra cleanup to guarantee no markdown stars or surrounding quotes
    clean_title = res.strip().strip('"').strip("'").replace("**", "").replace("*", "")
    return clean_title

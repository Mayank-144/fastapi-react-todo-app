import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Groq LLM Initialize karo (qwen/qwen3.8-27b fast and reliable)
llm = ChatGroq(
    groq_api_key=GROQ_API_KEY,
    model_name="qwen/qwen3.8-27b",
    temperature=0.3
)

output_parser = StrOutputParser()


# ==========================================
# Feature 1: Task Summary Generator
# ==========================================
def generate_task_summary(tasks: list[dict]) -> str:
    """
    User ke saare tasks lekar AI summary banata hai.
    """
    if not tasks:
        return "Abhi aapke paas koi task nahi hai! Ek naya task add karein."
    
    tasks_text = "\n".join([
        f"- {t['title']} [{'COMPLETED' if t['is_done'] else 'PENDING'}]"
        for t in tasks
    ])
    
    prompt = ChatPromptTemplate.from_messages([
        (
            "system",
            "Aap ek friendly aur smart Task Manager AI assistant ho. "
            "User ke tasks analyze karke ek crisp, structured aur motivational summary Hinglish me do. "
            "Bullet points use karo aur batao kitne pending hain aur kitne completed."
        ),
        (
            "human",
            "Ye rahe mere tasks:\n{tasks_text}\n\nMujhe summary do ki meri progress kaisi chal rahi hai."
        )
    ])
    
    chain = prompt | llm | output_parser
    return chain.invoke({"tasks_text": tasks_text})


# ==========================================
# Feature 2: Task Priority Suggestions
# ==========================================
def suggest_task_priorities(tasks: list[dict]) -> str:
    """
    Pending tasks ko analyze karke High, Medium, Low priority suggest karta hai.
    """
    pending_tasks = [t for t in tasks if not t['is_done']]
    if not pending_tasks:
        return "Shabash! Aapke saare tasks already completed hain. Enjoy karo!"
    
    tasks_text = "\n".join([f"- {t['title']}" for t in pending_tasks])
    
    prompt = ChatPromptTemplate.from_messages([
        (
            "system",
            "Aap ek productivity coach AI ho. "
            "User ke pending tasks analyze karke unhe High, Medium, aur Low priority me categorize karo "
            "aur har ek ke sath 1-line reason do Hinglish me ki pehle kya karna chahiye."
        ),
        (
            "human",
            "Ye mere pending tasks hain:\n{tasks_text}\n\nBatao mujhe pehle kaunsa task karna chahiye aur priority kya honi chahiye?"
        )
    ])
    
    chain = prompt | llm | output_parser
    return chain.invoke({"tasks_text": tasks_text})


# ==========================================
# Feature 3: Natural Language Task Extraction
# ==========================================
def extract_task_from_natural_language(user_text: str) -> str:
    """
    User ke casual Hinglish/English text se clean Todo Title nikalta hai.
    Example: 'Mujhe kal shaam 6 baje gym jana hai' -> 'Kal shaam 6 baje gym jana'
    """
    prompt = ChatPromptTemplate.from_messages([
        (
            "system",
            "Aap ek Todo Extraction AI ho. "
            "User casual Hinglish ya English me bolega ki use kya karna hai. "
            "Aapko sirf aur sirf ek clean, actionable Todo Title return karna hai bina kisi extra quotes, formatting ya unnecessary explanation ke."
        ),
        (
            "human",
            "User text: '{user_text}'\n\nClean Todo Title:"
        )
    ])
    
    chain = prompt | llm | output_parser
    res = chain.invoke({"user_text": user_text})
    return res.strip().strip('"').strip("'")

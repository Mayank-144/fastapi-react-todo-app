import os
import requests
from dotenv import load_dotenv
from sqlalchemy.orm import Session
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.tools import tool
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage, ToolMessage

import models

load_dotenv()

def get_llm():
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY is missing in your .env file.")
    return ChatGroq(
        groq_api_key=api_key,
        model_name="qwen/qwen3.8-27b",
        temperature=0.2
    )

output_parser = StrOutputParser()


# ==========================================
# Feature 1: Task Summary Generator (LCEL)
# ==========================================
def generate_task_summary(tasks: list[dict]) -> str:
    """
    Generates a structured, motivating task summary.
    Accepts tasks in English, Hindi, or Hinglish, and outputs clean, structured English.
    """
    if not tasks:
        return "You currently have no tasks in your list! Add a new task using the input box or ask the AI Assistant."
    
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
    
    chain = prompt | get_llm() | output_parser
    return chain.invoke({
        "tasks_text": tasks_text,
        "total": total,
        "done_count": done_count,
        "pending_count": pending_count
    }).strip()


# ==========================================
# Feature 2: Task Priority Suggestions (LCEL)
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
    
    chain = prompt | get_llm() | output_parser
    return chain.invoke({"tasks_text": tasks_text}).strip()


# ==========================================
# Feature 3: Natural Language Task Extraction (LCEL)
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
    
    chain = prompt | get_llm() | output_parser
    res = chain.invoke({"user_text": user_text})
    # Sanitize any accidental quotes or asterisks
    clean_title = res.strip().strip('"').strip("'").replace("**", "").replace("*", "")
    return clean_title


# ==========================================
# Weather Service Helper (OpenWeatherMap + Fallback)
# ==========================================
def fetch_live_weather(city: str) -> str:
    """
    Fetches live weather for a city using OpenWeatherMap API.
    Falls back gracefully to Open-Meteo if no API key or on error.
    """
    api_key = os.getenv("OPENWEATHERMAP_API_KEY", "").strip()
    
    # 1. Try OpenWeatherMap API if key is provided
    if api_key:
        try:
            url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
            resp = requests.get(url, timeout=6)
            if resp.status_code == 200:
                data = resp.json()
                desc = data["weather"][0]["description"].capitalize()
                temp = data["main"]["temp"]
                feels_like = data["main"]["feels_like"]
                humidity = data["main"]["humidity"]
                wind = data["wind"]["speed"]
                name = data.get("name", city)
                country = data.get("sys", {}).get("country", "")
                return (
                    f"🌤 Live Weather for {name}, {country}:\n"
                    f"• Condition: {desc}\n"
                    f"• Temperature: {temp}°C (Feels like: {feels_like}°C)\n"
                    f"• Humidity: {humidity}%\n"
                    f"• Wind Speed: {wind} m/s"
                )
        except Exception:
            pass # Fall through to fallback
            
    # 2. Fallback: Open-Meteo API (100% Free, No API key required)
    try:
        geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1&language=en&format=json"
        geo_resp = requests.get(geo_url, timeout=6)
        if geo_resp.status_code == 200:
            results = geo_resp.json().get("results", [])
            if results:
                loc = results[0]
                lat, lon = loc["latitude"], loc["longitude"]
                name, country = loc["name"], loc.get("country", "")
                
                weather_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"
                weather_resp = requests.get(weather_url, timeout=6)
                if weather_resp.status_code == 200:
                    cw = weather_resp.json().get("current_weather", {})
                    temp = cw.get("temperature")
                    wind = cw.get("windspeed")
                    return (
                        f"🌤 Live Weather for {name}, {country}:\n"
                        f"• Temperature: {temp}°C\n"
                        f"• Wind Speed: {wind} km/h\n"
                        f"• Weather Status: Available"
                    )
    except Exception as err:
        return f"Could not retrieve weather for '{city}' at this moment. Error: {str(err)}"

    return f"Could not find location or weather data for '{city}'. Please check the city name."


# ==========================================
# Feature 4: LangChain Tool-Calling Agent
# ==========================================
def run_todo_agent(
    user_message: str,
    db: Session,
    user_id: int,
    chat_history: list = None
) -> dict:
    """
    Executes the LangChain Tool-Calling Agent.
    The agent dynamically decides whether to:
    - Check live weather (using OpenWeatherMap / Open-Meteo)
    - Add a new task to the user's todo list in the database
    - Generate a smart task summary
    - Suggest task priority recommendations
    - List current user tasks
    - Or engage in friendly, conversational chat.
    """
    executed_tools = []
    created_tasks = []

    # Define Agent Tools bound to the current database session & user_id
    @tool
    def get_weather(city: str) -> str:
        """Get the live current weather report for any specified city or location worldwide."""
        executed_tools.append(f"get_weather({city})")
        return fetch_live_weather(city)

    @tool
    def add_todo_task(task_title: str) -> str:
        """Create and add a new todo task to the user's todo list. Use this whenever the user wants to add, create, or schedule a task."""
        executed_tools.append(f"add_todo_task({task_title})")
        clean_title = task_title.strip().strip('"').strip("'")
        new_todo = models.Todo(title=clean_title, is_done=False, user_id=user_id)
        db.add(new_todo)
        db.commit()
        db.refresh(new_todo)
        created_tasks.append({"id": new_todo.id, "title": new_todo.title, "is_done": new_todo.is_done})
        return f"Successfully added task: '{clean_title}' to your todo list (Task ID: {new_todo.id})."

    @tool
    def get_todo_summary() -> str:
        """Generate an intelligent overview and progress summary of all current tasks in the user's todo list."""
        executed_tools.append("get_todo_summary()")
        todos = db.query(models.Todo).filter(models.Todo.user_id == user_id).all()
        tasks_data = [{"title": t.title, "is_done": t.is_done} for t in todos]
        return generate_task_summary(tasks_data)

    @tool
    def get_priority_recommendations() -> str:
        """Analyze pending tasks and provide high, medium, and low priority recommendations."""
        executed_tools.append("get_priority_recommendations()")
        todos = db.query(models.Todo).filter(models.Todo.user_id == user_id).all()
        tasks_data = [{"title": t.title, "is_done": t.is_done} for t in todos]
        return suggest_task_priorities(tasks_data)

    @tool
    def list_todos() -> str:
        """List all current tasks and their completion status in the user's todo list."""
        executed_tools.append("list_todos()")
        todos = db.query(models.Todo).filter(models.Todo.user_id == user_id).all()
        if not todos:
            return "Your todo list is currently empty!"
        lines = [f"• {t.title} - [{'✅ Completed' if t.is_done else '⏳ Pending'}]" for t in todos]
        return "Current Tasks:\n" + "\n".join(lines)

    tools = [get_weather, add_todo_task, get_todo_summary, get_priority_recommendations, list_todos]
    tools_by_name = {t.name: t for t in tools}

    llm = get_llm()
    llm_with_tools = llm.bind_tools(tools)

    system_prompt = (
        "You are an intelligent, friendly AI Personal Assistant inside a modern Todo Application.\n"
        "You have access to specialized tools for:\n"
        "1. Live Weather checks (get_weather)\n"
        "2. Adding new tasks/todos directly into the database (add_todo_task)\n"
        "3. Generating intelligent task summaries (get_todo_summary)\n"
        "4. Analyzing and recommending task priorities (get_priority_recommendations)\n"
        "5. Listing current tasks (list_todos)\n\n"
        "LANGUAGE SUPPORT:\n"
        "- The user may speak in English, Hindi, or Hinglish.\n"
        "- Understand their request in any of these languages and provide clear, structured English responses.\n\n"
        "CRITICAL RULES:\n"
        "- When the user asks about the weather, ALWAYS call get_weather.\n"
        "- When the user asks to add or schedule a task, ALWAYS call add_todo_task.\n"
        "- When the user asks for a summary or progress report, call get_todo_summary.\n"
        "- When the user asks what to work on next or how to prioritize, call get_priority_recommendations.\n"
        "- When the user asks to see/list their tasks, call list_todos.\n"
        "- Format responses cleanly with emojis and bullet points. Avoid markdown tables."
    )

    # Build conversation messages
    messages = [SystemMessage(content=system_prompt)]

    # Add historical messages if provided
    if chat_history:
        for msg in chat_history:
            role = msg.get("role")
            content = msg.get("content", "")
            if role == "user":
                messages.append(HumanMessage(content=content))
            elif role == "assistant":
                messages.append(AIMessage(content=content))

    # Add current user prompt
    messages.append(HumanMessage(content=user_message))

    # Run agent loop (up to 5 iterations max)
    max_iterations = 5
    for _ in range(max_iterations):
        response = llm_with_tools.invoke(messages)
        messages.append(response)

        # Check if the LLM invoked any tools
        if response.tool_calls:
            for tool_call in response.tool_calls:
                tool_name = tool_call["name"]
                tool_args = tool_call["args"]
                tool_id = tool_call["id"]
                
                if tool_name in tools_by_name:
                    tool_fn = tools_by_name[tool_name]
                    tool_result = tool_fn.invoke(tool_args)
                else:
                    tool_result = f"Error: Tool '{tool_name}' not recognized."
                
                messages.append(ToolMessage(content=str(tool_result), tool_call_id=tool_id))
        else:
            # No further tool calls, agent has generated final answer
            break

    final_reply = messages[-1].content if messages else "No response generated."
    
    return {
        "reply": final_reply,
        "tools_used": list(set(executed_tools)),
        "created_tasks": created_tasks
    }

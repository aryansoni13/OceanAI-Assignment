import os
from pathlib import Path
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

# Using Gemini 2.5 Flash - latest and fastest model
LLM_MODEL = "gemini-2.5-flash"

def get_llm(api_key=None):
    """
    Returns the Gemini LLM instance.
    """
    if not api_key:
        api_key = os.environ.get("GOOGLE_API_KEY")
    
    if not api_key:
        raise ValueError("Google API Key is missing.")

    return ChatGoogleGenerativeAI(model=LLM_MODEL, temperature=0, google_api_key=api_key)

def load_prompt():
    """
    Loads the QA Architect Master Prompt.
    """
    prompt_path = Path(__file__).parent / "prompts" / "qa_architect_master.txt"
    if not prompt_path.exists():
        # Fallback or error
        raise FileNotFoundError(f"Prompt file not found at {prompt_path}")
    return prompt_path.read_text(encoding="utf-8")

def generate_test_cases(vector_store, topic: str, api_key: str):
    """
    Generates test cases based on the topic and knowledge base.
    """
    llm = get_llm(api_key)
    retriever = vector_store.as_retriever(search_kwargs={"k": 5})

    master_prompt = load_prompt()
    
    # Append specific instructions for Phase 1
    template = master_prompt + """
    
    ---
    
    ⭐ CURRENT TASK: PHASE 1 — TEST CASE GENERATION
    
    User Query / Feature: "{topic}"
    
    Context from Documentation:
    {context}
    
    Generate the test cases now, adhering strictly to the "TEST CASE OUTPUT FORMAT" and "Requirements" defined in the Master Prompt.
    """
    
    prompt = ChatPromptTemplate.from_template(template)
    
    chain = (
        {"context": retriever, "topic": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )
    
    return chain.invoke(topic)

def generate_selenium_script(vector_store, test_case: str, html_content: str, api_key: str):
    """
    Generates a Selenium script for a specific test case.
    """
    llm = get_llm(api_key)
    # We might want to retrieve context relevant to the test case as well, 
    # but the HTML content is the most critical part for the script.
    # We can also retrieve context to understand business rules if needed.
    retriever = vector_store.as_retriever(search_kwargs={"k": 3})
    
    master_prompt = load_prompt()
    
    # Append specific instructions for Phase 2
    template = master_prompt + """
    
    ---
    
    ⭐ CURRENT TASK: PHASE 2 — SELENIUM SCRIPT GENERATION
    
    Test Case to Automate:
    {test_case}
    
    Target HTML Content:
    {html_content}
    
    Additional Context (Business Rules):
    {context}
    
    Generate the Python Selenium script now, adhering strictly to the "Script Requirements" and template defined in the Master Prompt.
    """
    
    prompt = ChatPromptTemplate.from_template(template)
    
    chain = (
        {"context": retriever, "test_case": RunnablePassthrough(), "html_content": lambda x: html_content}
        | prompt
        | llm
        | StrOutputParser()
    )
    
    return chain.invoke(test_case)

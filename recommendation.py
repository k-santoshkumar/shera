# recommendation.py
from langchain.prompts import PromptTemplate #type:ignore
from langchain.chains import LLMChain #type:ignore
from langchain_openai import AzureChatOpenAI #type:ignore
from dotenv import load_dotenv #type:ignore
load_dotenv()


def generate_recommendation_response(query, history=None, model="gpt-4"):
    """
    Generate product recommendations based on client needs
    
    Args:
        query: Current user query
        history: Conversation history for context
        model: LLM model to use
    
    Returns:
        Formatted recommendation response
    """
    # Build conversation context
    context = ""
    if history:
        for message in history[-5:]:  # Use last 5 messages as context
            role = "Customer" if message["role"] == "user" else "Advisor"
            context += f"{role}: {message['content']}\n"
    
    # Create prompt template
    prompt_template = PromptTemplate.from_template(
        "You are an expert product recommender. Use this conversation history:\n"
        "{context}\n\n"
        "Current query: {query}\n\n"
        "Provide specific product recommendations with features that match the client's needs. "
        "Ask clarifying questions if needed. Format response with product names, key features, "
        "and why they match the client's requirements."
    )
    
    llm = AzureChatOpenAI(
    model="gpt-4o",
    api_version="2024-05-01-preview",
    temperature=0,
)
    # Create and run chain
    chain = LLMChain(llm=llm, prompt=prompt_template)
    response = chain.run(context=context, query=query)
    
    return response
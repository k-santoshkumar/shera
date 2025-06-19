from sklearn.metrics.pairwise import cosine_similarity #type:ignore
from langchain_openai import AzureChatOpenAI #type:ignore
from embeddings import initialize_embeddings
from config import document_chat_prompt
from langchain_core.prompts import PromptTemplate

prompt_template = PromptTemplate.from_template("Tell me a joke about {topic}")

prompt_template.invoke({"topic": "cats"})
import os
from dotenv import load_dotenv #type:ignore

load_dotenv()

def reranker_scratch(retrieved_docs: list, top_n: int, query: str) -> list:
    """Re-rank documents based on cosine similarity."""
    embeddings_poc = initialize_embeddings()
    base_new = []
    
    for doc in retrieved_docs:
        chunk_embedder = embeddings_poc.embed_query(doc.page_content)
        query_embedding = embeddings_poc.embed_query(query)
        cosine = cosine_similarity([query_embedding], [chunk_embedder])
        base_new.append({
            "document": doc,
            "cosine_score": cosine[0][0]
        })
    
    return sorted(base_new, key=lambda x: x['cosine_score'], reverse=True)[:top_n]

def generate_response(query: str, retriever) -> str:  # Now accepts single retriever
    """Generate answer using Azure OpenAI."""
    # Retrieve relevant docs - using single retriever directly
    docs = retriever.get_relevant_documents(query, k=10)
    # final = reranker_scratch(docs, top_n=5, query=query)
    
    # Prepare context
    context = "\n---\n".join([
        f"Source: {doc.metadata.get('source', 'Unknown')}\n"
        f"Content:\n{doc.page_content}"
        for doc in docs
    ])
    
    # Initialize LLM
    llm = AzureChatOpenAI(
    model="gpt4o",
    api_version="2025-01-01-preview",
    temperature=0,
) 
    
#     prompt = """
# You are a highly skilled data analyst focused on answering questions based solely on given datasets. Your specialty lies in retrieving relevant information efficiently and providing clear and concise responses formatted in Markdown.
# Your task is to answer a question based on a specific list of strings retrieved from an Excel file.
# Understand the query properly and respond to the query appropriately.
# The response should be only the answer with a well strucutred sentences in a markdown format.
# Avoid the words like "Based on the context", "From the context".
# Here are the details you need to consider:
# List of strings (context) is in a markdown table format: {context}
# Question to answer: {query}
# Make sure your response is clear, well-structured, and follows the Markdown format without any extraneous information.
# # **The response should be in a MARKDOWN format. Make the important parts of the response to bold**.
# #     Format your response with:
# #     - **Bold** for key roles
# #     - Bullet points for lists
# #     - Headers (#) for sections
# #     - If the response requires tables return the response with markdown tables.
# #     - Code blocks for any technical terms
# """ 
    
    formatted_prompt = document_chat_prompt.format(context=context, query=query)
    
    try:
        response = llm.invoke(formatted_prompt).content
        # Clean response
        response = response.replace("```markdown", "").replace("```", "")
        return response.strip()
    except Exception as e:
        raise Exception(f"Error generating response: {str(e)}")
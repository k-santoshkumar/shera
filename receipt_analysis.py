import base64
from typing import Dict, Optional, Union
from langchain_google_genai import ChatGoogleGenerativeAI #type:ignore
from dotenv import load_dotenv #type:ignore
from config import reciepts_ocr_prompt
import json
import os

load_dotenv()

def encode_image(image_path: str) -> str:
    """Encode image to base64 string."""
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Image file not found: {image_path}")
    
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")
    
def receipt_analysis(
    image_path: str,
    model: str = "gemini-2.0-flash",
    temperature: float = 0
) -> Union[Dict, str]:
    """
    Analyze a receipt image and extract structured information.
    
    Args:
        image_path: Path to the receipt image file
        prompt: Optional custom prompt
        model: Gemini model to use
        temperature: Creativity parameter (0 for deterministic)
    
    Returns:
        JSON response as dictionary or raw string if parsing fails
    """
    # Default prompt if none provided
    # default_prompt = """Extract store name, date, amounts and items from this receipt that are in Thai. 
    #     *The Output should be in a json format*. Do not make up any assumptions, if you are not sure about something, 
    #     just leave it blank. Do not add any extra information or comments."""
    
    prompt = reciepts_ocr_prompt
    
    try:
        # Encode the image
        base64_image = encode_image(image_path)
        
        # Prepare the messages structure
        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}
                    }
                ]
            }
        ]
        
        llm_gemini = ChatGoogleGenerativeAI(
            model=model,
            temperature=temperature,
            max_tokens=None,
            timeout=None,
            max_retries=2,
        )
        
        resp = llm_gemini.invoke(messages).content
        resp = resp.strip("```json").strip("```").strip()
        # Try to parse JSON if possible
        try:
            return json.loads(resp)
        except json.JSONDecodeError:
            return resp
    
    except Exception as e:
        raise Exception(f"Receipt analysis failed: {str(e)}")
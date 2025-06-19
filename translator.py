from deep_translator import GoogleTranslator #type:ignore

def translate_receipt_results(receipt_data, source_language='auto', target_language='en'):
    """
    Translates receipt aznalysis results to English using deep-translator
    
    Args:
        receipt_data: The receipt analysis result (dict or str)
        source_language: Source language code (default 'auto' for auto-detection)
        target_language: Target language code (default 'en' for English)
    
    Returns:
        Translated receipt data in the same format as input
    """
    translator = GoogleTranslator(source=source_language, target=target_language)
    
    try:
        if isinstance(receipt_data, dict):
            # Translate dictionary values recursively
            translated_dict = {}
            for key, value in receipt_data.items():
                if isinstance(value, str):
                    translated_dict[key] = translator.translate(value)
                elif isinstance(value, dict):
                    translated_dict[key] = translate_receipt_results(value, source_language, target_language)
                elif isinstance(value, list):
                    translated_dict[key] = [
                        translate_receipt_results(item, source_language, target_language) 
                        if isinstance(item, (str, dict)) else item 
                        for item in value
                    ]
                else:
                    translated_dict[key] = value
            return translated_dict
        
        elif isinstance(receipt_data, str):
            # Translate simple string
            return translator.translate(receipt_data)
        
        else:
            # Return as-is if not translatable
            return receipt_data
            
    except Exception as e:
        print(f"Translation error: {str(e)}")
        return receipt_data  # Return original if translation fails
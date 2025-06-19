import streamlit as st
from ui_utils import add_bg_from_local
from file_utils import validate_file, get_file_hash, process_file
from embeddings import update_vector_store
from llm_utils import generate_response
from web_scraper import scrape_website #type:ignore

def main():
    st.set_page_config(
        page_title="Sultante of Oman Q&A bot",
        page_icon="📊",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    add_bg_from_local(r"/Users/suppi/santosh/moi_en.png")

    # Add logo at the top left corner using columns and CSS
    # logo_path = r"/Users/suppi/santosh/WhatsApp_Image_2025-05-21_at_20.07.53-removebg-preview.png"  # Replace with your logo path
    
    # Create a container for the header
    header = st.container()
    col1, col2 = st.columns([1, 5])
    with col1:
        st.image(r"/Users/suppi/santosh/WhatsApp_Image_2025-05-21_at_20.07.53-removebg-preview.png", width=100)  # Adjust width as needed
    with col2:
        pass  # This empty column will push other content to the right

    # Rest of your existing code...

    # Initialize session state
    if "processed_files" not in st.session_state:
        st.session_state.processed_files = {}
    if "processed_urls" not in st.session_state:
        st.session_state.processed_urls = {}
    if "vector_store" not in st.session_state:
        st.session_state.vector_store = None
    if "messages" not in st.session_state:
        st.session_state.messages = [{"role": "assistant", "content": "Hello! I am Sultante of Oman chatbot. How can I help you today?"}]
    
    # Data Sources Section
    with st.sidebar:
        st.header("📂 Data Sources")
        
        # File Upload Section
        with st.expander("Upload Files", expanded=True):
            uploaded_files = st.file_uploader(
                "Upload documents",
                type=["xlsx", "xls", "pdf", "docx"],
                accept_multiple_files=True,
                help="Upload Excel, PDF, or Word documents"
            )
            
            if uploaded_files:
                for file in uploaded_files:
                    if validate_file(file):
                        file_hash = get_file_hash(file)
                        
                        if file_hash not in st.session_state.processed_files:
                            with st.spinner(f"Processing {file.name}..."):
                                try:
                                    docs = process_file(file)
                                    if docs:
                                        st.session_state.vector_store = update_vector_store(docs)
                                        st.session_state.processed_files[file_hash] = file.name
                                        st.success(f"✅ Processed: {file.name}")
                                    else:
                                        st.warning(f"⚠️ No content found in: {file.name}")
                                except Exception as e:
                                    st.error(f"❌ Failed {file.name}: {str(e)}")
                        else:
                            st.info(f"⏩ Already processed: {file.name}")
                    else:
                        st.warning(f"⚠️ Unsupported format: {file.name}")
        
        # URL Input Section
        with st.expander("Add Website URL", expanded=True):
            url = st.text_input(
                "Enter website URL to scrape",
                placeholder="https://example.com",
                help="Enter a valid URL to scrape content"
            )
            
            if url and st.button("Process URL"):
                if url not in st.session_state.processed_urls:
                    with st.spinner(f"Processing {url}..."):
                        try:
                            scraped_docs = scrape_website(url)
                            if scraped_docs:
                                st.session_state.vector_store = update_vector_store(scraped_docs)
                                st.session_state.processed_urls[url] = True
                                st.success(f"✅ Successfully scraped: {url}")
                            else:
                                st.warning("⚠️ No content found at this URL")
                        except Exception as e:
                            st.error(f"❌ Failed to scrape {url}: {str(e)}")
                else:
                    st.info(f"⏩ Already processed: {url}")

    # Interactive Q&A
    if st.session_state.vector_store:
        st.divider()
        st.title("Q&A bot")
        
        # Display chat history
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                if msg["role"] == "assistant":
                    st.markdown(msg["content"], unsafe_allow_html=True)
                else:
                    st.write(msg["content"])
        
        # User input
        if query := st.chat_input("Enter your query ..."):
            st.session_state.messages.append({"role": "user", "content": query})
            
            with st.chat_message("user"):
                st.write(query)
            
            with st.chat_message("assistant"):
                with st.spinner("Analyzing..."):
                    try:
                        # Pass the single retriever directly
                        response = generate_response(query, st.session_state.vector_store)
                        st.markdown(response, unsafe_allow_html=True)
                        st.session_state.messages.append({"role": "assistant", "content": response})
                    except Exception as e:
                        error_msg = f"Error generating response: {str(e)}"
                        st.error(error_msg)
                        st.session_state.messages.append({"role": "assistant", "content": error_msg})
    else:
        st.info("Please upload files or add a website URL to begin.")

if __name__ == "__main__":
    main()
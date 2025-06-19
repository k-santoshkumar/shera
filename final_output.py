import streamlit as st #type:ignore
from ui_utils import add_bg_from_local
from file_utils import validate_file, get_file_hash, process_file
from embeddings import update_vector_store
from llm_utils import generate_response
from web_scraper import scrape_website
from receipt_analysis import receipt_analysis
from recommendation import generate_recommendation_response
from translator import translate_receipt_results
# from document_parser import scrape_website
import tempfile
import os
from streamlit_extras.badges import badge #type:ignore

def main():
    st.set_page_config(
        page_title="Sheera",
        page_icon="📊",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    st.markdown("""
    <style>
        .stApp {
            background: transparent !important;
        }
        .mode-badge {
            padding: 4px 8px;
            border-radius: 12px;
            font-size: 0.8rem;
            font-weight: 600;
        }
        .qa-mode { background-color: #e6f2ff; color: #0068c9; }
        .receipt-mode { background-color: #e6ffe6; color: #00a854; }
        .recommend-mode { background-color: #f0e6ff; color: #7d3bed; }
        .mode-border {
            border-left: 4px solid;
            padding-left: 12px;
            background-color: rgba(255, 255, 255, 0.7);
            border-radius: 10px;
            padding: 15px;
            margin-bottom: 20px;
        }
        .qa-border { border-color: #0068c9; }
        .receipt-border { border-color: #00a854; }
        .recommend-border { border-color: #7d3bed; }
        .empty-state {
            text-align: center;
            padding: 40px;
            border-radius: 12px;
            background-color: rgba(248, 249, 250, 0);
            margin: 20px 0;
        }
        .stTabs [data-baseweb="tab-list"] {
            gap: 8px;
        }
        .stTabs [data-baseweb="tab"] {
            padding: 8px 16px;
            border-radius: 4px 4px 0 0;
            background-color: rgba(255, 255, 255, 0.7);
        }
        .stSidebar {
            background-color: rgba(255, 255, 255, 0.7) !important;
        }
        .stChatMessage {
            background-color: rgba(255, 255, 255, 0.7) !important;
        }
        .stDataFrame {
            background-color: rgba(255, 255, 255, 0.7) !important;
        }
    </style>
    """, unsafe_allow_html=True)
    ca1, ca2 = st.columns([1, 1])
    with ca1:             
        st.image(os.path.abspath("shera_logo.png"))
        # pass
    # Header with logo and mode indicator
    col1, col2 = st.columns([2,1])
    with col1:
        if "current_mode" not in st.session_state:
            st.session_state.current_mode = "qa"
            mode_title = {
                "qa": "Shera Chat",
                "receipt": "Shera Receipt Reader", 
                "recommendation": "Shera Recommender"
            }
            
            mode_color = {
                "qa": ("qa-mode", "qa-border"),
                "receipt": ("receipt-mode", "receipt-border"), 
                "recommendation": ("recommend-mode", "recommend-border")
            }
            
            st.markdown(f"""
            <div style="display: flex; align-items: center; gap: 12px;">
                <h1>{mode_title[st.session_state.current_mode]}</h1>
                <span class="mode-badge {mode_color[st.session_state.current_mode][0]}">
                    {st.session_state.current_mode.upper()}
                </span>
            </div>
            """, unsafe_allow_html=True)
    # Initialize session state
    if "processed_files" not in st.session_state:
        st.session_state.processed_files = {}
    if "processed_urls" not in st.session_state:
        st.session_state.processed_urls = {}
    if "vector_store" not in st.session_state:
        st.session_state.vector_store = None
    if "messages" not in st.session_state:
        st.session_state.messages = [{"role": "assistant", "content": "Hello! I am SHERA Chat. How can I help you today?"}]
    if "current_mode" not in st.session_state:
        st.session_state.current_mode = "qa"
    if "uploaded_receipt" not in st.session_state:
        st.session_state.uploaded_receipt = None
    if "receipt_result" not in st.session_state:
        st.session_state.receipt_result = None
    if "recommendation_history" not in st.session_state:
        st.session_state.recommendation_history = [
            {"role": "assistant", "content": "Hi! I am your SHERA Recommender for your client. How can I assist you today?"}
        ]

    # Sidebar Layout
    with st.sidebar:
        st.header("🔀 Switch Mode")
        current_mode = st.selectbox(
            "Select mode",
            ["SHERA Chat", "SHERA Receipt Reader", "SHERA Recommender"],
            index=["SHERA Chat", "SHERA Receipt Reader", "SHERA Recommender"].index(
                "SHERA Chat" if st.session_state.current_mode == "qa" 
                else "SHERA Receipt Reader" if st.session_state.current_mode == "receipt" 
                else "SHERA Recommender"
            ),
            label_visibility="collapsed"
        )
        
        new_mode = {
            "SHERA Chat": "qa",
            "SHERA Receipt Reader": "receipt",
            "SHERA Recommender": "recommendation"
        }[current_mode]
        
        if new_mode != st.session_state.current_mode:
            st.session_state.current_mode = new_mode
            st.rerun()
        
        if st.session_state.current_mode == "qa":
            st.divider()
            st.header("📂 Data Sources")
            
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
        
        # Add receipt uploader to sidebar when in receipt mode
        if st.session_state.current_mode == "receipt":
            st.divider()
            st.subheader("📄 Upload Receipt")
            uploaded_image = st.file_uploader(
                "Upload a clear photo of your receipt.",
                type=["jpg", "jpeg", "png"],
                key="receipt_uploader"
            )
             
            if uploaded_image:
                st.session_state.uploaded_receipt = uploaded_image
                st.session_state.receipt_result = None
                st.success("✅ Image uploaded successfully!")

    # Main Content Area
    # st.markdown(f'<div class="mode-border {mode_border_class}">', unsafe_allow_html=True)

    if st.session_state.current_mode == "receipt":
        # Receipt Reader Interface
        if not st.session_state.uploaded_receipt:
            with st.empty():
                with st.container():
                    st.header("SHERA Receipt Reader")
                    # st.markdown("""
                    # <div class="empty-state">
                    #     <h3>📸 Drag & Drop Receipt</h3>
                    #     <p>Upload a clear photo of your receipt to analyze</p>
                    # </div>
                    # """, unsafe_allow_html=True)
        
        # Create columns for side-by-side layout
        col1, col2 = st.columns([1, 1], gap="medium")
        
        # Display receipt preview in first column
        if st.session_state.uploaded_receipt:
            with col1:
                st.subheader("Receipt Preview")
                st.image(
                    st.session_state.uploaded_receipt,
                    caption="Uploaded Receipt",
                    use_container_width=True,
                    width=300,
                    clamp=True
                )
            
            # Auto-process on upload
            if st.session_state.receipt_result is None:
                with st.spinner("Analyzing receipt..."):
                    try:
                        with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp_file:
                            tmp_file.write(st.session_state.uploaded_receipt.getvalue())
                            tmp_path = tmp_file.name
                        
                        result = receipt_analysis(tmp_path)
                        os.unlink(tmp_path)
                        st.session_state.receipt_result = result
                    except Exception as e:
                        st.error(f"❌ Error processing receipt: {str(e)}")
        
        # Display analysis results in second column
        if st.session_state.receipt_result:
            with col2:
                st.subheader("Extracted Data Points")
                
                tab1, tab2 = st.tabs(["Original", "English Translation"])
                
                with tab1:
                    if isinstance(st.session_state.receipt_result, dict):
                        st.dataframe(st.session_state.receipt_result)
                        # st.markdown("### Detailed View")
                        for key, value in st.session_state.receipt_result.items():
                            if isinstance(value, dict):
                                st.markdown(f"**{key}**")
                                for subkey, subvalue in value.items():
                                    st.markdown(f"- {subkey}: {subvalue}")
                            else:
                                st.markdown(f"**{key}**: {value}")
                    else:
                        st.text_area("Original Result", 
                                    st.session_state.receipt_result, 
                                    height=300)
                
                with tab2:
                    translated_result = translate_receipt_results(st.session_state.receipt_result)
                    if isinstance(translated_result, dict):
                        st.dataframe(translated_result)
                        for key, value in translated_result.items():
                            if isinstance(value, dict):
                                st.markdown(f"**{key}**")
                                for subkey, subvalue in value.items():
                                    st.markdown(f"- {subkey}: {subvalue}")
                            else:
                                st.markdown(f"**{key}**: {value}")
                    else:
                        st.text_area("English Translation", 
                                    translated_result, 
                                    height=300)
                
                # Download buttons
                col_d1, col_d2 = st.columns(2)
                with col_d1:
                    st.download_button(
                        label="📥 Download Original",
                        data=str(st.session_state.receipt_result),
                        file_name="receipt_analysis_original.txt",
                        mime="text/plain"
                    )
                with col_d2:
                    st.download_button(
                        label="📥 Download English",
                        data=str(translate_receipt_results(st.session_state.receipt_result)),
                        file_name="receipt_analysis_english.txt",
                        mime="text/plain"
                    )

    elif st.session_state.current_mode == "recommendation":
        # Product Recommendation Interface
        if not st.session_state.recommendation_history or len(st.session_state.recommendation_history) <= 1:
            with st.empty():
                with st.container():
                    st.header("SHERA Recommender")
                    # columns_1, columns_2 = st.columns(2)
                    # with columns_1:
                    #     st.markdown("""
                    #     <div class="empty-state", align="left">
                    #         <h3>👋 Tell me about your client</h3>
                    #         <p>Start by describing your client's needs and preferences</p>
                    #         <div style="text-align: left; max-width: 400px; margin: 0 auto;">
                    #             <p>▸ Budget-conscious student</p>
                    #             <p>▸ Luxury business traveler</p>
                    #             <p>▸ Eco-friendly family</p>
                    #         </div>
                    #     </div>
                    #     """, unsafe_allow_html=True)
        
        for msg in st.session_state.recommendation_history:
            with st.chat_message(msg["role"]):
                if msg["role"] == "assistant":
                    st.markdown(msg["content"], unsafe_allow_html=True)
                else:
                    st.write(msg["content"])
        
        if query := st.chat_input("Describe your client's needs..."):
            st.session_state.recommendation_history.append({"role": "user", "content": query})
            
            with st.chat_message("user"):
                st.write(query)
            
            with st.chat_message("assistant"):
                with st.spinner("Finding recommendations..."):
                    try:
                        response = generate_recommendation_response(
                            query, 
                            history=st.session_state.recommendation_history
                        )
                        st.markdown(response, unsafe_allow_html=True)
                        st.session_state.recommendation_history.append({"role": "assistant", "content": response})
                    except Exception as e:
                        error_msg = f"Error generating recommendation: {str(e)}"
                        st.error(error_msg)
                        st.session_state.recommendation_history.append({"role": "assistant", "content": error_msg})
    
    else:
        # Default Q&A Interface
        if not st.session_state.vector_store:
            with st.empty():
                with st.container():
                    # st.header("SHERA CHAT")
                    cols_3, cols_4 = st.columns(2)
                    with cols_3:
                        st.markdown("""
                        <div class="empty-state">
                            <h3>📄 Upload documents to get started</h3>
                            <p>Add your files or website URLs to begin asking questions</p>
                            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 16px; max-width: 500px; margin: 20px auto;">
                                <div style="padding: 12px; background: rgba(255, 255, 255, 0.7); border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                                    <b>Sample Questions:</b>
                                    <p style="font-size: 0.9em;">▸ What are the key points?</p>
                                    <p style="font-size: 0.9em;">▸ Summarize this document</p>
                                </div>
                                <div style="padding: 12px; background: rgba(255, 255, 255, 0.7); border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                                    <b>Supported Formats:</b>
                                    <p style="font-size: 0.9em;">▸ PDF, Word, Excel</p>
                                    <p style="font-size: 0.9em;">▸ Website URLs</p>
                                </div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
        else:
            for msg in st.session_state.messages:
                with st.chat_message(msg["role"]):
                    if msg["role"] == "assistant":
                        st.markdown(msg["content"], unsafe_allow_html=True)
                    else:
                        st.write(msg["content"])
            
            if query := st.chat_input("Enter your query ..."):
                st.session_state.messages.append({"role": "user", "content": query})
                
                with st.chat_message("user"):
                    st.write(query)
                
                with st.chat_message("assistant"):
                    with st.spinner("Analyzing..."):
                        try:
                            response = generate_response(query, st.session_state.vector_store)
                            st.markdown(response, unsafe_allow_html=True)
                            st.session_state.messages.append({"role": "assistant", "content": response})
                        except Exception as e:
                            error_msg = f"Error generating response: {str(e)}"
                            st.error(error_msg)
                            st.session_state.messages.append({"role": "assistant", "content": error_msg})
    
    st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
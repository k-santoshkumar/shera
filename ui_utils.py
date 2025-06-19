import base64
import streamlit as st

def add_bg_from_local(image_file):
    with open(image_file, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode()

    st.markdown(
        f"""
        <style>
            .stMain {{
                position: relative;
                display: flex;
                justify-content: center;
            }}
            .bg-container {{
                position: fixed;
                top:0;
                width: 1100px;
                height: 600px;
                opacity: 1;
                display: flex;
                justify-content: center;
                align-items: flex-end;
            
            }}
            .bg-container img {{
                width: 50%;
                object-fit: contain;
                margin-bottom: 100px;
                opacity: 0.4;
            }}
    
            .block-container {{
                position: relative;
                
            }}
        </style>
    
        <div class="bg-container">
            <img src="data:image/png;base64,{encoded_string}" />
        </div>
        """,
        unsafe_allow_html=True
    )
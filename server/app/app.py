import streamlit as st
import requests
from typing import List
import json

# Configure the page
st.set_page_config(
    page_title="Vibe Check",
    page_icon="🌟",
    layout="centered"
)

st.title("✨ Vibe Check ✨")
st.write("Get a quick vibe check on your text or images!")

# API endpoint
API_URL = "http://127.0.0.1:8000/api/v1/query/vibe"

def get_vibe_check(text: str = None, files: List[bytes] = None) -> dict:
    """Send request to the vibe check API"""
    try:
        # Prepare the form data
        data = {}
        files_data = []
        
        if text:
            data["query"] = text
            
        if files:
            for i, file in enumerate(files):
                # Send the file with correct content type
                files_data.append(
                    ("images", ("image.jpg", file, "image/jpeg"))
                )
        
        # Make the API request
        response = requests.post(API_URL, data=data, files=files_data)
        response.raise_for_status()
        return response.json()
    
    except requests.exceptions.RequestException as e:
        st.error(f"Error communicating with the API: {str(e)}")
        return None

# User input section
text_input = st.text_area("Enter your text for a vibe check:", height=100)
uploaded_files = st.file_uploader("Upload images for vibe check (optional)", 
                                accept_multiple_files=True,
                                type=['png', 'jpg', 'jpeg'])

if st.button("Get Vibe Check! 🎯"):
    with st.spinner("Checking the vibes..."):
        # Prepare files if any were uploaded
        files = []
        if uploaded_files:
            files = [file.getvalue() for file in uploaded_files]  # Use getvalue() instead of read()
        
        # Get the vibe check
        if text_input or files:
            result = get_vibe_check(text_input, files)
            
            if result:
                st.success("Vibe check complete! 🎉")
                
                # Display the response in chat bubble style
                st.markdown("### Response:")
                
                # Handle the Gemini response format
                response_data = result.get("result", {})
                if isinstance(response_data, dict):
                    # Extract text from Gemini response structure
                    response_text = response_data.get("candidates", [])[0].get("content", {}).get("parts", [])[0].get("text", "No response received")
                else:
                    # If the response is already processed
                    response_text = str(response_data)

                bubbles = response_text.split("$endbubble")
                
                for bubble in bubbles:
                    if bubble.strip():
                        st.markdown(
                            f"""
                            <div style="
                                background-color: #e3f2fd;
                                border-radius: 15px;
                                padding: 10px;
                                margin: 5px 0;
                                max-width: 80%;
                            ">
                                {bubble.strip()}
                            </div>
                            """,
                            unsafe_allow_html=True
                        )
        else:
            st.warning("Please enter some text or upload an image to get a vibe check!")
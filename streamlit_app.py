import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

import streamlit as st
from my_agent.executor import GraphExecutor
import os
from dotenv import load_dotenv
import matplotlib
matplotlib.use('Agg')  # Set the backend to Agg
import matplotlib.pyplot as plt
import logging
import time
import re

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

print("Starting Streamlit app...")  # Debug print

def initialize_session_state():
    """Initialize session state variables"""
    print("Initializing session state...")  # Debug print
    if "messages" not in st.session_state:
        print("Creating new messages list...")  # Debug print
        st.session_state.messages = [{"role": "assistant", "content": "Hello! I'm your research assistant. I can help you research topics and create visualizations. What would you like to know?"}]
    if "executor" not in st.session_state:
        print("Creating new executor...")  # Debug print
        st.session_state.executor = GraphExecutor()

def display_chat_history():
    """Display all messages in the chat history"""
    print("Displaying chat history...")  # Debug print
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            if message["role"] == "assistant":
                st.markdown(f"🤖 Assistant: {message['content']}")
            else:
                st.markdown(message["content"])
            # If this message created a plot, display it
            if message.get("has_plot", False) and os.path.exists("uk_gdp_chart.png"):
                st.image("uk_gdp_chart.png")

def clean_content(text: str) -> str:
    """Clean up message content by removing garbage and non-relevant text."""
    # Only keep relevant sections
    relevant_markers = [
        "Based on my research",
        "The chart shows",
        "Successfully created",
        "FINAL ANSWER"
    ]
    
    for marker in relevant_markers:
        if marker in text:
            text = text[text.index(marker):]
            break
    
    # Remove any non-ASCII characters
    text = ''.join(char for char in text if ord(char) < 128)
    
    # Clean up the text
    text = text.replace('\\n', '\n')  # Convert \n to actual newlines
    text = text.replace('|', '')      # Remove table markers
    text = text.replace('undefined', '')  # Remove undefined markers
    
    # Remove multiple spaces
    text = ' '.join(text.split())
    
    return text.strip()

def format_message(content: str) -> str:
    """Format message content with proper markdown."""
    content = clean_content(content)
    
    # Convert numbered points to bullet points
    import re
    content = re.sub(r'^\d+\.\s', '• ', content, flags=re.MULTILINE)
    
    # Convert dash points to bullet points
    content = re.sub(r'^\s*-\s', '• ', content, flags=re.MULTILINE)
    
    # Add proper spacing
    paragraphs = content.split('\n')
    formatted = '\n\n'.join(p.strip() for p in paragraphs if p.strip())
    
    return formatted

def process_user_input(user_input: str):
    """Process user input and update chat"""
    logger.info(f"Processing user input: {user_input}")
    plot_displayed = False
    processed_messages = set()
    
    try:
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": user_input})

        # Show user message immediately
        with st.chat_message("user"):
            st.markdown(user_input)

        # Show "Assistant is thinking" message
        with st.chat_message("assistant"):
            thinking_placeholder = st.empty()
            thinking_placeholder.markdown("🤖 Assistant: _thinking..._")

            # Execute the graph
            events = st.session_state.executor.execute_single(user_input)
            
            for event in events:
                # Handle researcher messages
                if 'researcher' in event:
                    messages = event['researcher']['messages']
                    for msg in messages:
                        if hasattr(msg, 'content') and hasattr(msg, 'id'):
                            if msg.id in processed_messages:
                                continue
                            processed_messages.add(msg.id)
                            
                            content = msg.content
                            if isinstance(content, list):
                                content_text = ' '.join([
                                    item.get('text', '') if isinstance(item, dict) else str(item)
                                    for item in content
                                ])
                            else:
                                content_text = str(content)
                            
                            formatted_content = format_message(content_text)
                            if formatted_content:  # Only display if there's content after cleaning
                                st.markdown(f"🔍 Research: {formatted_content}")
                
                # Handle chart generator messages
                if 'chart_generator' in event:
                    messages = event['chart_generator']['messages']
                    for msg in messages:
                        if hasattr(msg, 'content') and hasattr(msg, 'id'):
                            if msg.id in processed_messages:
                                continue
                            processed_messages.add(msg.id)
                            
                            content = msg.content
                            if isinstance(content, list):
                                content_text = ' '.join([
                                    item.get('text', '') if isinstance(item, dict) else str(item)
                                    for item in content
                                ])
                            else:
                                content_text = str(content)
                            
                            formatted_content = format_message(content_text)
                            if formatted_content:  # Only display if there's content after cleaning
                                st.markdown(f"📊 Chart Generator: {formatted_content}")
                            
                            # Display plot only once
                            if not plot_displayed and os.path.exists('uk_gdp_chart.png'):
                                if 'saved plot' in content_text.lower() or 'uk_gdp_chart.png' in content_text.lower():
                                    try:
                                        st.image('uk_gdp_chart.png', 
                                               caption="UK GDP Trend (2019-2023)", 
                                               use_column_width=True)
                                        plot_displayed = True
                                        logger.info("Successfully displayed plot")
                                    except Exception as e:
                                        logger.error(f"Failed to display plot: {e}")
            
            # Clear thinking message
            thinking_placeholder.empty()
                            
    except Exception as e:
        logger.error(f"Error in process_user_input: {str(e)}", exc_info=True)
        thinking_placeholder.markdown(f"🤖 Assistant: Sorry, I encountered an error: {str(e)}")

# Add debug function
def debug_plot():
    """Debug function to check plot file"""
    plot_path = "uk_gdp_chart.png"
    if os.path.exists(plot_path):
        file_size = os.path.getsize(plot_path)
        st.sidebar.success(f"✅ Plot file exists ({file_size:,} bytes)")
        try:
            st.sidebar.image(plot_path, caption="Debug: Plot Preview", use_column_width=True)
        except Exception as e:
            st.sidebar.error(f"❌ Error displaying plot: {str(e)}")
    else:
        st.sidebar.error("❌ Plot file not found")

def main():
    print("Entering main function...")  # Debug print
    
    # Set page config
    st.set_page_config(
        page_title="Research Assistant",
        page_icon="🤖",
        layout="wide"
    )

    # Initialize session state
    initialize_session_state()

    # Sidebar configuration
    st.sidebar.title("🤖 Assistant Settings")

    # Add description and placeholder links in the sidebar
    st.sidebar.markdown("An AI research assistant that can analyze data and create visualizations")
    st.sidebar.markdown("[Documentation](https://example.com)")
    st.sidebar.markdown("[GitHub](https://github.com)")

    # Display configuration in sidebar
    st.sidebar.subheader("⚙️ Configuration")
    first_sentence = "I am a research assistant capable of finding information and creating visualizations."
    st.sidebar.write(f"📝 About: {first_sentence}")
    st.sidebar.write("🌡️ Temperature: 0.7")
    st.sidebar.write("🧠 Model: Claude-3")
    st.sidebar.write("⚠️ Disclaimer: Responses may not be 100% accurate.")

    # Add debug information in sidebar
    st.sidebar.subheader("🔍 Debug Info")
    if st.sidebar.button("Check Plot File"):
        debug_plot()

    # Main chat interface
    st.title("🤖 Research Assistant")
    st.markdown("📊 Your AI companion for research and data visualization")

    # Display chat history
    display_chat_history()

    # Chat input
    if prompt := st.chat_input("Ask me anything..."):
        print(f"Received prompt: {prompt}")  # Debug print
        process_user_input(prompt)

    # Footer
    st.markdown("---")

if __name__ == "__main__":
    print("Starting main...")  # Debug print
    main()
import streamlit as st
from typing import Optional, Dict, Any, List
import os
from dotenv import load_dotenv
from shared import init_session_state

# Load environment variables
load_dotenv()

# Check required API keys
SCRAPER_API_KEY = os.getenv("SCRAPER_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not SCRAPER_API_KEY or not OPENAI_API_KEY:
    raise ValueError("Missing required API keys. Please check your .env file.")

def main():
    """Main application function that sets up the welcome page."""
    # Ensure Streamlit uses the correct port
    os.environ['STREAMLIT_SERVER_PORT'] = '8080'
    
    st.set_page_config(
        page_title="Fiverr Gig Optimizer",
        page_icon="💡",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Initialize session state
    init_session_state()
    
    st.title("🚀 Welcome to Fiverr Gig Research & Optimization Platform")
    
    st.markdown("""
    ### Transform Your Fiverr Success with AI-Powered Insights
    
    Welcome to the most comprehensive Fiverr optimization platform. Our AI-powered tools help you:
    
    #### 🔍 Smart Keyword Research
    - Discover high-demand, low-competition keywords
    - Analyze market trends and opportunities
    - Track keyword performance metrics
    
    #### 🎯 Profile Analysis
    - Get detailed competitor insights
    - Optimize your profile for better visibility
    - Identify improvement opportunities
    
    #### ✍️ Gig Creation & Optimization
    - Generate SEO-optimized gig content
    - Create compelling packages
    - Maximize conversion potential
    
    ### 🚀 Getting Started
    
    1. Use the sidebar navigation to access different tools
    2. Start with Keyword Research to find opportunities
    3. Analyze competitor profiles for insights
    4. Create optimized gigs with AI assistance
    
    ### 💡 Pro Tips
    
    - Save promising keywords for later use
    - Monitor market trends regularly
    - Test different gig variations
    - Keep your portfolio updated
    
    ### 📈 Features
    
    - **AI-Powered Analysis**: Get deep insights with GPT-4
    - **Market Research**: Understand your competition
    - **SEO Optimization**: Rank higher in search results
    - **Smart Recommendations**: Data-driven suggestions
    - **Performance Tracking**: Monitor your progress
    """)
    
    # Display current stats
    st.markdown("### 📊 Your Stats")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Keywords History", len(st.session_state.analysis_history))
    with col2:
        st.metric("Gigs History", len(st.session_state.gig_history))

if __name__ == "__main__":
    main()

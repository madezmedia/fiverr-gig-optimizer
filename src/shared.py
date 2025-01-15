import streamlit as st
import os
import pandas as pd
from typing import Dict, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def init_session_state():
    """Initialize session state with required variables."""
    if 'state_initialized' not in st.session_state:
        # Initialize and validate API keys from environment
        st.session_state.SCRAPER_API_KEY = os.getenv("SCRAPER_API_KEY")
        if not st.session_state.SCRAPER_API_KEY:
            st.error("SCRAPER_API_KEY not found in environment. Please set it in .env file.")
            
        st.session_state.OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
        if not st.session_state.OPENAI_API_KEY:
            st.error("OPENAI_API_KEY not found in environment. Please set it in .env file.")
        else:
            # Set OpenAI API key globally
            import openai
            openai.api_key = st.session_state.OPENAI_API_KEY
            
        st.session_state.FIVERR_API_KEY = os.getenv("FIVERR_API_KEY")
        if not st.session_state.FIVERR_API_KEY:
            st.warning("FIVERR_API_KEY not found. Some features may be limited.")
        
        # Initialize state variables
        st.session_state.analysis_history = {}
        st.session_state.favorites = []
        st.session_state.generated_gigs = {}
        st.session_state.gig_history = {}
        st.session_state.search_keyword = ""
        st.session_state.selected_category = "All"
        st.session_state.selected_subcategory = "All"
        st.session_state.selected_tags = []
        st.session_state.state_initialized = True

def render_sidebar():
    """Render the shared sidebar with search and filters."""
    with st.sidebar:
        # Search Box
        st.text_input(
            "🔍 Search",
            key="search_keyword",
            placeholder="Enter keyword...",
            help="Search for gigs, profiles, or keywords"
        )
        
        # Category Filter
        st.selectbox(
            "Category",
            ["All", "Programming & Tech", "Digital Marketing", "Writing & Translation", "Design"],
            key="selected_category"
        )
        
        # Subcategory Filter (dynamic based on category)
        subcategories = {
            "Programming & Tech": ["All", "Web Development", "Mobile Apps", "Desktop Apps"],
            "Digital Marketing": ["All", "SEO", "Social Media", "Content Marketing"],
            "Writing & Translation": ["All", "Articles & Blog Posts", "Translation", "Creative Writing"],
            "Design": ["All", "Logo Design", "Web Design", "Graphic Design"]
        }
        
        if st.session_state.selected_category != "All":
            st.selectbox(
                "Subcategory",
                subcategories.get(st.session_state.selected_category, ["All"]),
                key="selected_subcategory"
            )
        
        # Tags Filter
        st.multiselect(
            "Tags",
            ["Trending", "High Demand", "Low Competition", "Best Rated", "New"],
            key="selected_tags"
        )
        
        # Stats Overview
        st.markdown("### 📊 Stats")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Keywords History", len(st.session_state.analysis_history))
        with col2:
            st.metric("Gigs History", len(st.session_state.gig_history))

def filter_results(data: Dict[str, Any]) -> Dict[str, Any]:
    """Filter results based on search and filters."""
    filtered_data = {}
    
    for k, v in data.items():
        # Skip if no category match
        if st.session_state.selected_category != "All":
            if v.get('category') != st.session_state.selected_category:
                continue
        
        # Skip if no subcategory match
        if st.session_state.selected_subcategory != "All":
            if v.get('subcategory') != st.session_state.selected_subcategory:
                continue
        
        # Skip if no tag match
        if st.session_state.selected_tags:
            if not any(tag in v.get('tags', []) for tag in st.session_state.selected_tags):
                continue
        
        # Skip if no search match
        if st.session_state.search_keyword:
            search_term = st.session_state.search_keyword.lower()
            # Search in key
            if search_term not in k.lower():
                # Search in insights if they exist
                insights = v.get('insights', {})
                if isinstance(insights, dict):
                    raw_insights = insights.get('raw_insights', '')
                    if not raw_insights or search_term not in raw_insights.lower():
                        continue
        
        filtered_data[k] = v
    
    return filtered_data

def copy_to_clipboard(text: str) -> None:
    """Copy text to clipboard and show success message."""
    try:
        st.code(text, language=None)
        st.toast("Click the copy button in the code block above!")
    except Exception as e:
        st.error(f"Failed to copy: {str(e)}")

def save_to_favorites(keyword: str) -> None:
    """Save keyword to favorites."""
    if keyword not in st.session_state.favorites:
        st.session_state.favorites.append(keyword)
        st.toast(f"Added {keyword} to favorites!")
        st.rerun()

def remove_from_favorites(keyword: str) -> None:
    """Remove keyword from favorites."""
    if keyword in st.session_state.favorites:
        st.session_state.favorites.remove(keyword)
        st.toast(f"Removed {keyword} from favorites")
        st.rerun()

def add_to_history(keyword: str, data: Dict[str, Any]) -> None:
    """Add analysis to history."""
    st.session_state.analysis_history[keyword] = data

def add_gig_to_history(keyword: str, gig_data: Dict[str, Any]) -> None:
    """Add gig to history."""
    st.session_state.gig_history[keyword] = {
        "timestamp": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S"),
        "data": gig_data,
        "category": st.session_state.selected_category,
        "subcategory": st.session_state.selected_subcategory,
        "tags": st.session_state.selected_tags
    }
    st.toast(f"Added gig for {keyword} to history!")

def add_generated_gig(keyword: str, gig_data: Dict[str, Any]) -> None:
    """Add generated gig to history."""
    st.session_state.generated_gigs[keyword] = gig_data

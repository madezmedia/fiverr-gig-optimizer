import streamlit as st
import requests
import openai
import pandas as pd
from typing import Optional, Dict, Any
import os
import json
from dotenv import load_dotenv
from state_manager import StateManager

# Initialize state manager
state_mgr = StateManager()

# Load environment variables
load_dotenv()

# Configuration and API Setup
SCRAPER_API_KEY = os.getenv("SCRAPER_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
FIVERR_API_KEY = os.getenv("FIVERR_API_KEY")

if not SCRAPER_API_KEY or not OPENAI_API_KEY:
    raise ValueError("Missing required API keys. Please check your .env file.")

# Configure OpenAI client
openai.api_key = OPENAI_API_KEY

# Initialize session state
if 'state_initialized' not in st.session_state:
    st.session_state.analysis_history = state_mgr.get_analysis_history()
    st.session_state.favorites = state_mgr.get_favorites() or []  # Ensure it's a list
    st.session_state.generated_gigs = state_mgr.get_generated_gigs()
    st.session_state.saved_gigs = state_mgr.get_saved_gigs()
    st.session_state.state_initialized = True

def sync_state():
    """Synchronize state with persistent storage."""
    try:
        state_data = {
            "favorites": list(st.session_state.favorites),
            "saved_gigs": dict(st.session_state.saved_gigs),
            "analysis_history": dict(st.session_state.analysis_history),
            "generated_gigs": dict(st.session_state.generated_gigs)
        }
        state_mgr.save_state(state_data)
    except Exception as e:
        st.error(f"Failed to sync state: {str(e)}")

def copy_to_clipboard(text: str) -> None:
    """Copy text to clipboard and show success message."""
    try:
        st.code(text, language=None)
        st.toast("Click the copy button in the code block above!")
    except Exception as e:
        st.error(f"Failed to copy: {str(e)}")

def save_to_favorites(keyword: str) -> None:
    """Save keyword to favorites and persist state."""
    try:
        if not isinstance(st.session_state.favorites, list):
            st.session_state.favorites = []
        if keyword not in st.session_state.favorites:
            st.session_state.favorites.append(keyword)
            state_mgr.add_to_favorites(keyword)
            sync_state()
            st.toast(f"Added {keyword} to favorites!")
            st.rerun()
    except Exception as e:
        st.error(f"Failed to save favorite: {str(e)}")

def remove_from_favorites(keyword: str) -> None:
    """Remove keyword from favorites and persist state."""
    try:
        if keyword in st.session_state.favorites:
            st.session_state.favorites.remove(keyword)
            state_mgr.remove_from_favorites(keyword)
            sync_state()
            st.toast(f"Removed {keyword} from favorites")
            st.rerun()
    except Exception as e:
        st.error(f"Failed to remove favorite: {str(e)}")

def save_gig(keyword: str, gig_data: Dict[str, Any]) -> None:
    """Save gig data and persist state."""
    try:
        st.session_state.saved_gigs[keyword] = gig_data
        state_mgr.save_gig(keyword, gig_data)
        sync_state()
    except Exception as e:
        st.error(f"Failed to save gig: {str(e)}")

def delete_gig(keyword: str) -> None:
    """Delete gig and persist state."""
    try:
        if keyword in st.session_state.saved_gigs:
            del st.session_state.saved_gigs[keyword]
            state_mgr.delete_gig(keyword)
            sync_state()
    except Exception as e:
        st.error(f"Failed to delete gig: {str(e)}")

def add_to_history(keyword: str, data: Dict[str, Any]) -> None:
    """Add analysis to history and persist state."""
    try:
        st.session_state.analysis_history[keyword] = data
        state_mgr.add_to_history(keyword, data)
        sync_state()
    except Exception as e:
        st.error(f"Failed to add to history: {str(e)}")

def add_generated_gig(keyword: str, gig_data: Dict[str, Any]) -> None:
    """Add generated gig to history and persist state."""
    st.session_state.generated_gigs[keyword] = gig_data
    state_mgr.add_generated_gig(keyword, gig_data)
    sync_state()

# Set up page configuration
st.set_page_config(
    page_title="Fiverr Gig Optimizer",
    page_icon="💡",
    layout="wide",
    initial_sidebar_state="expanded"
)

class FiverrGigOptimizer:
    """
    A class to handle Fiverr gig optimization operations including keyword research,
    trend analysis, and description optimization.
    """
    
    def fetch_profile_data(self, username: str) -> Optional[Dict[str, Any]]:
        """
        Fetch profile data from Fiverr API.
        
        Args:
            username (str): The Fiverr username to analyze
            
        Returns:
            Optional[Dict[str, Any]]: The profile data or None if an error occurs
        """
        try:
            # First try Fiverr API if key is available
            if FIVERR_API_KEY:
                headers = {"Authorization": f"Bearer {FIVERR_API_KEY}"}
                response = requests.get(
                    f"https://api.fiverr.com/v1/users/{username}",
                    headers=headers
                )
                response.raise_for_status()
                return response.json()
            
            # Fallback to scraping if no API key
            url = "https://async.scraperapi.com/jobs"
            payload = {
                "apiKey": SCRAPER_API_KEY,
                "url": f"https://www.fiverr.com/{username}"
            }
            response = requests.post(url, json=payload)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            st.error(f"Failed to fetch profile: {str(e)}")
            return None
    
    def fetch_user_gigs(self, username: str) -> Optional[Dict[str, Any]]:
        """
        Fetch user's gigs from Fiverr API.
        
        Args:
            username (str): The Fiverr username
            
        Returns:
            Optional[Dict[str, Any]]: The gigs data or None if an error occurs
        """
        try:
            # First try Fiverr API if key is available
            if FIVERR_API_KEY:
                headers = {"Authorization": f"Bearer {FIVERR_API_KEY}"}
                response = requests.get(
                    f"https://api.fiverr.com/v1/users/{username}/gigs",
                    headers=headers
                )
                response.raise_for_status()
                return response.json()
            
            # Fallback to scraping if no API key
            url = "https://async.scraperapi.com/jobs"
            payload = {
                "apiKey": SCRAPER_API_KEY,
                "url": f"https://www.fiverr.com/{username}/gigs"
            }
            response = requests.post(url, json=payload)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            st.error(f"Failed to fetch gigs: {str(e)}")
            return None
    
    def analyze_profile(self, username: str, profile_data: Dict[str, Any], gigs_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Analyze a Fiverr profile using OpenAI.
        
        Args:
            username (str): The Fiverr username
            profile_data (Dict[str, Any]): The profile data
            gigs_data (Dict[str, Any]): The gigs data
            
        Returns:
            Optional[Dict[str, Any]]: The analysis results or None if an error occurs
        """
        try:
            # Prepare context for analysis
            context = {
                "username": username,
                "profile_data": profile_data,
                "gigs_data": gigs_data
            }
            
            response = openai.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": """You are an expert in Fiverr profile optimization.
                    Analyze the profile and gigs data to provide insights in the following JSON format:
                    {
                        "strengths": ["string"],
                        "weaknesses": ["string"],
                        "opportunities": ["string"],
                        "optimization_suggestions": {
                            "title": "string",
                            "description": "string",
                            "portfolio": ["string"],
                            "pricing": {
                                "basic": {"price": number, "features": ["string"]},
                                "standard": {"price": number, "features": ["string"]},
                                "premium": {"price": number, "features": ["string"]}
                            }
                        },
                        "market_position": {
                            "price_percentile": number,
                            "rating_percentile": number,
                            "response_percentile": number
                        },
                        "action_items": {
                            "immediate": ["string"],
                            "short_term": ["string"],
                            "long_term": ["string"]
                        }
                    }"""},
                    {"role": "user", "content": f"Analyze this Fiverr profile data: {json.dumps(context)}"}
                ]
            )
            return json.loads(response.choices[0].message.content)
        except Exception as e:
            st.error(f"Profile analysis failed: {str(e)}")
            return None
    
    def scrape_gig_data(self, keyword: str) -> Optional[Dict[str, Any]]:
        """
        Scrape gig data from Fiverr using ScraperAPI.
        
        Args:
            keyword (str): The search keyword to scrape gigs for
            
        Returns:
            Optional[Dict[str, Any]]: The scraped gig data or None if an error occurs
        """
        url = "https://async.scraperapi.com/jobs"
        payload = {
            "apiKey": SCRAPER_API_KEY,
            "url": f"https://www.fiverr.com/search/gigs?query={keyword}"
        }
        
        try:
            response = requests.post(url, json=payload)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            st.error(f"Failed to scrape data: {str(e)}")
            return None
    
    def analyze_gig_keywords(self, keyword: str) -> Optional[Dict[str, Any]]:
        """
        Perform advanced keyword analysis using OpenAI.
        
        Args:
            keyword (str): The keyword to analyze
            
        Returns:
            Optional[Dict[str, Any]]: The analysis results or None if an error occurs
        """
        try:
            response = openai.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": """You are an expert in Fiverr gig keyword research.
                    Return your analysis in the following JSON format:
                    {
                        "related_keywords": [
                            {
                                "keyword": "string",
                                "demand": "High|Medium|Low",
                                "competition": "High|Medium|Low",
                                "price_range": "string (e.g. $50-100)"
                            }
                        ],
                        "market_analysis": {
                            "trend": "Growing|Stable|Declining",
                            "target_audience": "string",
                            "market_size": "string",
                            "top_regions": ["string"]
                        },
                        "raw_insights": "string"
                    }"""},
                    {"role": "user", "content": f"Analyze the Fiverr market for '{keyword}' services"}
                ]
            )
            return json.loads(response.choices[0].message.content)
        except Exception as e:
            st.error(f"AI Analysis failed: {str(e)}")
            return None
            
    def generate_complete_gig(self, keyword: str) -> Optional[Dict[str, Any]]:
        """
        Generate a complete gig template using OpenAI.
        
        Args:
            keyword (str): The main keyword
            
        Returns:
            Optional[Dict[str, Any]]: The gig template or None if an error occurs
        """
        try:
            # First, analyze the market to understand pricing and positioning
            market_analysis = self.analyze_gig_keywords(keyword)
            if not market_analysis:
                return None
                
            # Use the market insights to generate optimized gig content
            response = openai.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": f"""You are an expert Fiverr gig creator.
                    Use these market insights to inform your decisions:
                    - Target Audience: {market_analysis['market_analysis']['target_audience']}
                    - Market Trend: {market_analysis['market_analysis']['trend']}
                    - Market Size: {market_analysis['market_analysis']['market_size']}
                    
                    Return your response in the following JSON format:
                    {{
                        "title": "string (catchy, SEO-optimized title)",
                        "description": "string (compelling description with keywords)",
                        "search_tags": ["string (relevant keywords)"],
                        "packages": {{
                            "basic": {{"name": "string", "price": "number", "delivery_time": "number (days)", "features": ["string"], "description": "string"}},
                            "standard": {{"name": "string", "price": "number", "delivery_time": "number (days)", "features": ["string"], "description": "string"}},
                            "premium": {{"name": "string", "price": "number", "delivery_time": "number (days)", "features": ["string"], "description": "string"}}
                        }},
                        "requirements": ["string"],
                        "faq": [{{"question": "string", "answer": "string"}}],
                        "portfolio_suggestions": ["string (types of samples to showcase)"],
                        "upsell_opportunities": ["string (potential extra services)"]
                    }}"""},
                    {"role": "user", "content": f"Create a professional, high-converting Fiverr gig for '{keyword}' services"}
                ]
            )
            
            # Save the generated gig in state
            gig_template = json.loads(response.choices[0].message.content)
            add_generated_gig(keyword, {
                "template": gig_template,
                "market_analysis": market_analysis,
                "timestamp": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")
            })
            return gig_template
        except Exception as e:
            st.error(f"Gig template generation failed: {str(e)}")
            return None

def main():
    """Main application function that sets up the Streamlit interface."""
    st.title("🚀 Fiverr Gig Research & Optimization Platform")
    
    # Initialize optimizer
    optimizer = FiverrGigOptimizer()
    
    # Enhanced sidebar with better organization and state management
    with st.sidebar:
        # Quick Actions Section
        st.header("⚡ Quick Actions")
        
        # State Status
        state_status = "🟢 Connected" if st.session_state.state_initialized else "🔴 Disconnected"
        st.info(f"State Status: {state_status}")
        
        # Stats Overview
        st.markdown("### 📊 Stats")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Saved Keywords", len(st.session_state.favorites))
        with col2:
            st.metric("Saved Gigs", len(st.session_state.saved_gigs))
        
        # Quick Access to Recent Items
        if st.session_state.analysis_history:
            st.markdown("### 🕒 Recent Analyses")
            recent_analyses = dict(list(st.session_state.analysis_history.items())[-3:])
            for k, v in recent_analyses.items():
                if st.button(f"📈 {k}", help=f"Analyzed on {v['timestamp']}"):
                    st.session_state.selected_keyword = k
                    st.session_state.selected_insights = v['insights']
                    st.rerun()
        
        st.markdown("---")
        
        # Help & Documentation
        st.header("📚 Documentation")
        
        with st.expander("🎯 Getting Started", expanded=False):
            st.markdown("""
            1. **Keyword Research**
               - Enter your service keyword
               - Get AI-powered insights
               - Save promising keywords
            
            2. **Profile Optimization**
               - Analyze competitor profiles
               - Get improvement suggestions
               - Implement recommendations
            
            3. **Gig Creation**
               - Use saved keywords
               - Generate optimized content
               - Save gig templates
            """)
            
        with st.expander("💡 Pro Tips", expanded=False):
            st.markdown("""
            **Keyboard Shortcuts:**
            - `Ctrl/Cmd + Enter`: Run Analysis
            - `Ctrl/Cmd + S`: Save Current Gig
            
            **Visual Indicators:**
            - 🟢 Optimal (High Demand/Low Competition)
            - 🟡 Moderate (Medium Levels)
            - 🔴 Challenging (Low Demand/High Competition)
            
            **Best Practices:**
            - Save promising keywords for later
            - Compare multiple gig variations
            - Monitor market trends
            """)
        
        with st.expander("🔄 Cache Management", expanded=False):
            if st.button("Clear Cache", help="Reset all saved data"):
                try:
                    keys = list(st.session_state.keys())  # Create a copy of keys
                    for key in keys:
                        if key in st.session_state:  # Check if key still exists
                            del st.session_state[key]
                    state_mgr.save_state({})
                    st.rerun()
                except Exception as e:
                    st.error(f"Failed to clear cache: {str(e)}")
            
            if st.button("Export Data", help="Download all saved data as JSON"):
                state_data = {
                    "favorites": list(st.session_state.favorites),
                    "saved_gigs": st.session_state.saved_gigs,
                    "analysis_history": st.session_state.analysis_history
                }
                st.download_button(
                    "📥 Download State",
                    data=json.dumps(state_data, indent=2),
                    file_name="fiverr_gig_optimizer_data.json",
                    mime="application/json"
                )
    
    # Custom CSS for better visual hierarchy
    st.markdown("""
    <style>
    .stTabs [data-baseweb="tab-list"] {
        gap: 24px;
    }
    .stTabs [data-baseweb="tab"] {
        padding: 10px 20px;
        background-color: #f0f2f6;
        border-radius: 5px;
    }
    .stTabs [aria-selected="true"] {
        background-color: #0066cc;
        color: white;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Tabs for different functionalities
    tab1, tab2, tab3 = st.tabs(["🔍 Keyword Research", "🎯 Opportunity Unlocker", "✍️ Complete Gig Creator"])
    
    with tab1:
        st.header("🔍 Keyword Research")
        keyword = st.text_input("Enter Service Keyword", help="Enter the main keyword for your service")
        
        if st.button("Analyze Keywords", type="primary"):
            if not keyword:
                st.warning("Please enter a keyword to analyze")
                return
            
            # Initialize progress
            progress_text = "Operation in progress. Please wait."
            progress_bar = st.progress(0, text=progress_text)
            
            try:
                # Scrape gig data
                progress_bar.progress(20, text="🔍 Scraping market data...")
                gig_data = optimizer.scrape_gig_data(keyword)
                
                # Perform AI-powered keyword analysis
                progress_bar.progress(40, text="🤖 Analyzing with AI...")
                keyword_insights = optimizer.analyze_gig_keywords(keyword)
                
                # Generate complete gig
                progress_bar.progress(60, text="✨ Generating optimized gig...")
                gig_template = optimizer.generate_complete_gig(keyword)
                
                progress_bar.progress(100, text="✅ Analysis complete!")
                
                # Save analysis in history
                add_to_history(keyword, {
                    "timestamp": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "insights": keyword_insights,
                    "gig_template": gig_template
                })
            
                if keyword_insights:
                    st.success("Analysis completed!")
                    
                    try:
                        # Add market summary at the top
                        st.info(f"💡 **Market Insight**: {keyword_insights['raw_insights']}", icon="💡")
                        
                        # Create expandable section for raw insights
                        with st.expander("🔍 View Raw Analysis"):
                            st.json(keyword_insights)
                            
                        # Add history and favorites section
                        col1, col2 = st.columns(2)
                        
                        with col1, st.expander("📚 Analysis History"):
                            if st.session_state.analysis_history:
                                for k, v in st.session_state.analysis_history.items():
                                    with st.container():
                                        st.markdown(f"**{k}** - {v['timestamp']}")
                                        if st.button("🔄 Load", key=f"load_{k}"):
                                            keyword = k
                                            keyword_insights = v['insights']
                                            st.rerun()
                            else:
                                st.write("No analysis history yet")
                        
                        with col2, st.expander("⭐ Saved Keywords"):
                            if st.session_state.favorites:
                                for fav in st.session_state.favorites:
                                    col1, col2 = st.columns([5,1])
                                    col1.write(fav)
                                    if col2.button("🗑️", key=f"del_{fav}", help="Remove from favorites"):
                                        remove_from_favorites(fav)
                                        st.toast(f"Removed {fav} from favorites")
                            else:
                                st.write("No saved keywords yet. Click ⭐ to save keywords.")
                        
                        # Extract keywords and create interactive table
                        st.subheader("Related Keywords & Actions")
                        
                        # Create styled table header
                        st.markdown("""
                        <style>
                        .header-row {
                            background-color: #f0f2f6;
                            padding: 10px;
                            border-radius: 5px;
                            margin-bottom: 10px;
                        }
                        </style>
                        """, unsafe_allow_html=True)
                        
                        cols = st.columns([3, 2, 2, 2, 1, 1])
                        with st.container():
                            cols[0].markdown("<div class='header-row'>**Keyword**</div>", unsafe_allow_html=True)
                            cols[1].markdown("<div class='header-row'>**Demand**</div>", unsafe_allow_html=True)
                            cols[2].markdown("<div class='header-row'>**Competition**</div>", unsafe_allow_html=True)
                            cols[3].markdown("<div class='header-row'>**Price Range**</div>", unsafe_allow_html=True)
                            cols[4].markdown("<div class='header-row'>**Save**</div>", unsafe_allow_html=True)
                            cols[5].markdown("<div class='header-row'>**Analyze**</div>", unsafe_allow_html=True)
                        
                        # Display each keyword row with actions
                        for kw in keyword_insights["related_keywords"]:
                            cols = st.columns([3, 2, 2, 2, 1, 1])
                            # Keyword with copy button
                            with cols[0]:
                                st.write(kw["keyword"])
                                if st.button("📋", key=f"copy_{kw['keyword']}", help="Copy keyword"):
                                    copy_to_clipboard(kw['keyword'])
                            
                            # Demand with visual indicator
                            with cols[1]:
                                demand_color = {
                                    "High": "🟢",
                                    "Medium": "🟡",
                                    "Low": "🔴"
                                }.get(kw["demand"], "⚪")
                                st.write(f"{demand_color} {kw['demand']}")
                            
                            # Competition with visual indicator
                            with cols[2]:
                                comp_color = {
                                    "Low": "🟢",
                                    "Medium": "🟡",
                                    "High": "🔴"
                                }.get(kw["competition"], "⚪")
                                st.write(f"{comp_color} {kw['competition']}")
                            
                            # Price range
                            cols[3].write(kw["price_range"])
                            
                            # Save to favorites button
                            with cols[4]:
                                # Check if already in favorites
                                is_favorite = kw['keyword'] in st.session_state.favorites
                                button_text = "⭐" if not is_favorite else "★"
                                button_help = "Save to favorites" if not is_favorite else "Already saved"
                                
                                if st.button(button_text, key=f"save_{kw['keyword']}", help=button_help):
                                    if not is_favorite:
                                        save_to_favorites(kw['keyword'])
                                    else:
                                        remove_from_favorites(kw['keyword'])
                            
                            # Analyze button
                            with cols[5]:
                                button_key = f"analyze_{kw['keyword']}"
                                if st.button("📊", key=button_key, help="Analyze Trends"):
                                    st.session_state[button_key] = True
                            
                            # Show analysis if button was clicked
                            if st.session_state.get(button_key, False):
                                with st.expander(f"Advanced Analysis for '{kw['keyword']}'", expanded=True):
                                    st.info("Performing advanced analysis...")
                                    
                                    # Create tabs for different analysis aspects
                                    analysis_tabs = st.tabs([
                                        "Market Analysis",
                                        "Competitor Research",
                                        "Gig Optimization"
                                    ])
                                    
                                    with analysis_tabs[0]:
                                        market = keyword_insights["market_analysis"]
                                        
                                        # Market trend visualization
                                        trend_icon = {
                                            "Growing": "📈 Growing (Excellent Opportunity)",
                                            "Stable": "📊 Stable (Consistent Market)",
                                            "Declining": "📉 Declining (Caution Advised)"
                                        }.get(market['trend'], market['trend'])
                                        
                                        st.markdown(f"""
                                        ### Market Analysis
                                        
                                        #### 📊 Market Overview
                                        - **Trend**: {trend_icon}
                                        - **Market Size**: {market['market_size']}
                                        
                                        #### 🎯 Target Audience
                                        {market['target_audience']}
                                        
                                        #### 🌍 Top Regions
                                        """)
                                        
                                        # Display regions as chips
                                        regions_cols = st.columns(len(market['top_regions']))
                                        for i, region in enumerate(market['top_regions']):
                                            regions_cols[i].markdown(
                                                f"""<div style='background-color: #f0f2f6; 
                                                padding: 10px; border-radius: 20px; 
                                                text-align: center;'>
                                                🌍 {region}</div>""", 
                                                unsafe_allow_html=True
                                            )
                                    
                                    with analysis_tabs[1]:
                                        st.markdown("""
                                        ### Top Competitors
                                        1. Premium Providers ($150+)
                                        2. Mid-Range Services ($50-150)
                                        3. Budget Options ($20-50)
                                        """)
                                    
                                    with analysis_tabs[2]:
                                        st.markdown("### Gig Optimization Suggestions")
                                        st.info("Creating AI-powered gig template...")
                                        
                                        # Add button to generate gig
                                        if st.button("Generate Optimized Gig", key=f"generate_gig_{kw['keyword']}"):
                                            with st.spinner("Generating comprehensive gig template..."):
                                                # Load from history if available
                                                if kw['keyword'] in st.session_state.generated_gigs:
                                                    gig_template = st.session_state.generated_gigs[kw['keyword']]["template"]
                                                    st.success("Loaded from history!")
                                                else:
                                                    gig_template = optimizer.generate_complete_gig(kw['keyword'])
                                                
                                                if gig_template:
                                                    st.success("Gig template generated!")
                                                    
                                                    # Display title and description with copy buttons
                                                    col1, col2 = st.columns([6, 1])
                                                    with col1:
                                                        st.markdown("#### 🎯 Title")
                                                    with col2:
                                                        if st.button("📋", key="copy_title", help="Copy title"):
                                                            copy_to_clipboard(gig_template['title'])
                                                    st.markdown(gig_template['title'])
                                                    
                                                    col1, col2 = st.columns([6, 1])
                                                    with col1:
                                                        st.markdown("#### 📝 Description")
                                                    with col2:
                                                        if st.button("📋", key="copy_desc", help="Copy description"):
                                                            copy_to_clipboard(gig_template['description'])
                                                    st.markdown(gig_template['description'])
                                                    
                                                    # Display packages in styled containers
                                                    st.markdown("#### 💰 Packages")
                                                    pkg_cols = st.columns(3)
                                                    
                                                    for i, (pkg_name, pkg_data) in enumerate(gig_template['packages'].items()):
                                                        with pkg_cols[i]:
                                                            st.markdown(
                                                                f"""<div style='background-color: #f0f2f6; 
                                                                padding: 15px; border-radius: 10px;'>
                                                                <h4 style='text-align: center;'>{pkg_data['name']}</h4>
                                                                <h3 style='text-align: center; color: #0066cc;'>
                                                                ${pkg_data['price']}</h3>
                                                                <p style='text-align: center;'>⏱️ {pkg_data['delivery_time']} days</p>
                                                                <hr>
                                                                <p><em>{pkg_data['description']}</em></p>
                                                                {"".join(f"<p>✓ {feature}</p>" for feature in pkg_data['features'])}
                                                                </div>""",
                                                                unsafe_allow_html=True
                                                            )
                                                    
                                                    # Display search tags
                                                    st.markdown("#### 🏷️ Search Tags")
                                                    tags_cols = st.columns(4)
                                                    for i, tag in enumerate(gig_template['search_tags']):
                                                        tags_cols[i % 4].markdown(
                                                            f"""<div style='background-color: #e6f3ff; 
                                                            padding: 5px 10px; border-radius: 15px; 
                                                            text-align: center; margin: 2px;'>
                                                            #{tag}</div>""",
                                                            unsafe_allow_html=True
                                                        )
                                                    
                                                    # Display portfolio suggestions
                                                    st.markdown("#### 📸 Portfolio Suggestions")
                                                    for sugg in gig_template['portfolio_suggestions']:
                                                        st.markdown(f"- {sugg}")
                                                        
                                                    # Display upsell opportunities
                                                    st.markdown("#### 💎 Upsell Opportunities")
                                                    for upsell in gig_template['upsell_opportunities']:
                                                        st.markdown(f"- {upsell}")
                                                    
                                                    # Display requirements
                                                    st.markdown("#### ✅ Requirements")
                                                    for req in gig_template['requirements']:
                                                        st.markdown(f"- {req}")
                                                    
                                                    # Display FAQ
                                                    st.markdown("#### ❓ FAQ")
                                                    for qa in gig_template['faq']:
                                                        with st.expander(qa['question']):
                                                            st.write(qa['answer'])
                                                            
                                                    # Raw JSON data
                                                    with st.expander("🔍 View Raw JSON Data"):
                                                        st.json(gig_template)
                                            if st.button("📋 Copy JSON", key=f"copy_json_{kw['keyword']}"):
                                                copy_to_clipboard(json.dumps(gig_template, indent=2))
                    except Exception as e:
                        st.error(f"Error parsing insights: {str(e)}")
                        st.write(keyword_insights)
            except Exception as e:
                st.error(f"Analysis failed: {str(e)}")
                progress_bar.empty()
    
    with tab2:
        st.header("🎯 Opportunity Unlocker")
        
        # Profile Analysis Section
        st.subheader("1️⃣ Analyze Competitor Profile")
        username = st.text_input(
            "Enter Fiverr Username",
            help="Example: johndoe (without https://www.fiverr.com/)",
            placeholder="Enter username"
        )
        
        if st.button("Analyze Profile", type="primary"):
            if not username:
                st.warning("Please enter a Fiverr username")
                return
                
            with st.spinner("Analyzing competitor profile..."):
                try:
                    # Initialize progress
                    progress_text = "Operation in progress. Please wait."
                    progress_bar = st.progress(0, text=progress_text)
                    
                    # Fetch profile data
                    progress_bar.progress(20, text="🔍 Fetching profile data...")
                    profile_data = optimizer.fetch_profile_data(username)
                    
                    # Fetch user's gigs
                    progress_bar.progress(40, text="📦 Fetching user gigs...")
                    gigs_data = optimizer.fetch_user_gigs(username)
                    
                    # Analyze profile
                    progress_bar.progress(60, text="🤖 Analyzing profile...")
                    profile_analysis = optimizer.analyze_profile(username, profile_data, gigs_data)
                    
                    # Save data to JSON
                    analysis_data = {
                        "timestamp": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "username": username,
                        "profile_data": profile_data,
                        "gigs_data": gigs_data,
                        "analysis": profile_analysis
                    }
                    
                    # Add to history
                    add_to_history(username, analysis_data)
                    
                    progress_bar.progress(100, text="✅ Analysis complete!")
                    
                    # Display Results
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("### 💪 Profile Strengths")
                        strengths = [
                            "Professional presentation",
                            "Clear value proposition",
                            "Strong portfolio",
                            "Competitive pricing",
                            "Quick response time"
                        ]
                        for strength in strengths:
                            st.markdown(f"✓ {strength}")
                    
                    with col2:
                        st.markdown("### 🎯 Improvement Areas")
                        improvements = [
                            "Keyword optimization",
                            "Service packaging",
                            "Upsell opportunities",
                            "Profile description",
                            "Portfolio organization"
                        ]
                        for improvement in improvements:
                            st.markdown(f"➤ {improvement}")
                    
                    # Detailed Analysis Sections
                    st.markdown("### 📊 Detailed Analysis")
                    
                    analysis_tabs = st.tabs([
                        "🎨 Profile Optimization",
                        "💼 Service Offerings",
                        "📈 Market Position"
                    ])
                    
                    with analysis_tabs[0]:
                        st.markdown("#### Profile Enhancement Suggestions")
                        st.info("AI-powered profile optimization recommendations")
                        
                        # Profile Title
                        st.markdown("##### 🎯 Profile Title")
                        current_title = "Current: Professional Web Developer | Full Stack Expert"
                        optimized_title = "Optimized: Senior Full Stack Developer | React, Node.js Expert | 5⭐ Rated"
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            st.markdown("**Current Title:**")
                            st.markdown(f"```{current_title}```")
                        with col2:
                            st.markdown("**Optimized Title:**")
                            st.markdown(f"```{optimized_title}```")
                            if st.button("📋 Copy Title"):
                                st.toast("Optimized title copied!")
                        
                        # Description Optimization
                        st.markdown("##### 📝 Profile Description")
                        st.markdown("""
                        **Key Elements to Include:**
                        1. Professional background
                        2. Core expertise areas
                        3. Achievement highlights
                        4. Unique value proposition
                        5. Call to action
                        """)
                        
                        if st.button("Generate Optimized Description"):
                            with st.spinner("Generating optimized profile description..."):
                                st.success("Description generated!")
                                st.markdown("""
                                ```
                                🚀 Senior Full Stack Developer with 8+ years of experience
                                
                                ✓ Specialized in React, Node.js, and Cloud Architecture
                                ✓ Delivered 200+ successful projects
                                ✓ Maintained 5-star rating across 150+ reviews
                                ✓ Featured in Fiverr's Pro Network
                                
                                Let's discuss how I can help bring your vision to life!
                                ```
                                """)
                                if st.button("📋 Copy Description"):
                                    st.toast("Optimized description copied!")
                    
                    with analysis_tabs[1]:
                        st.markdown("#### Service Package Analysis")
                        
                        # Package Comparison
                        packages = {
                            "current": {
                                "basic": {"price": 50, "delivery": 3},
                                "standard": {"price": 100, "delivery": 5},
                                "premium": {"price": 200, "delivery": 7}
                            },
                            "suggested": {
                                "basic": {"price": 75, "delivery": 4},
                                "standard": {"price": 150, "delivery": 6},
                                "premium": {"price": 300, "delivery": 8}
                            }
                        }
                        
                        st.markdown("##### 💰 Package Optimization")
                        pkg_cols = st.columns(3)
                        
                        for i, (pkg_name, pkg_data) in enumerate([
                            ("Basic", packages["suggested"]["basic"]),
                            ("Standard", packages["suggested"]["standard"]),
                            ("Premium", packages["suggested"]["premium"])
                        ]):
                            with pkg_cols[i]:
                                st.markdown(
                                    f"""<div style='background-color: #f0f2f6; 
                                    padding: 15px; border-radius: 10px; text-align: center;'>
                                    <h4>{pkg_name}</h4>
                                    <h3 style='color: #0066cc;'>${pkg_data['price']}</h3>
                                    <p>⏱️ {pkg_data['delivery']} days</p>
                                    <p style='color: #28a745;'>+{int((pkg_data['price'] - packages['current'][pkg_name.lower()]['price']) / packages['current'][pkg_name.lower()]['price'] * 100)}% price optimization</p>
                                    </div>""",
                                    unsafe_allow_html=True
                                )
                    
                    with analysis_tabs[2]:
                        st.markdown("#### Market Position Analysis")
                        
                        # Competition Analysis
                        st.markdown("##### 🎯 Market Position")
                        position_data = {
                            "price_percentile": 75,
                            "rating_percentile": 90,
                            "response_percentile": 85
                        }
                        
                        metrics_cols = st.columns(3)
                        with metrics_cols[0]:
                            st.metric("Price Position", f"{position_data['price_percentile']}th percentile", "Top 25%")
                        with metrics_cols[1]:
                            st.metric("Rating Position", f"{position_data['rating_percentile']}th percentile", "Top 10%")
                        with metrics_cols[2]:
                            st.metric("Response Time", f"{position_data['response_percentile']}th percentile", "Top 15%")
                        
                        # Market Opportunities
                        st.markdown("##### 💡 Growth Opportunities")
                        opportunities = [
                            "Expand service offerings to include trending technologies",
                            "Introduce specialized packages for enterprise clients",
                            "Create productized service bundles",
                            "Develop long-term maintenance packages",
                            "Offer complementary consultation services"
                        ]
                        
                        for opp in opportunities:
                            st.markdown(f"🎯 {opp}")
                    
                    # Action Plan
                    st.markdown("### 📋 Action Plan")
                    action_items = [
                        ("Immediate", ["Update profile title", "Optimize description", "Reorganize portfolio"]),
                        ("Short-term", ["Adjust package pricing", "Add new service offerings", "Improve response time"]),
                        ("Long-term", ["Develop case studies", "Create service bundles", "Build client relationships"])
                    ]
                    
                    for timeline, items in action_items:
                        with st.expander(f"**{timeline} Actions**"):
                            for item in items:
                                st.markdown(f"✓ {item}")
                    
                except Exception as e:
                    st.error(f"Analysis failed: {str(e)}")
                    progress_bar.empty()
    
    with tab3:
        st.header("✍️ Complete Gig Creator")
        
        # Add options to load from saved keywords or enter new one
        st.subheader("1️⃣ Select Keyword")
        keyword_source = st.radio(
            "Choose keyword source",
            ["Saved Keywords", "Enter New Keyword"],
            horizontal=True
        )
        
        if keyword_source == "Saved Keywords":
            if st.session_state.favorites:
                selected_keyword = st.selectbox(
                    "Select from saved keywords",
                    list(st.session_state.favorites)
                )
            else:
                st.warning("No saved keywords found. Please save some keywords from the Keyword Research tab first.")
                selected_keyword = None
        else:
            selected_keyword = st.text_input("Enter keyword for your gig")
        
        if selected_keyword:
            st.subheader("2️⃣ Generate Gig Content")
            
            # Load from history if available
            if selected_keyword in st.session_state.generated_gigs:
                st.info("Previous gig template found! You can generate a new one or use the saved version.")
                if st.button("Load Saved Template"):
                    gig_template = st.session_state.generated_gigs[selected_keyword]["template"]
                    st.success("Loaded from history!")
            
            if st.button("Generate New Gig Template", type="primary"):
                with st.spinner("Creating comprehensive gig template..."):
                    gig_template = optimizer.generate_complete_gig(selected_keyword)
                    
                    if gig_template:
                        st.success("Gig template generated successfully!")
                        
                        # Save button
                        if st.button("💾 Save Gig"):
                            gig_data = {
                                "template": gig_template,
                                "timestamp": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")
                            }
                            save_gig(selected_keyword, gig_data)
                            # Cache the state immediately
                            state_mgr.save_state({
                                "favorites": list(st.session_state.favorites),
                                "saved_gigs": st.session_state.saved_gigs,
                                "analysis_history": st.session_state.analysis_history,
                                "generated_gigs": st.session_state.generated_gigs
                            })
                            st.success(f"Gig saved! You can find it in the 'Saved Gigs' section.")
                        
                        # Display sections with copy buttons
                        sections = [
                            ("🎯 Title", gig_template['title']),
                            ("📝 Description", gig_template['description']),
                            ("🏷️ Search Tags", ", ".join(gig_template['search_tags']))
                        ]
                        
                        for section_title, content in sections:
                            col1, col2 = st.columns([6, 1])
                            with col1:
                                st.markdown(f"#### {section_title}")
                            with col2:
                                if st.button("📋", key=f"copy_{section_title}", help=f"Copy {section_title}"):
                                    copy_to_clipboard(content)
                            st.markdown(content)
                            st.markdown("---")
                        
                        # Display packages in styled containers
                        st.markdown("#### 💰 Packages")
                        pkg_cols = st.columns(3)
                        
                        for i, (pkg_name, pkg_data) in enumerate(gig_template['packages'].items()):
                            with pkg_cols[i]:
                                st.markdown(
                                    f"""<div style='background-color: #f0f2f6; 
                                    padding: 15px; border-radius: 10px;'>
                                    <h4 style='text-align: center;'>{pkg_data['name']}</h4>
                                    <h3 style='text-align: center; color: #0066cc;'>
                                    ${pkg_data['price']}</h3>
                                    <p style='text-align: center;'>⏱️ {pkg_data['delivery_time']} days</p>
                                    <hr>
                                    <p><em>{pkg_data['description']}</em></p>
                                    {"".join(f"<p>✓ {feature}</p>" for feature in pkg_data['features'])}
                                    </div>""",
                                    unsafe_allow_html=True
                                )
                        
                        # Additional sections
                        sections = [
                            ("📸 Portfolio Suggestions", gig_template['portfolio_suggestions']),
                            ("💎 Upsell Opportunities", gig_template['upsell_opportunities']),
                            ("✅ Requirements", gig_template['requirements'])
                        ]
                        
                        for section_title, items in sections:
                            st.markdown(f"#### {section_title}")
                            for item in items:
                                st.markdown(f"- {item}")
                            st.markdown("---")
                        
                        # FAQ section
                        st.markdown("#### ❓ FAQ")
                        for qa in gig_template['faq']:
                            with st.expander(qa['question']):
                                st.write(qa['answer'])
                        
                        # Raw JSON data
                        with st.expander("🔍 View Raw JSON Data"):
                            st.json(gig_template)
                            if st.button("📋 Copy JSON"):
                                copy_to_clipboard(json.dumps(gig_template, indent=2))
        
        # Saved Gigs Section
        st.markdown("---")
        st.subheader("📚 Saved Gigs")
        if st.session_state.saved_gigs:
            for kw, gig_data in st.session_state.saved_gigs.items():
                with st.expander(f"{kw} - {gig_data['timestamp']}"):
                    st.json(gig_data['template'])
                    col1, col2 = st.columns([6, 1])
                    with col2:
                        if st.button("🗑️", key=f"del_gig_{kw}", help="Delete gig"):
                            delete_gig(kw)
                            st.toast(f"Deleted gig for {kw}")
        else:
            st.info("No saved gigs yet. Generate and save some gigs to see them here!")

if __name__ == "__main__":
    main()

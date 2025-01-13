import streamlit as st
import openai
import requests
from openrouter import OpenRouter
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans

# Configuration and API Setup
SCRAPER_API_KEY = "aa6ab9d35128f4e0ca7cfb1cdeae28b1"
OPENROUTER_API_KEY = "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"

# Set up page configuration
st.set_page_config(page_title="Fiverr Gig Optimizer", page_icon="💡", layout="wide")

# Main Application Class
class FiverrGigOptimizer:
    def __init__(self):
        # Initialize OpenRouter client
        self.openrouter_client = OpenRouter(api_key=OPENROUTER_API_KEY)
    
    def scrape_gig_data(self, keyword):
        """Scrape gig data using ScraperAPI"""
        url = "https://async.scraperapi.com/jobs"
        payload = {
            "apiKey": SCRAPER_API_KEY,
            "url": f"https://www.fiverr.com/search/gigs?query={keyword}"
        }
        
        try:
            response = requests.post(url, json=payload)
            return response.json()
        except Exception as e:
            st.error(f"Scraping error: {e}")
            return None
    
    def analyze_gig_keywords(self, keyword):
        """Advanced keyword analysis using DeepSeek AI"""
        try:
            response = self.openrouter_client.chat.completions.create(
                model="deepseek/deepseek-chat",
                messages=[
                    {"role": "system", "content": "You are an expert in Fiverr gig keyword research."},
                    {"role": "user", "content": f"Provide a comprehensive keyword analysis for '{keyword}', including:"\
                        "1. Related sub-keywords\n2. Market demand estimation\n3. Competition level\n4. Potential pricing strategies"}
                ]
            )
            return response.choices[0].message.content
        except Exception as e:
            st.error(f"AI Analysis Error: {e}")
            return None
    
    def optimize_gig_description(self, current_description):
        """AI-powered gig description optimization"""
        try:
            response = self.openrouter_client.chat.completions.create(
                model="deepseek/deepseek-chat",
                messages=[
                    {"role": "system", "content": "You are a professional Fiverr gig description optimizer."},
                    {"role": "user", "content": f"Optimize this gig description to improve visibility and conversion:\n{current_description}"}
                ]
            )
            return response.choices[0].message.content
        except Exception as e:
            st.error(f"Optimization Error: {e}")
            return None

# Streamlit App Interface
def main():
    st.title("🚀 Fiverr Gig Research & Optimization Platform")
    
    # Initialize optimizer
    optimizer = FiverrGigOptimizer()
    
    # Tabs for different functionalities
    tab1, tab2, tab3 = st.tabs(["Keyword Research", "Gig Trend Analysis", "Gig Description Optimizer"])
    
    with tab1:
        st.header("🔍 Keyword Research")
        keyword = st.text_input("Enter Service Keyword")
        
        if st.button("Analyze Keywords"):
            with st.spinner("Analyzing keywords..."):
                # Scrape gig data
                gig_data = optimizer.scrape_gig_data(keyword)
                
                # Perform AI-powered keyword analysis
                keyword_insights = optimizer.analyze_gig_keywords(keyword)
                
                # Display results
                st.subheader("Keyword Insights")
                st.write(keyword_insights)
    
    with tab2:
        st.header("📈 Gig Trend Analysis")
        category = st.selectbox("Select Category", [
            "Graphics & Design", 
            "Digital Marketing", 
            "Writing & Translation", 
            "Programming & Tech"
        ])
        
        if st.button("Analyze Trends"):
            st.info("Trend analysis in progress...")
    
    with tab3:
        st.header("✍️ Gig Description Optimizer")
        current_description = st.text_area("Paste Your Current Gig Description")
        
        if st.button("Optimize Description"):
            with st.spinner("Optimizing description..."):
                optimized_description = optimizer.optimize_gig_description(current_description)
                
                st.subheader("Optimized Description")
                st.write(optimized_description)

if __name__ == "__main__":
    main()
import streamlit as st
import pandas as pd
from typing import Dict, Any, Optional
import json
from shared import (
    init_session_state, render_sidebar, copy_to_clipboard,
    add_gig_to_history, add_generated_gig, filter_results
)
from optimizer import FiverrGigOptimizer

def generate_gig_content(optimizer: FiverrGigOptimizer, keyword: str) -> Optional[Dict[str, Any]]:
    """Generate comprehensive gig content with enhanced AI analysis."""
    try:
        # Initialize progress
        progress_text = "Operation in progress. Please wait."
        progress_bar = st.progress(0, text=progress_text)
        
        # Step 1: Analyze market and competition
        progress_bar.progress(20, text="🔍 Analyzing market...")
        market_data = optimizer.scrape_gig_data(keyword)
        
        # Step 2: Analyze keywords and categories
        progress_bar.progress(40, text="🎯 Analyzing keywords...")
        gig_titles = [gig.get('title', '') for gig in market_data.get('raw_data', {}).get('gigs', [])]
        gig_descriptions = [gig.get('description', '') for gig in market_data.get('raw_data', {}).get('gigs', [])]
        category_analysis = optimizer._analyze_categories(gig_titles, gig_descriptions)
        
        # Step 3: Generate optimized gig
        progress_bar.progress(60, text="✨ Generating gig content...")
        gig_template = optimizer.generate_complete_gig(keyword)
        
        if not gig_template:
            return None
        
        # Step 4: Enhance with trend analysis
        progress_bar.progress(80, text="📈 Analyzing trends...")
        trend_analysis = optimizer._analyze_trends(
            category_analysis.get('primary_category', ''),
            gig_template.get('search_tags', [])
        )
        
        # Combine all data
        gig_data = {
            "template": gig_template,
            "market_analysis": market_data,
            "category_analysis": category_analysis,
            "trend_analysis": trend_analysis,
            "timestamp": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S"),
            "category": st.session_state.selected_category,
            "subcategory": st.session_state.selected_subcategory,
            "tags": st.session_state.selected_tags
        }
        
        # Save to generated gigs
        add_generated_gig(keyword, gig_data)
        
        progress_bar.progress(100, text="✅ Generation complete!")
        
        return gig_data
        
    except Exception as e:
        st.error(f"Gig generation failed: {str(e)}")
        if progress_bar:
            progress_bar.empty()
        return None

def display_gig_content(keyword: str, gig_data: Dict[str, Any]):
    """Display comprehensive gig content with enhanced insights."""
    st.success("Gig content generated successfully!")
    
    # Save button
    if st.button("💾 Save Gig"):
        add_gig_to_history(keyword, gig_data)
        st.success(f"Gig saved! You can find it in the 'Gig History' section.")
    
    # Overview
    st.header("📊 Gig Overview")
    
    # Category and Market Fit
    category_analysis = gig_data["category_analysis"]
    st.info(f"Primary Category: {category_analysis['primary_category']}")
    
    # Market Fit Score
    score = category_analysis["category_fit_score"]
    score_color = "🟢" if score >= 8 else "🟡" if score >= 6 else "🔴"
    st.metric("Category Fit Score", f"{score_color} {score}/10")
    
    # Content Tabs
    content_tabs = st.tabs([
        "📝 Gig Content",
        "🎯 Keywords & SEO",
        "💰 Packages",
        "📈 Market Analysis"
    ])
    
    with content_tabs[0]:
        st.subheader("Gig Content")
        
        # Title
        st.markdown("### 🎯 Title")
        col1, col2 = st.columns([6, 1])
        with col1:
            st.code(gig_data["template"]["title"])
        with col2:
            if st.button("📋", key="copy_title", help="Copy title"):
                copy_to_clipboard(gig_data["template"]["title"])
        
        # Description
        st.markdown("### 📝 Description")
        col1, col2 = st.columns([6, 1])
        with col1:
            st.markdown(gig_data["template"]["description"])
        with col2:
            if st.button("📋", key="copy_desc", help="Copy description"):
                copy_to_clipboard(gig_data["template"]["description"])
        
        # Requirements
        st.markdown("### ✅ Requirements")
        for req in gig_data["template"]["requirements"]:
            st.markdown(f"- {req}")
        
        # FAQ
        st.markdown("### ❓ FAQ")
        for qa in gig_data["template"]["faq"]:
            with st.expander(qa["question"]):
                st.write(qa["answer"])
    
    with content_tabs[1]:
        st.subheader("Keywords & SEO")
        
        # Search Tags
        st.markdown("### 🏷️ Search Tags")
        tags_cols = st.columns(4)
        for i, tag in enumerate(gig_data["template"]["search_tags"]):
            tags_cols[i % 4].markdown(
                f"""<div style='background-color: #e6f3ff; 
                padding: 5px 10px; border-radius: 15px; 
                text-align: center; margin: 2px;'>
                #{tag}</div>""",
                unsafe_allow_html=True
            )
        
        # Keyword Clusters
        st.markdown("### 🎯 Keyword Clusters")
        for cluster in category_analysis["keyword_clusters"]:
            with st.expander(f"Topic: {cluster['topic']}"):
                for keyword in cluster["keywords"]:
                    st.markdown(f"- {keyword}")
        
        # Suggested Categories
        st.markdown("### 📂 Suggested Categories")
        for category in category_analysis["suggested_categories"]:
            st.markdown(f"- {category}")
    
    with content_tabs[2]:
        st.subheader("Package Structure")
        
        # Display packages in styled containers
        pkg_cols = st.columns(3)
        for i, (pkg_name, pkg_data) in enumerate(gig_data["template"]["packages"].items()):
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
        
        # Upsell Opportunities
        st.markdown("### 💎 Upsell Opportunities")
        for upsell in gig_data["template"]["upsell_opportunities"]:
            st.markdown(f"- {upsell}")
    
    with content_tabs[3]:
        st.subheader("Market Analysis")
        
        # Trend Analysis
        trend_data = gig_data["trend_analysis"]
        
        # Market Direction
        trend_icon = {
            "Growing": "📈",
            "Stable": "📊",
            "Declining": "📉"
        }.get(trend_data["trend_direction"], "📊")
        
        st.markdown(f"""
        ### 📈 Market Trends
        - Direction: {trend_icon} {trend_data['trend_direction']}
        - Market Size: {trend_data['market_size']}
        - Growth Rate: {trend_data['growth_rate']}
        """)
        
        # Seasonal Factors
        with st.expander("🗓️ Seasonal Factors"):
            for factor in trend_data["seasonal_factors"]:
                st.markdown(f"- {factor}")
        
        # Opportunities and Threats
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("### 💡 Emerging Opportunities")
            for opp in trend_data["emerging_opportunities"]:
                st.markdown(f"- {opp}")
        
        with col2:
            st.markdown("### ⚠️ Threat Factors")
            for threat in trend_data["threat_factors"]:
                st.markdown(f"- {threat}")
        
        # Portfolio Suggestions
        st.markdown("### 📸 Portfolio Suggestions")
        for sugg in gig_data["template"]["portfolio_suggestions"]:
            st.markdown(f"- {sugg}")

def main():
    """Main function for the gig creator page."""
    # Initialize session state and render sidebar
    init_session_state()
    render_sidebar()
    
    st.title("✍️ Complete Gig Creator")
    
    # Keyword Source Selection
    st.subheader("1️⃣ Select Keyword")
    keyword_source = st.radio(
        "Choose keyword source",
        ["Saved Keywords", "Enter New Keyword"],
        horizontal=True
    )
    
    selected_keyword = None
    
    if keyword_source == "Saved Keywords":
        if st.session_state.favorites:
            selected_keyword = st.selectbox(
                "Select from saved keywords",
                list(st.session_state.favorites)
            )
        else:
            st.warning("No saved keywords found. Please save some keywords from the Keyword Research tab first.")
    else:
        selected_keyword = st.text_input("Enter keyword for your gig")
    
    if selected_keyword:
        st.subheader("2️⃣ Generate Gig Content")
        
        # Check for existing template
        if selected_keyword in st.session_state.generated_gigs:
            st.info("Previous gig template found! You can generate a new one or use the saved version.")
            if st.button("Load Saved Template"):
                gig_data = st.session_state.generated_gigs[selected_keyword]
                st.success("Loaded from history!")
                display_gig_content(selected_keyword, gig_data)
        
        if st.button("Generate New Gig Template", type="primary"):
            optimizer = FiverrGigOptimizer()
            gig_data = generate_gig_content(optimizer, selected_keyword)
            
            if gig_data:
                display_gig_content(selected_keyword, gig_data)
    
    # Gig History Section
    st.markdown("---")
    st.subheader("📚 Gig History")
    
    if st.session_state.gig_history:
        filtered_history = filter_results(st.session_state.gig_history)
        
        if filtered_history:
            for kw, gig_data in filtered_history.items():
                with st.expander(f"{kw} - {gig_data['timestamp']}"):
                    # Display category and tags if available
                    if "category" in gig_data:
                        st.info(f"Category: {gig_data['category']} | Subcategory: {gig_data['subcategory']}")
                        if gig_data['tags']:
                            st.markdown("**Tags:** " + ", ".join(gig_data['tags']))
                    
                    # Display template data
                    st.json(gig_data["data"]["template"])
                    
                    # Regenerate button
                    if st.button("🔄 Regenerate", key=f"regen_{kw}", help="Generate new gig"):
                        optimizer = FiverrGigOptimizer()
                        new_gig_data = generate_gig_content(optimizer, kw)
                        if new_gig_data:
                            display_gig_content(kw, new_gig_data)
        else:
            st.info("No matching gigs found with current filters")
    else:
        st.info("No gigs in history yet. Generate some gigs to see them here!")

if __name__ == "__main__":
    main()

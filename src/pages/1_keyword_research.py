import streamlit as st
import pandas as pd
from typing import Dict, Any, Optional
import json
from shared import (
    init_session_state, render_sidebar, copy_to_clipboard,
    save_to_favorites, remove_from_favorites, add_to_history,
    filter_results, add_generated_gig
)
from optimizer import FiverrGigOptimizer

def analyze_keyword_data(optimizer: FiverrGigOptimizer, keyword: str) -> Optional[Dict[str, Any]]:
    """Analyze keyword data and return insights."""
    try:
        # Initialize progress
        progress_text = "Operation in progress. Please wait."
        progress_bar = st.progress(0, text=progress_text)
        
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
        
        # Save analysis in history with category metadata
        analysis_data = {
            "timestamp": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S"),
            "insights": keyword_insights,
            "gig_template": gig_template,
            "category": st.session_state.selected_category,
            "subcategory": st.session_state.selected_subcategory,
            "tags": st.session_state.selected_tags
        }
        add_to_history(keyword, analysis_data)
        
        return keyword_insights
        
    except Exception as e:
        st.error(f"Analysis failed: {str(e)}")
        if progress_bar:
            progress_bar.empty()
        return None

def display_keyword_insights(keyword: str, keyword_insights: Dict[str, Any]):
    """Display keyword analysis insights."""
    st.success("Analysis completed!")
    
    # Market summary at the top
    st.info(f"💡 **Market Insight**: {keyword_insights['raw_insights']}", icon="💡")
    
    # Raw analysis in expandable section
    with st.expander("🔍 View Raw Analysis"):
        st.json(keyword_insights)
    
    # Related Keywords Table
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
            if st.button("📊", key=f"analyze_{kw['keyword']}", help="Analyze Trends"):
                display_trend_analysis(kw['keyword'], keyword_insights)

def display_trend_analysis(keyword: str, keyword_insights: Dict[str, Any]):
    """Display detailed trend analysis for a keyword."""
    with st.expander(f"Advanced Analysis for '{keyword}'", expanded=True):
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
            if st.button("Generate Optimized Gig", key=f"generate_gig_{keyword}"):
                with st.spinner("Generating comprehensive gig template..."):
                    # Load from history if available
                    if keyword in st.session_state.generated_gigs:
                        gig_template = st.session_state.generated_gigs[keyword]["template"]
                        st.success("Loaded from history!")
                    else:
                        optimizer = FiverrGigOptimizer()
                        gig_template = optimizer.generate_complete_gig(keyword)
                    
                    if gig_template:
                        st.success("Gig template generated!")
                        display_gig_template(gig_template)

def display_gig_template(gig_template: Dict[str, Any]):
    """Display the generated gig template."""
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
    
    # Display additional sections
    sections = [
        ("📸 Portfolio Suggestions", gig_template['portfolio_suggestions']),
        ("💎 Upsell Opportunities", gig_template['upsell_opportunities']),
        ("✅ Requirements", gig_template['requirements'])
    ]
    
    for section_title, items in sections:
        st.markdown(f"#### {section_title}")
        for item in items:
            st.markdown(f"- {item}")
    
    # Display FAQ
    st.markdown("#### ❓ FAQ")
    for qa in gig_template['faq']:
        with st.expander(qa['question']):
            st.write(qa['answer'])
    
    # Raw JSON data
    with st.expander("🔍 View Raw JSON Data"):
        st.json(gig_template)
        if st.button("📋 Copy JSON"):
            copy_to_clipboard(json.dumps(gig_template, indent=2))

def main():
    """Main function for the keyword research page."""
    # Initialize session state and render sidebar
    init_session_state()
    render_sidebar()
    
    st.title("🔍 Keyword Research")
    
    # Get keyword from search box in sidebar
    keyword = st.session_state.search_keyword
    
    if st.button("Analyze Keywords", type="primary"):
        if not keyword:
            st.warning("Please enter a keyword in the search box")
            return
        
        optimizer = FiverrGigOptimizer()
        keyword_insights = analyze_keyword_data(optimizer, keyword)
        
        if keyword_insights:
            display_keyword_insights(keyword, keyword_insights)
    
    # Display filtered history
    if st.session_state.analysis_history:
        st.markdown("### 📚 Analysis History")
        filtered_history = filter_results(st.session_state.analysis_history)
        
        if filtered_history:
            for k, v in filtered_history.items():
                with st.expander(f"**{k}** - {v['timestamp']}"):
                    if 'insights' in v:
                        st.json(v['insights'])
                    else:
                        st.json(v)
                    if st.button("🔄 Reanalyze", key=f"reanalyze_{k}"):
                        optimizer = FiverrGigOptimizer()
                        keyword_insights = analyze_keyword_data(optimizer, k)
                        if keyword_insights:
                            display_keyword_insights(k, keyword_insights)
        else:
            st.info("No matching analyses found")

if __name__ == "__main__":
    main()

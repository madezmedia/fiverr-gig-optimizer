import streamlit as st
import pandas as pd
from typing import Dict, Any, Optional
import json
from shared import (
    init_session_state, render_sidebar, copy_to_clipboard,
    add_to_history, filter_results
)
from optimizer import FiverrGigOptimizer

def analyze_profile_data(optimizer: FiverrGigOptimizer, username: str) -> Optional[Dict[str, Any]]:
    """Analyze profile data with enhanced AI analysis."""
    try:
        # Initialize progress
        progress_text = "Operation in progress. Please wait."
        progress_bar = st.progress(0, text=progress_text)
        
        # Fetch profile data
        progress_bar.progress(20, text="🔍 Fetching profile data...")
        profile_data = optimizer.fetch_profile_data(username)
        if not profile_data:
            st.error("Failed to fetch profile data. Please check the username and try again.")
            return None
        
        # Fetch user's gigs
        progress_bar.progress(40, text="📦 Fetching user gigs...")
        gigs_data = optimizer.fetch_user_gigs(username)
        if not gigs_data:
            st.error("Failed to fetch gigs data. The user might not have any active gigs.")
            return None
        
        # Analyze profile with enhanced AI analysis
        progress_bar.progress(60, text="🤖 Analyzing profile...")
        profile_analysis = optimizer.analyze_profile(username, profile_data, gigs_data)
        if not profile_analysis:
            st.error("Failed to analyze profile. Please try again.")
            return None
        
        # Save analysis in history with metadata
        analysis_data = {
            "timestamp": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S"),
            "username": username,
            "profile_data": profile_data,
            "gigs_data": gigs_data,
            "analysis": profile_analysis,
            "category": st.session_state.selected_category,
            "subcategory": st.session_state.selected_subcategory,
            "tags": st.session_state.selected_tags
        }
        add_to_history(username, analysis_data)
        
        progress_bar.progress(100, text="✅ Analysis complete!")
        
        return analysis_data
        
    except Exception as e:
        st.error(f"Analysis failed: {str(e)}")
        if progress_bar:
            progress_bar.empty()
        return None

def display_profile_analysis(username: str, analysis_data: Dict[str, Any]):
    """Display comprehensive profile analysis with enhanced insights."""
    st.success("Analysis completed!")
    
    if not analysis_data or "analysis" not in analysis_data:
        st.error("No analysis data available")
        return
        
    analysis = analysis_data.get("analysis", {})
    if not analysis:
        st.error("Analysis results are empty")
        return
    
    # Profile Overview
    st.header("📊 Profile Overview")
    
    # Category Insights
    category_insights = analysis.get("category_insights", {})
    if category_insights:
        st.info(f"Primary Category: {category_insights.get('primary_category', 'Unknown')}")
        
        # Market Fit Score
        score = category_insights.get("market_fit_score", 0)
        score_color = "🟢" if score >= 8 else "🟡" if score >= 6 else "🔴"
        st.metric("Market Fit Score", f"{score_color} {score}/10")
    
        # Keyword Clusters
        st.subheader("🎯 Keyword Clusters")
        for cluster in category_insights.get("keyword_clusters", []):
            with st.expander(f"Topic: {cluster.get('topic', 'General')}"):
                for keyword in cluster.get("keywords", []):
                    st.markdown(f"- {keyword}")
    
    # Analysis Tabs
    analysis_tabs = st.tabs([
        "🔍 Competitive Analysis",
        "📈 Market Position",
        "✨ Optimization Suggestions",
        "📋 Action Plan"
    ])
    
    with analysis_tabs[0]:
        st.subheader("Competitive Analysis")
        
        competitive_analysis = analysis.get("competitive_analysis", {})
        if competitive_analysis:
            # SWOT Analysis
            col1, col2 = st.columns(2)
            with col1:
                with st.container():
                    st.markdown("### 💪 Strengths")
                    for strength in competitive_analysis.get("strengths", []):
                        st.markdown(f"✓ {strength}")
                
                with st.container():
                    st.markdown("### 🎯 Opportunities")
                    for opp in competitive_analysis.get("opportunities", []):
                        st.markdown(f"↗️ {opp}")
            
            with col2:
                with st.container():
                    st.markdown("### 🔍 Weaknesses")
                    for weakness in competitive_analysis.get("weaknesses", []):
                        st.markdown(f"⚠️ {weakness}")
                
                with st.container():
                    st.markdown("### ⚡ Threats")
                    for threat in competitive_analysis.get("threats", []):
                        st.markdown(f"⚠️ {threat}")
            
            # Unique Selling Points
            st.markdown("### 🌟 Unique Selling Points")
            for usp in competitive_analysis.get("unique_selling_points", []):
                st.markdown(f"🎯 {usp}")
        else:
            st.warning("No competitive analysis data available")
    
    with analysis_tabs[1]:
        st.subheader("Market Position Analysis")
        
        market_pos = analysis.get("market_position", {})
        if market_pos:
            # Market Metrics
            metrics_cols = st.columns(3)
            with metrics_cols[0]:
                st.metric("Price Position", f"{market_pos.get('price_percentile', 0)}th percentile")
            with metrics_cols[1]:
                st.metric("Rating Position", f"{market_pos.get('rating_percentile', 0)}th percentile")
            with metrics_cols[2]:
                st.metric("Response Position", f"{market_pos.get('response_percentile', 0)}th percentile")
            
            # Market Share and Growth
            st.info(f"**Market Share**: {market_pos.get('market_share_estimate', 'Unknown')}")
            st.info(f"**Growth Potential**: {market_pos.get('growth_potential', 'Unknown')}")
            
            # Trend Analysis
            trend_data = analysis.get("trend_analysis", {})
            if trend_data:
                st.markdown("### 📈 Market Trends")
                
                # Trend Direction
                trend_icon = {
                    "Growing": "📈",
                    "Stable": "📊",
                    "Declining": "📉"
                }.get(trend_data.get("trend_direction", "Unknown"), "📊")
                
                st.markdown(f"""
                - Direction: {trend_icon} {trend_data.get('trend_direction', 'Unknown')}
                - Market Size: {trend_data.get('market_size', 'Unknown')}
                - Growth Rate: {trend_data.get('growth_rate', 'Unknown')}
                """)
                
                # Seasonal Factors
                with st.expander("🗓️ Seasonal Factors"):
                    for factor in trend_data.get("seasonal_factors", []):
                        st.markdown(f"- {factor}")
                
                # Opportunities and Threats
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown("### 💡 Emerging Opportunities")
                    for opp in trend_data.get("emerging_opportunities", []):
                        st.markdown(f"- {opp}")
                
                with col2:
                    st.markdown("### ⚠️ Threat Factors")
                    for threat in trend_data.get("threat_factors", []):
                        st.markdown(f"- {threat}")
            else:
                st.warning("No trend analysis data available")
        else:
            st.warning("No market position data available")
    
    with analysis_tabs[2]:
        st.subheader("Optimization Suggestions")
        
        opt_data = analysis.get("optimization_suggestions", {})
        if opt_data:
            # Title Optimization
            title_data = opt_data.get("title", {})
            if title_data:
                st.markdown("### 🎯 Title Optimization")
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown("**Current Title:**")
                    st.code(title_data.get("current", "No current title"))
                with col2:
                    st.markdown("**Optimized Title:**")
                    optimized_title = title_data.get("optimized", "No optimization available")
                    st.code(optimized_title)
                    if st.button("📋 Copy Optimized Title"):
                        copy_to_clipboard(optimized_title)
                
                st.info(f"**Reasoning**: {title_data.get('reasoning', 'No reasoning provided')}")
            
            # Description Structure
            desc_data = opt_data.get("description", {})
            if desc_data:
                st.markdown("### 📝 Description Structure")
                for i, point in enumerate(desc_data.get("structure", []), 1):
                    st.markdown(f"{i}. {point}")
                
                # Key Points
                with st.expander("🔑 Key Points to Include"):
                    for point in desc_data.get("key_points", []):
                        st.markdown(f"- {point}")
                
                # SEO Keywords
                st.markdown("### 🎯 SEO Keywords")
                keyword_cols = st.columns(4)
                for i, keyword in enumerate(desc_data.get("seo_keywords", [])):
                    keyword_cols[i % 4].markdown(
                        f"""<div style='background-color: #e6f3ff; 
                        padding: 5px 10px; border-radius: 15px; 
                        text-align: center; margin: 2px;'>
                        {keyword}</div>""",
                        unsafe_allow_html=True
                    )
            
            # Portfolio Optimization
            portfolio_data = opt_data.get("portfolio", {})
            if portfolio_data:
                st.markdown("### 📸 Portfolio Optimization")
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown("**Recommended Samples:**")
                    for sample in portfolio_data.get("recommended_samples", []):
                        st.markdown(f"- {sample}")
                with col2:
                    st.markdown("**Presentation Tips:**")
                    for tip in portfolio_data.get("presentation_tips", []):
                        st.markdown(f"- {tip}")
            
            # Pricing Strategy
            pricing_data = opt_data.get("pricing_strategy", {})
            if pricing_data:
                st.markdown("### 💰 Pricing Strategy")
                st.info(f"**Market Position**: {pricing_data.get('market_position', 'Unknown')}")
                
                packages = pricing_data.get("packages", {})
                if packages:
                    pkg_cols = st.columns(3)
                    for i, (pkg_name, pkg_data) in enumerate(packages.items()):
                        with pkg_cols[i]:
                            st.markdown(
                                f"""<div style='background-color: #f0f2f6; 
                                padding: 15px; border-radius: 10px;'>
                                <h4 style='text-align: center;'>{pkg_name.title()}</h4>
                                <h3 style='text-align: center; color: #0066cc;'>
                                ${pkg_data.get('price', 0)}</h3>
                                <hr>
                                <p><strong>Features:</strong></p>
                                {"".join(f"<p>✓ {feature}</p>" for feature in pkg_data.get('features', []))}
                                <p><strong>Upsell Opportunities:</strong></p>
                                {"".join(f"<p>↗️ {upsell}</p>" for upsell in pkg_data.get('upsell_opportunities', []))}
                                </div>""",
                                unsafe_allow_html=True
                            )
        else:
            st.warning("No optimization suggestions available")
    
    with analysis_tabs[3]:
        st.subheader("Action Plan")
        
        action_plan = analysis.get("action_plan", {})
        if action_plan:
            # Immediate Actions
            immediate = action_plan.get("immediate", {})
            if immediate:
                with st.expander("🚀 Immediate Actions", expanded=True):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown("**Tasks:**")
                        for task in immediate.get("tasks", []):
                            st.markdown(f"✓ {task}")
                    with col2:
                        st.markdown("**Expected Impact:**")
                        for impact in immediate.get("expected_impact", []):
                            st.markdown(f"↗️ {impact}")
            
            # Short Term Actions
            short_term = action_plan.get("short_term", {})
            if short_term:
                with st.expander("⏳ Short Term Actions"):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown("**Tasks:**")
                        for task in short_term.get("tasks", []):
                            st.markdown(f"✓ {task}")
                    with col2:
                        st.markdown("**Expected Impact:**")
                        for impact in short_term.get("expected_impact", []):
                            st.markdown(f"↗️ {impact}")
            
            # Long Term Actions
            long_term = action_plan.get("long_term", {})
            if long_term:
                with st.expander("🎯 Long Term Actions"):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown("**Tasks:**")
                        for task in long_term.get("tasks", []):
                            st.markdown(f"✓ {task}")
                    with col2:
                        st.markdown("**Expected Impact:**")
                        for impact in long_term.get("expected_impact", []):
                            st.markdown(f"↗️ {impact}")
            
            # SEO Optimization Score
            seo_data = analysis.get("seo_optimization", {})
            if seo_data:
                st.markdown("### 🎯 SEO Optimization")
                
                # Display score with color indicator
                score = seo_data.get("optimization_score", 0)
                score_color = "🟢" if score >= 8 else "🟡" if score >= 6 else "🔴"
                st.metric("SEO Score", f"{score_color} {score}/10")
                
                # Target Keywords
                st.markdown("**Target Keywords:**")
                keyword_cols = st.columns(4)
                for i, keyword in enumerate(seo_data.get("target_keywords", [])):
                    keyword_cols[i % 4].markdown(
                        f"""<div style='background-color: #e6f3ff; 
                        padding: 5px 10px; border-radius: 15px; 
                        text-align: center; margin: 2px;'>
                        {keyword}</div>""",
                        unsafe_allow_html=True
                    )
                
                # Content Gaps
                st.markdown("**Content Gaps to Address:**")
                for gap in seo_data.get("content_gaps", []):
                    st.markdown(f"- {gap}")
        else:
            st.warning("No action plan available")

def main():
    """Main function for the profile analysis page."""
    # Initialize session state and render sidebar
    init_session_state()
    render_sidebar()
    
    st.title("🎯 Profile Analysis")
    
    # Profile input
    username = st.text_input(
        "Enter Fiverr Username",
        help="Example: johndoe (without https://www.fiverr.com/)",
        placeholder="Enter username"
    )
    
    if st.button("Analyze Profile", type="primary"):
        if not username:
            st.warning("Please enter a Fiverr username")
            return
        
        optimizer = FiverrGigOptimizer()
        analysis_data = analyze_profile_data(optimizer, username)
        
        if analysis_data:
            display_profile_analysis(username, analysis_data)
    
    # Display filtered history
    if st.session_state.analysis_history:
        st.markdown("### 📚 Analysis History")
        filtered_history = filter_results(st.session_state.analysis_history)
        
        if filtered_history:
            for k, v in filtered_history.items():
                if "username" in v:  # Only show profile analyses
                    with st.expander(f"**{v['username']}** - {v['timestamp']}"):
                        st.json(v['analysis'])
                        if st.button("🔄 Reanalyze", key=f"reanalyze_{k}"):
                            optimizer = FiverrGigOptimizer()
                            new_analysis = analyze_profile_data(optimizer, v['username'])
                            if new_analysis:
                                display_profile_analysis(v['username'], new_analysis)
        else:
            st.info("No matching analyses found")

if __name__ == "__main__":
    main()

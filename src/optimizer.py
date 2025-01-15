import openai
import pandas as pd
from typing import Optional, Dict, Any, List
import json
import streamlit as st
from bs4 import BeautifulSoup
from io import StringIO
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import timedelta
import requests
from api_client import APIClient
from cache_manager import CacheManager

class FiverrGigOptimizer:
    """
    A class to handle Fiverr gig optimization operations including keyword research,
    trend analysis, and description optimization.
    """
    
    def __init__(self):
        """Initialize the optimizer with API keys and support services."""
        self.scraper_api_key = st.session_state.SCRAPER_API_KEY
        self.fiverr_api_key = st.session_state.get('FIVERR_API_KEY')
        
        # Initialize support services
        self.api_client = APIClient()
        self.cache = CacheManager()
        
        # Configure default headers
        self.default_headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        # Set up Fiverr API headers if key is available
        if self.fiverr_api_key:
            self.fiverr_headers = {
                "x-rapidapi-key": self.fiverr_api_key,
                "x-rapidapi-host": "fiverr7.p.rapidapi.com"
            }
    
    def _get_page_data(self, url: str) -> Optional[Dict[str, Any]]:
        """Helper method to fetch and parse page data with caching."""
        try:
            # Check cache first
            cache_key = f"page_data_{url}"
            cached_data = self.cache.get(cache_key, max_age=timedelta(hours=1))
            if cached_data:
                # Reconstruct BeautifulSoup object from cached HTML
                soup = BeautifulSoup(cached_data['html'], features='html.parser')
                return {
                    'soup': soup,
                    'props_json': cached_data['props_json'],
                    'html': cached_data['html']
                }
            
            # Fetch fresh data using ScraperAPI
            encoded_url = requests.utils.quote(url)
            scraper_url = f"http://api.scraperapi.com?api_key={self.scraper_api_key}&url={encoded_url}&render=true"
            
            st.info(f"Fetching data from URL: {url}")
            response = self.api_client.get(scraper_url)
            
            # Log response details
            st.info(f"Response received. Type: {type(response)}")
            
            # Parse HTML using StringIO to avoid markup warning
            html_content = StringIO(response.text if isinstance(response, str) else response.text)
            st.info("HTML content parsed successfully")
            soup = BeautifulSoup(html_content, features='html.parser')
            
            # Log soup content for debugging
            st.info(f"BeautifulSoup object created. Found {len(soup.find_all())} elements")
            
            # Try to extract JSON data from script tags
            scripts = soup.find_all('script', {'type': 'application/json'})
            st.info(f"Found {len(scripts)} script tags with type 'application/json'")
            props_json = {}
            
            for script in scripts:
                try:
                    if script.string and script.string.strip():
                        script_content = script.string.strip()
                        # Handle potential HTML entities
                        script_content = script_content.replace('&quot;', '"')
                        data = json.loads(script_content)
                        if isinstance(data, dict):
                            props_json.update(data)
                except json.JSONDecodeError:
                    continue
                except Exception as e:
                    st.error(f"Error parsing script data: {str(e)}")
                    continue
            
            return {
                'soup': soup,
                'props_json': props_json,
                'html': str(soup)
            }
            
        except Exception as e:
            st.error(f"Failed to fetch page data: {str(e)}")
            return None
    
    def fetch_profile_data(self, username: str) -> Optional[Dict[str, Any]]:
        """
        Fetch profile data from Fiverr using scraping.
        
        Args:
            username (str): The Fiverr username to analyze
            
        Returns:
            Optional[Dict[str, Any]]: The profile data or None if an error occurs
        """
        try:
            # Generate public profile URL
            profile_url = f"https://www.fiverr.com/{username.strip().lower()}"
            st.info(f"Attempting to fetch profile from: {profile_url}")
            
            # Fetch page data
            page_data = self._get_page_data(profile_url)
            if not page_data:
                st.error("Failed to get page data")
                return None
            
            soup = page_data['soup']
            st.info("Extracting profile elements...")
            
            # Log found elements for debugging
            st.info(f"Found {len(soup.find_all('div', {'class': 'language'}))} language elements")
            st.info(f"Found {len(soup.find_all('div', {'class': 'skill-tag'}))} skill elements")
            
            # Extract profile data with more flexible selectors
            languages = []
            for lang_elem in soup.find_all(['div', 'span'], class_=lambda x: x and 'language' in x.lower()):
                languages.append(lang_elem.text.strip())
            
            skills = []
            for skill_elem in soup.find_all(['div', 'span'], class_=lambda x: x and ('skill' in x.lower() or 'tag' in x.lower())):
                skills.append(skill_elem.text.strip())
            
            member_since = ""
            for elem in soup.find_all(['div', 'span', 'p'], string=lambda x: x and 'member since' in x.lower()):
                member_since = elem.text.strip()
                break
            
            response_time = ""
            for elem in soup.find_all(['div', 'span', 'p'], string=lambda x: x and 'response time' in x.lower()):
                response_time = elem.text.strip()
                break
            
            last_delivery = ""
            for elem in soup.find_all(['div', 'span', 'p'], string=lambda x: x and 'last delivery' in x.lower()):
                last_delivery = elem.text.strip()
                break
            
            profile_data = {
                "username": username,
                "props_json": page_data['props_json'],
                "html": page_data['html'],
                "languages": languages,
                "skills": skills,
                "member_since": member_since,
                "response_time": response_time,
                "last_delivery": last_delivery
            }
            
            st.info("Profile data extracted successfully")
            return profile_data
            
        except Exception as e:
            st.error(f"Failed to fetch profile: {str(e)}")
            st.error(f"Error type: {type(e).__name__}")
            st.error(f"Error details: {str(e)}")
            return None
    
    def fetch_user_gigs(self, username: str) -> Optional[Dict[str, Any]]:
        """
        Fetch user's gigs using scraping.
        
        Args:
            username (str): The Fiverr username
            
        Returns:
            Optional[Dict[str, Any]]: The gigs data or None if an error occurs
        """
        try:
            # Generate gigs URL
            gigs_url = f"https://www.fiverr.com/{username.strip().lower()}/gigs"
            
            # Fetch page data
            page_data = self._get_page_data(gigs_url)
            if not page_data:
                return None
            
            soup = page_data['soup']
            
            # Extract gigs data
            gigs = []
            gig_cards = soup.find_all('div', {'class': 'gig-card-layout'})
            
            for card in gig_cards:
                gig = {
                    "title": card.find('h3').text.strip() if card.find('h3') else "",
                    "description": card.find('p', {'class': 'description'}).text.strip() if card.find('p', {'class': 'description'}) else "",
                    "price": card.find('span', {'class': 'price'}).text.strip() if card.find('span', {'class': 'price'}) else "0",
                    "rating": card.find('span', {'class': 'rating'}).text.strip() if card.find('span', {'class': 'rating'}) else "0",
                    "reviews": card.find('span', {'class': 'reviews'}).text.strip() if card.find('span', {'class': 'reviews'}) else "0",
                    "orders_in_queue": card.find('span', {'class': 'orders-in-queue'}).text.strip() if card.find('span', {'class': 'orders-in-queue'}) else "0",
                    "delivery_time": card.find('span', {'class': 'delivery-time'}).text.strip() if card.find('span', {'class': 'delivery-time'}) else "",
                    "tags": [tag.text.strip() for tag in card.find_all('span', {'class': 'gig-tag'})]
                }
                gigs.append(gig)
            
            gigs_data = {
                "username": username,
                "gigs": gigs,
                "props_json": page_data['props_json'],
                "html": page_data['html'],
                "total_gigs": len(gigs),
                "categories": list(set(tag for gig in gigs for tag in gig['tags']))
            }
            
            return gigs_data
            
        except Exception as e:
            st.error(f"Failed to fetch gigs: {str(e)}")
            return None
    
    def analyze_profile(self, username: str, profile_data: Dict[str, Any], gigs_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Perform comprehensive profile analysis using AI and market data.
        
        Args:
            username (str): The Fiverr username
            profile_data (Dict[str, Any]): The profile data
            gigs_data (Dict[str, Any]): The gigs data
            
        Returns:
            Optional[Dict[str, Any]]: Enhanced analysis results or None if an error occurs
        """
        try:
            if not profile_data or not gigs_data:
                return {
                    "category_insights": {
                        "primary_category": "Unknown",
                        "subcategories": [],
                        "keyword_clusters": [],
                        "market_fit_score": 0,
                        "category_opportunities": []
                    },
                    "competitive_analysis": {
                        "strengths": [],
                        "weaknesses": [],
                        "opportunities": [],
                        "threats": [],
                        "unique_selling_points": []
                    },
                    "optimization_suggestions": {
                        "title": {
                            "current": "",
                            "optimized": "",
                            "reasoning": ""
                        },
                        "description": {
                            "structure": [],
                            "key_points": [],
                            "seo_keywords": []
                        },
                        "portfolio": {
                            "recommended_samples": [],
                            "presentation_tips": []
                        },
                        "pricing_strategy": {
                            "market_position": "Unknown",
                            "packages": {}
                        }
                    },
                    "market_position": {
                        "price_percentile": 0,
                        "rating_percentile": 0,
                        "response_percentile": 0,
                        "market_share_estimate": "Unknown",
                        "growth_potential": "Unknown"
                    },
                    "action_plan": {
                        "immediate": {
                            "tasks": [],
                            "expected_impact": []
                        },
                        "short_term": {
                            "tasks": [],
                            "expected_impact": []
                        },
                        "long_term": {
                            "tasks": [],
                            "expected_impact": []
                        }
                    },
                    "seo_optimization": {
                        "target_keywords": [],
                        "content_gaps": [],
                        "optimization_score": 0
                    }
                }
            
            # Step 1: Extract key information
            gig_titles = [gig.get('title', '') for gig in gigs_data.get('gigs', [])]
            gig_descriptions = [gig.get('description', '') for gig in gigs_data.get('gigs', [])]
            reviews = gigs_data.get('reviews', [])
            pricing_data = [{'price': gig.get('price', '0')} for gig in gigs_data.get('gigs', [])]
            
            # Step 2: Perform category analysis
            category_analysis = self._analyze_categories(gig_titles, gig_descriptions)
            
            # Step 3: Analyze market position
            market_position = self._analyze_market_position(pricing_data, reviews)
            
            # Step 4: Generate comprehensive AI analysis
            # Create a trimmed version of the data without HTML content
            trimmed_profile_data = {
                "username": profile_data["username"],
                "languages": profile_data["languages"],
                "skills": profile_data["skills"],
                "member_since": profile_data["member_since"],
                "response_time": profile_data["response_time"],
                "last_delivery": profile_data["last_delivery"]
            }
            
            trimmed_gigs_data = {
                "username": gigs_data["username"],
                "gigs": [{
                    "title": gig["title"],
                    "description": gig["description"],
                    "price": gig["price"],
                    "rating": gig["rating"],
                    "reviews": gig["reviews"],
                    "orders_in_queue": gig["orders_in_queue"],
                    "delivery_time": gig["delivery_time"],
                    "tags": gig["tags"]
                } for gig in gigs_data["gigs"]],
                "total_gigs": gigs_data["total_gigs"],
                "categories": gigs_data["categories"]
            }
            
            context = {
                "username": username,
                "profile_data": trimmed_profile_data,
                "gigs_data": trimmed_gigs_data,
                "category_analysis": category_analysis,
                "market_position": market_position
            }
            
            st.info("Sending analysis request to OpenAI...")
            response = openai.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": """You are an expert in Fiverr profile optimization and market analysis.
                    Analyze the profile, gigs, and market data to provide comprehensive insights in the following JSON format:
                    {
                        "category_insights": {
                            "primary_category": "string",
                            "subcategories": ["string"],
                            "keyword_clusters": [{"topic": "string", "keywords": ["string"]}],
                            "market_fit_score": number,
                            "category_opportunities": ["string"]
                        },
                        "competitive_analysis": {
                            "strengths": ["string"],
                            "weaknesses": ["string"],
                            "opportunities": ["string"],
                            "threats": ["string"],
                            "unique_selling_points": ["string"]
                        },
                        "optimization_suggestions": {
                            "title": {
                                "current": "string",
                                "optimized": "string",
                                "reasoning": "string"
                            },
                            "description": {
                                "structure": ["string"],
                                "key_points": ["string"],
                                "seo_keywords": ["string"]
                            },
                            "portfolio": {
                                "recommended_samples": ["string"],
                                "presentation_tips": ["string"]
                            },
                            "pricing_strategy": {
                                "market_position": "string",
                                "packages": {
                                    "basic": {"price": number, "features": ["string"], "upsell_opportunities": ["string"]},
                                    "standard": {"price": number, "features": ["string"], "upsell_opportunities": ["string"]},
                                    "premium": {"price": number, "features": ["string"], "upsell_opportunities": ["string"]}
                                }
                            }
                        },
                        "market_position": {
                            "price_percentile": number,
                            "rating_percentile": number,
                            "response_percentile": number,
                            "market_share_estimate": "string",
                            "growth_potential": "string"
                        },
                        "action_plan": {
                            "immediate": {
                                "tasks": ["string"],
                                "expected_impact": ["string"]
                            },
                            "short_term": {
                                "tasks": ["string"],
                                "expected_impact": ["string"]
                            },
                            "long_term": {
                                "tasks": ["string"],
                                "expected_impact": ["string"]
                            }
                        },
                        "seo_optimization": {
                            "target_keywords": ["string"],
                            "content_gaps": ["string"],
                            "optimization_score": number
                        }
                    }"""},
                    {"role": "user", "content": f"Perform comprehensive analysis of this Fiverr profile data: {json.dumps(context)}"}
                ]
            )
            
            analysis_results = json.loads(response.choices[0].message.content)
            
            # Step 5: Enhance with trend data
            analysis_results["trend_analysis"] = self._analyze_trends(
                analysis_results["category_insights"]["primary_category"],
                analysis_results["seo_optimization"]["target_keywords"]
            )
            
            return analysis_results
        except Exception as e:
            st.error(f"Profile analysis failed: {str(e)}")
            return None
    
    def get_reviews_by_category(self, category: str) -> Optional[Dict[str, Any]]:
        """
        Fetch reviews data for a specific category using Fiverr API.
        
        Args:
            category (str): The category to fetch reviews for
            
        Returns:
            Optional[Dict[str, Any]]: Reviews data or None if an error occurs
        """
        try:
            # Use ScraperAPI to fetch category reviews
            url = f"https://www.fiverr.com/categories/{category.lower().replace(' ', '-')}/reviews"
            encoded_url = requests.utils.quote(url)
            scraper_url = f"http://api.scraperapi.com?api_key={self.scraper_api_key}&url={encoded_url}&render=true"
            
            response = self.api_client.get(scraper_url)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract reviews from the page
            review_elements = soup.find_all('div', {'class': 'review-item'})
            reviews_data = []
            
            for review in review_elements:
                try:
                    rating_elem = review.find('span', {'class': 'rating'})
                    comment_elem = review.find('p', {'class': 'review-description'})
                    
                    reviews_data.append({
                        'rating': float(rating_elem.text.strip()) if rating_elem else 0,
                        'comment': comment_elem.text.strip() if comment_elem else '',
                    })
                except Exception as e:
                    st.error(f"Error parsing review: {str(e)}")
                    continue
            
            # Process and structure the reviews data
            processed_data = {
                "category": category,
                "total_reviews": len(reviews_data),
                "average_rating": sum(review.get('rating', 0) for review in reviews_data) / len(reviews_data) if reviews_data else 0,
                "sentiment_distribution": {
                    "positive": len([r for r in reviews_data if r.get('rating', 0) >= 4]),
                    "neutral": len([r for r in reviews_data if r.get('rating', 0) == 3]),
                    "negative": len([r for r in reviews_data if r.get('rating', 0) <= 2])
                },
                "common_keywords": self._extract_review_keywords(reviews_data),
                "buyer_demographics": self._analyze_buyer_demographics(reviews_data)
            }
            
            return processed_data
            
        except Exception as e:
            st.error(f"Failed to fetch category reviews: {str(e)}")
            return None
            
    def _extract_review_keywords(self, reviews: List[Dict[str, Any]]) -> List[Dict[str, int]]:
        """Extract and count common keywords from reviews."""
        try:
            # Combine all review texts
            all_text = " ".join([review.get('comment', '') for review in reviews])
            
            # Use GPT to extract meaningful keywords
            response = openai.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "Extract the most significant keywords from these reviews and return them as a JSON array of objects with 'keyword' and 'count' properties."},
                    {"role": "user", "content": all_text}
                ]
            )
            
            return json.loads(response.choices[0].message.content)
        except Exception as e:
            st.error(f"Failed to extract review keywords: {str(e)}")
            return []
            
    def _analyze_buyer_demographics(self, reviews: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze buyer demographics from reviews."""
        try:
            # Extract available demographic data
            countries = [review.get('buyer_country') for review in reviews if review.get('buyer_country')]
            
            return {
                "top_countries": self._get_top_items(countries, 5),
                "total_unique_buyers": len(set(review.get('buyer_id') for review in reviews if review.get('buyer_id'))),
                "repeat_buyer_percentage": self._calculate_repeat_buyers(reviews)
            }
        except Exception as e:
            st.error(f"Failed to analyze buyer demographics: {str(e)}")
            return {}
            
    def _get_top_items(self, items: List[str], limit: int = 5) -> List[Dict[str, Any]]:
        """Get top occurring items with their counts."""
        from collections import Counter
        counter = Counter(items)
        return [{"item": item, "count": count} for item, count in counter.most_common(limit)]
        
    def _calculate_repeat_buyers(self, reviews: List[Dict[str, Any]]) -> float:
        """Calculate percentage of repeat buyers."""
        try:
            buyer_counts = {}
            for review in reviews:
                buyer_id = review.get('buyer_id')
                if buyer_id:
                    buyer_counts[buyer_id] = buyer_counts.get(buyer_id, 0) + 1
                    
            repeat_buyers = len([b for b in buyer_counts.values() if b > 1])
            total_buyers = len(buyer_counts)
            
            return (repeat_buyers / total_buyers * 100) if total_buyers > 0 else 0
        except Exception:
            return 0
            
    def _analyze_categories(self, titles: List[str], descriptions: List[str]) -> Dict[str, Any]:
        """Analyze gig titles and descriptions to determine optimal categories."""
        try:
            # If no titles or descriptions, return default structure
            if not titles and not descriptions:
                return {
                    "primary_category": "Unknown",
                    "subcategories": [],
                    "keyword_clusters": [{"topic": "General", "keywords": []}],
                    "category_fit_score": 0,
                    "suggested_categories": []
                }
            
            # Combine titles and descriptions for analysis
            combined_text = "\n".join(titles + descriptions)
            if not combined_text.strip():
                return {
                    "primary_category": "Unknown",
                    "subcategories": [],
                    "keyword_clusters": [{"topic": "General", "keywords": []}],
                    "category_fit_score": 0,
                    "suggested_categories": []
                }
            
            st.info("Analyzing categories...")
            response = openai.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": """Analyze the text to determine optimal Fiverr categories.
                    Return analysis in the following JSON format:
                    {
                        "primary_category": "string",
                        "subcategories": ["string"],
                        "keyword_clusters": [{"topic": "string", "keywords": ["string"]}],
                        "category_fit_score": number,
                        "suggested_categories": ["string"]
                    }"""},
                    {"role": "user", "content": f"Analyze this gig content:\n{combined_text}"}
                ]
            )
            
            result = json.loads(response.choices[0].message.content)
            st.info("Category analysis completed successfully")
            return result
        except Exception as e:
            st.error(f"Category analysis failed: {str(e)}")
            return {
                "primary_category": "Unknown",
                "subcategories": [],
                "keyword_clusters": [{"topic": "General", "keywords": []}],
                "category_fit_score": 0,
                "suggested_categories": []
            }
    
    def _analyze_market_position(self, pricing_data: List[Dict[str, Any]], reviews: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze market position based on pricing and reviews."""
        try:
            # Calculate pricing statistics
            prices = []
            for price_info in pricing_data:
                if isinstance(price_info, dict):
                    price_str = price_info.get('price', '0')
                    # Extract numeric value from price string (e.g., "$50" -> 50)
                    try:
                        price = float(''.join(filter(str.isdigit, price_str)))
                        prices.append(price)
                    except ValueError:
                        continue
            
            avg_price = sum(prices) / len(prices) if prices else 0
            
            # Calculate review statistics
            ratings = [float(review.get('rating', '0')) for review in reviews]
            avg_rating = sum(ratings) / len(ratings) if ratings else 0
            
            return {
                "average_price": avg_price,
                "price_range": f"${min(prices)}-${max(prices)}" if prices else "N/A",
                "average_rating": avg_rating,
                "total_reviews": len(reviews),
                "rating_distribution": {
                    "5_star": len([r for r in ratings if r == 5]),
                    "4_star": len([r for r in ratings if r == 4]),
                    "3_star": len([r for r in ratings if r == 3]),
                    "2_star": len([r for r in ratings if r == 2]),
                    "1_star": len([r for r in ratings if r == 1])
                }
            }
        except Exception as e:
            st.error(f"Market position analysis failed: {str(e)}")
            return {
                "average_price": 0,
                "price_range": "N/A",
                "average_rating": 0,
                "total_reviews": 0,
                "rating_distribution": {
                    "5_star": 0,
                    "4_star": 0,
                    "3_star": 0,
                    "2_star": 0,
                    "1_star": 0
                }
            }
    
    def _analyze_trends(self, category: str, keywords: List[str]) -> Dict[str, Any]:
        """Analyze market trends for the category and keywords."""
        try:
            if not category or not keywords:
                return {
                    "trend_direction": "Unknown",
                    "market_size": "Unknown",
                    "growth_rate": "Unknown",
                    "seasonal_factors": [],
                    "emerging_opportunities": [],
                    "threat_factors": []
                }
            
            response = openai.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": """Analyze market trends for the given category and keywords.
                    Return analysis in the following JSON format:
                    {
                        "trend_direction": "Growing|Stable|Declining",
                        "market_size": "string",
                        "growth_rate": "string",
                        "seasonal_factors": ["string"],
                        "emerging_opportunities": ["string"],
                        "threat_factors": ["string"]
                    }"""},
                    {"role": "user", "content": f"Analyze trends for category '{category}' and keywords: {keywords}"}
                ]
            )
            
            result = json.loads(response.choices[0].message.content)
            return result
        except Exception as e:
            st.error(f"Trend analysis failed: {str(e)}")
            return {
                "trend_direction": "Unknown",
                "market_size": "Unknown",
                "growth_rate": "Unknown",
                "seasonal_factors": [],
                "emerging_opportunities": [],
                "threat_factors": []
            }
    
    def scrape_gig_data(self, keyword: str) -> Optional[Dict[str, Any]]:
        """
        Enhanced gig data scraping with comprehensive market analysis including category reviews.
        
        Args:
            keyword (str): The search keyword to scrape gigs for
            
        Returns:
            Optional[Dict[str, Any]]: Enhanced gig data or None if an error occurs
        """
        try:
            # Step 1: Basic gig data scraping
            page_data = self._get_page_data(f"https://www.fiverr.com/search/gigs?query={keyword}")
            if not page_data:
                return None
            
            soup = page_data['soup']
            
            # Extract gig details
            gigs = []
            gig_cards = soup.find_all('div', {'class': 'gig-card-layout'})
            
            for card in gig_cards:
                gig = {
                    "title": card.find('h3').text.strip() if card.find('h3') else "",
                    "description": card.find('p', {'class': 'description'}).text.strip() if card.find('p', {'class': 'description'}) else "",
                    "price": card.find('span', {'class': 'price'}).text.strip() if card.find('span', {'class': 'price'}) else "0",
                    "rating": card.find('span', {'class': 'rating'}).text.strip() if card.find('span', {'class': 'rating'}) else "0",
                    "reviews": card.find('span', {'class': 'reviews'}).text.strip() if card.find('span', {'class': 'reviews'}) else "0",
                    "orders_in_queue": card.find('span', {'class': 'orders-in-queue'}).text.strip() if card.find('span', {'class': 'orders-in-queue'}) else "0",
                    "delivery_time": card.find('span', {'class': 'delivery-time'}).text.strip() if card.find('span', {'class': 'delivery-time'}) else "",
                    "tags": [tag.text.strip() for tag in card.find_all('span', {'class': 'gig-tag'})]
                }
                gigs.append(gig)
            
            # Step 2: Extract gig details
            gig_titles = [gig.get('title', '') for gig in gigs]
            gig_descriptions = [gig.get('description', '') for gig in gigs]
            
            # Step 3: Analyze categories
            category_analysis = self._analyze_categories(gig_titles, gig_descriptions)
            
            # Step 4: Analyze market position
            market_position = self._analyze_market_position(
                [{'price': gig.get('price', '0')} for gig in gigs],
                [{'rating': gig.get('rating', '0')} for gig in gigs]
            )
            
            # Step 5: Get category reviews if available
            category_reviews = self.get_reviews_by_category(category_analysis.get('primary_category', ''))
            
            # Step 6: Enhance with trend analysis
            trend_analysis = self._analyze_trends(
                category_analysis.get('primary_category', ''),
                category_analysis.get('keyword_clusters', [{}])[0].get('keywords', [])
            )
            
            # Combine all analyses with review insights
            enhanced_data = {
                "raw_data": {
                    "gigs": gigs,
                    "total_gigs": len(gigs),
                    "categories": list(set(tag for gig in gigs for tag in gig['tags']))
                },
                "category_analysis": category_analysis,
                "market_position": market_position,
                "trend_analysis": trend_analysis,
                "category_reviews": category_reviews,
                "timestamp": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            return enhanced_data
        except Exception as e:
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
            
            result = json.loads(response.choices[0].message.content)
            return result
        except Exception as e:
            st.error(f"AI Analysis failed: {str(e)}")
            return {
                "related_keywords": [],
                "market_analysis": {
                    "trend": "Unknown",
                    "target_audience": "Unknown",
                    "market_size": "Unknown",
                    "top_regions": []
                },
                "raw_insights": "Analysis failed"
            }
            
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
            
            result = json.loads(response.choices[0].message.content)
            return result
        except Exception as e:
            st.error(f"Gig template generation failed: {str(e)}")
            return {
                "title": f"{keyword} Service",
                "description": "Service description not available",
                "search_tags": [keyword],
                "packages": {
                    "basic": {"name": "Basic", "price": 10, "delivery_time": 3, "features": [], "description": "Basic package"},
                    "standard": {"name": "Standard", "price": 20, "delivery_time": 5, "features": [], "description": "Standard package"},
                    "premium": {"name": "Premium", "price": 30, "delivery_time": 7, "features": [], "description": "Premium package"}
                },
                "requirements": [],
                "faq": [],
                "portfolio_suggestions": [],
                "upsell_opportunities": []
            }

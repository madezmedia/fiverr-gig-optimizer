import json
import os
from typing import Dict, Any, List, Optional

class StateManager:
    """Manages persistent state storage for the Fiverr Gig Optimizer."""
    
    def __init__(self):
        """Initialize the state manager with default paths."""
        self.state_dir = os.path.join(os.path.dirname(__file__), "state")
        self.state_file = os.path.join(self.state_dir, "app_state.json")
        self._ensure_state_dir()
        self._init_state()
    
    def _ensure_state_dir(self) -> None:
        """Ensure the state directory exists."""
        if not os.path.exists(self.state_dir):
            os.makedirs(self.state_dir)
    
    def _init_state(self) -> None:
        """Initialize state file if it doesn't exist."""
        if not os.path.exists(self.state_file):
            self.save_state({
                "favorites": [],
                "saved_gigs": {},
                "analysis_history": {},
                "generated_gigs": {}
            })
    
    def _load_state(self) -> Dict[str, Any]:
        """Load state from file with error handling."""
        try:
            if os.path.exists(self.state_file):
                with open(self.state_file, 'r') as f:
                    return json.load(f)
            return {
                "favorites": [],
                "saved_gigs": {},
                "analysis_history": {},
                "generated_gigs": {}
            }
        except Exception as e:
            print(f"Error loading state: {str(e)}")
            return {
                "favorites": [],
                "saved_gigs": {},
                "analysis_history": {},
                "generated_gigs": {}
            }
    
    def save_state(self, state: Dict[str, Any]) -> None:
        """Save state to file with error handling."""
        try:
            with open(self.state_file, 'w') as f:
                json.dump(state, f, indent=2)
        except Exception as e:
            print(f"Error saving state: {str(e)}")
    
    def get_favorites(self) -> List[str]:
        """Get list of favorite keywords."""
        return self._load_state().get("favorites", [])
    
    def add_to_favorites(self, keyword: str) -> None:
        """Add keyword to favorites."""
        state = self._load_state()
        if keyword not in state["favorites"]:
            state["favorites"].append(keyword)
            self.save_state(state)
    
    def remove_from_favorites(self, keyword: str) -> None:
        """Remove keyword from favorites."""
        state = self._load_state()
        if keyword in state["favorites"]:
            state["favorites"].remove(keyword)
            self.save_state(state)
    
    def get_saved_gigs(self) -> Dict[str, Any]:
        """Get saved gigs data."""
        return self._load_state().get("saved_gigs", {})
    
    def save_gig(self, keyword: str, gig_data: Dict[str, Any]) -> None:
        """Save gig data for a keyword."""
        state = self._load_state()
        state["saved_gigs"][keyword] = gig_data
        self.save_state(state)
    
    def delete_gig(self, keyword: str) -> None:
        """Delete gig data for a keyword."""
        state = self._load_state()
        if keyword in state["saved_gigs"]:
            del state["saved_gigs"][keyword]
            self.save_state(state)
    
    def get_analysis_history(self) -> Dict[str, Any]:
        """Get analysis history data."""
        return self._load_state().get("analysis_history", {})
    
    def add_to_history(self, keyword: str, data: Dict[str, Any]) -> None:
        """Add analysis data to history."""
        state = self._load_state()
        state["analysis_history"][keyword] = data
        self.save_state(state)
    
    def get_generated_gigs(self) -> Dict[str, Any]:
        """Get generated gigs data."""
        return self._load_state().get("generated_gigs", {})
    
    def add_generated_gig(self, keyword: str, gig_data: Dict[str, Any]) -> None:
        """Add generated gig data."""
        state = self._load_state()
        state["generated_gigs"][keyword] = gig_data
        self.save_state(state)
    
    def clear_state(self) -> None:
        """Clear all state data."""
        self.save_state({
            "favorites": [],
            "saved_gigs": {},
            "analysis_history": {},
            "generated_gigs": {}
        })

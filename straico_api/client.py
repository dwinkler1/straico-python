"""
Straico API Client - Python client for Straico's multi-LLM API.
"""

import difflib
import sys
import threading
import time
from typing import Dict, List, Optional

import requests


class LoadingAnimation:
    """Simple loading animation for API requests."""

    def __init__(self, message: str = "Thinking"):
        self.message = message
        self.running = False
        self.thread = None
        self.frames = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]

    def _animate(self):
        """Run the animation loop."""
        idx = 0
        while self.running:
            frame = self.frames[idx % len(self.frames)]
            print(f"\r{frame} {self.message}...", end="", flush=True)
            idx += 1
            time.sleep(0.1)

    def start(self):
        """Start the loading animation."""
        self.running = True
        self.thread = threading.Thread(target=self._animate, daemon=True)
        self.thread.start()

    def stop(self):
        """Stop the loading animation."""
        self.running = False
        if self.thread:
            self.thread.join()
        print("\r" + " " * (len(self.message) + 20) + "\r", end="", flush=True)


class StraicoClient:
    """Client for interacting with Straico API with smart LLM selection."""

    def __init__(self, api_key: str, api_version: str = "v1"):
        """
        Initialize Straico client.

        Args:
            api_key: Straico API key
            api_version: API version to use ("v0" or "v1", default: "v1")
        """
        self.api_key = api_key
        self.api_version = api_version
        self.base_url = f"https://api.straico.com/{api_version}"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    def get_models(self) -> Dict:
        """
        Fetch available models from Straico API.

        Returns:
            Dictionary containing model information
        """
        try:
            response = requests.get("https://api.straico.com/v1/models", headers=self.headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching models: {e}", file=sys.stderr)
            return {"data": [], "success": False}

    def find_similar_models(self, model_name: str, max_suggestions: int = 5) -> List[Dict]:
        """
        Find similar model names based on string similarity.

        Args:
            model_name: The model name to find matches for
            max_suggestions: Maximum number of suggestions to return

        Returns:
            List of similar models with their details
        """
        models_response = self.get_models()
        if not models_response.get("success"):
            return []

        all_models = models_response.get("data", {}).get("chat", [])
        if not all_models:
            return []

        # Extract model IDs and names
        model_list = [(m.get("model", ""), m.get("name", ""), m) for m in all_models]

        # Find similar models using difflib
        model_ids = [m[0] for m in model_list]
        close_matches = difflib.get_close_matches(
            model_name, model_ids, n=max_suggestions, cutoff=0.3
        )

        # Also check if the search term appears in model ID or name
        search_term = model_name.lower()
        keyword_matches = [
            m for m in model_list if search_term in m[0].lower() or search_term in m[1].lower()
        ]

        # Combine and deduplicate results
        result_models = []
        seen_ids = set()

        # First add close matches
        for match_id in close_matches:
            for model_id, model_name_str, model_data in model_list:
                if model_id == match_id and model_id not in seen_ids:
                    result_models.append(model_data)
                    seen_ids.add(model_id)
                    break

        # Then add keyword matches
        for model_id, model_name_str, model_data in keyword_matches:
            if model_id not in seen_ids and len(result_models) < max_suggestions:
                result_models.append(model_data)
                seen_ids.add(model_id)

        return result_models[:max_suggestions]

    def chat(
        self,
        message: str,
        pricing_method: str = "balance",
        model: Optional[str] = None,
        models: Optional[List[str]] = None,
        quantity: Optional[int] = None,
        show_animation: bool = True,
    ) -> Dict:
        """
        Send a chat message to Straico API using smart LLM selector or specific model(s).

        Args:
            message: The user's message/prompt
            pricing_method: Pricing method - "quality", "balance", or "budget"
            model: Optional single specific model to use (overrides smart_llm_selector)
            models: Optional list of models to query simultaneously (v1 only)
            quantity: Number of models to select with smart_llm_selector (v1 only, must be between 1 and 4)
            show_animation: Whether to show loading animation (default: True)

        Returns:
            API response dictionary
        """
        # Validate quantity parameter
        if quantity is not None and (quantity < 1 or quantity > 4):
            return {
                "success": False,
                "error": f"Quantity must be between 1 and 4 (got {quantity})",
            }

        payload = {"message": message, "replace_failed_models": True}

        # Priority: models list > single model > smart_llm_selector
        if models and len(models) > 0:
            # v1: Multiple models explicitly specified
            payload["models"] = models
        elif model:
            # Single model (works in both v0 and v1)
            if self.api_version == "v1":
                payload["models"] = [model]
            else:
                payload["model"] = model
        else:
            # smart_llm_selector
            if self.api_version == "v1" and quantity and quantity > 1:
                # v1: smart_llm_selector with quantity (multiple models)
                payload["smart_llm_selector"] = {
                    "quantity": quantity,
                    "pricing_method": pricing_method,
                }
            elif self.api_version == "v1":
                # v1: smart_llm_selector (single model)
                payload["smart_llm_selector"] = {
                    "quantity": 1,
                    "pricing_method": pricing_method,
                }
            else:
                # v0: smart_llm_selector (string format)
                payload["smart_llm_selector"] = pricing_method

        # Start loading animation
        animation = None
        if show_animation:
            animation = LoadingAnimation("Thinking")
            animation.start()

        try:
            response = requests.post(
                f"{self.base_url}/prompt/completion", headers=self.headers, json=payload
            )
            response.raise_for_status()
            result = response.json()
            return result
        except requests.exceptions.RequestException as e:
            # Check if it's a model not found error
            error_msg = str(e)
            if response is not None and response.status_code == 422:
                try:
                    error_data = response.json()
                    api_error = error_data.get("error", "")
                    
                    # Check for model not found error
                    if "Model not found" in api_error:
                        # Determine which model(s) were requested
                        requested_model = None
                        if model:
                            # Single model specified
                            requested_model = model
                        elif models and len(models) == 1:
                            # Single model in models list
                            requested_model = models[0]
                        elif models and len(models) > 1:
                            # Multiple models - try to extract the problematic one from error message
                            # The API error might contain the specific model name
                            for m in models:
                                if m in api_error:
                                    requested_model = m
                                    break
                            # If we can't identify the specific model, use the first one as fallback
                            if not requested_model:
                                requested_model = models[0]
                        
                        if requested_model:
                            # Find similar models for suggestions
                            similar_models = self.find_similar_models(requested_model)
                            return {
                                "success": False,
                                "error": api_error,
                                "model_not_found": True,
                                "requested_model": requested_model,
                                "suggestions": similar_models,
                            }
                except:
                    pass

            return {"success": False, "error": error_msg}
        finally:
            # Stop loading animation
            if animation:
                animation.stop()

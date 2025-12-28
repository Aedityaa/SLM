"""Wolfram Alpha API integration for advanced computations"""
import requests
import urllib.parse
from src.tools.base_tool import BaseTool
from typing import Dict, Any, Optional

class WolframAlphaTool(BaseTool):
    """Query Wolfram Alpha for complex math, science, and real-world data"""
    
    def __init__(self, app_id: Optional[str] = None):
        super().__init__(
            name="wolfram_alpha",
            description="Query Wolfram Alpha for complex math, physics, chemistry, real-world data, unit conversions, and scientific computations"
        )
        self.app_id = app_id
        self.base_url = "http://api.wolframalpha.com/v2/query"
        
        if not self.app_id:
            print("⚠️  Wolfram Alpha: No API key provided. Tool will be non-functional.")
            print("   Get your free API key at: https://products.wolframalpha.com/api/")
    
    def validate_input(self, query: str = None, **kwargs) -> bool:
        """Validate that query exists and API key is configured"""
        if not query:
            return False
        if not self.app_id or self.app_id == "YOUR_APP_ID_HERE":
            print("❌ Wolfram Alpha API key not configured")
            return False
        return True
    
    def execute(self, query: str, format: str = "plaintext", **kwargs) -> Dict[str, Any]:
        """
        Query Wolfram Alpha API
        
        Args:
            query: Natural language query (e.g., "integrate x^2 from 0 to 5")
            format: Output format - 'plaintext', 'image', or 'both'
        
        Returns:
            Dictionary with results, images, and metadata
        """
        params = {
            'input': query,
            'appid': self.app_id,
            'output': 'json',
            'format': 'plaintext,image',  # Get both text and images
            'podstate': 'Step-by-step solution',  # Request step-by-step if available
        }
        
        try:
            print(f"🔍 Querying Wolfram Alpha: {query}")
            response = requests.get(self.base_url, params=params, timeout=15)
            
            if response.status_code != 200:
                return {
                    "query": query,
                    "error": f"API request failed with status {response.status_code}",
                    "success": False
                }
            
            data = response.json()
            
            # Parse results
            if 'queryresult' not in data:
                return {
                    "query": query,
                    "error": "Invalid API response",
                    "success": False
                }
            
            query_result = data['queryresult']
            
            if not query_result.get('success'):
                return {
                    "query": query,
                    "error": query_result.get('error', {}).get('msg', 'Query failed'),
                    "suggestions": query_result.get('didyoumeans', {}).get('didyoumean', []),
                    "success": False
                }
            
            # Extract pods (result sections)
            results = []
            images = []
            
            for pod in query_result.get('pods', []):
                pod_title = pod.get('title', 'Result')
                
                for subpod in pod.get('subpods', []):
                    # Get plaintext
                    plaintext = subpod.get('plaintext', '')
                    
                    # Get image if available
                    img = subpod.get('img', {})
                    if img and img.get('src'):
                        images.append({
                            'title': pod_title,
                            'url': img['src'],
                            'alt': img.get('alt', '')
                        })
                    
                    if plaintext:
                        results.append({
                            'title': pod_title,
                            'result': plaintext
                        })
            
            return {
                "query": query,
                "results": results,
                "images": images,
                "success": len(results) > 0,
                "pods_count": len(query_result.get('pods', [])),
                "timing": query_result.get('timing', 0)
            }
        
        except requests.Timeout:
            return {
                "query": query,
                "error": "Request timeout (server took too long to respond)",
                "success": False
            }
        
        except requests.RequestException as e:
            return {
                "query": query,
                "error": f"Network error: {str(e)}",
                "success": False
            }
        
        except Exception as e:
            return {
                "query": query,
                "error": f"Unexpected error: {str(e)}",
                "success": False
            }
    
    def format_result(self, result: Dict[str, Any]) -> str:
        """Format Wolfram Alpha results for model injection"""
        if not result.get('success'):
            error_msg = result.get('error', 'Unknown error')
            suggestions = result.get('suggestions', [])
            
            formatted = f"❌ Wolfram Alpha Error: {error_msg}"
            
            if suggestions:
                formatted += f"\n\nDid you mean: {', '.join(suggestions[:3])}"
            
            return formatted
        
        # Format successful results
        formatted = f"✅ Wolfram Alpha results for: '{result['query']}'\n\n"
        
        for i, res in enumerate(result['results'], 1):
            formatted += f"[{res['title']}]\n{res['result']}\n\n"
        
        # Add image info if available
        if result.get('images'):
            formatted += f"📊 Generated {len(result['images'])} visualization(s)\n"
        
        formatted += f"⏱️ Query time: {result.get('timing', 0)}s"
        
        return formatted.strip()
    
    def get_step_by_step(self, query: str) -> Dict[str, Any]:
        """
        Try to get step-by-step solution
        
        Args:
            query: Math problem query
        """
        # Wolfram Alpha provides step-by-step for Pro API only
        # This is a wrapper that attempts to extract steps from results
        result = self.execute(query)
        
        if not result.get('success'):
            return result
        
        # Look for step-by-step pods
        steps = []
        for res in result.get('results', []):
            if 'step' in res['title'].lower() or 'solution' in res['title'].lower():
                steps.append(res)
        
        result['steps'] = steps
        return result
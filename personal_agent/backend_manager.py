import json
import re
from pathlib import Path
from typing import Dict, Any, Optional

class BackendPromptManager:
    """Dedicated prompt management system for backend operations"""
    
    def __init__(self, prompts_dir: Optional[Path] = None):
        # Adjust path to match your structure: prompts/backend/
        if prompts_dir is None:
            current_file = Path(__file__).resolve()
            # From root directory, go into prompts/backend/
            self.prompts_dir = current_file.parent / "prompts" / "backend"
        else:
            self.prompts_dir = prompts_dir
            
        self._prompt_cache: Dict[str, str] = {}
        self._ensure_prompts_dir()
    
    def _ensure_prompts_dir(self):
        """Ensure prompts directory exists"""
        if not self.prompts_dir.exists():
            raise FileNotFoundError(f"Backend prompts directory not found: {self.prompts_dir}")
        print(f"📁 Using backend prompts from: {self.prompts_dir}")
    
    def load_prompt(self, prompt_name: str) -> str:
        """Load prompt from file with caching"""
        if prompt_name not in self._prompt_cache:
            prompt_file = self.prompts_dir / f"{prompt_name}.txt"
            if not prompt_file.exists():
                raise FileNotFoundError(f"Backend prompt file not found: {prompt_file}")
            
            self._prompt_cache[prompt_name] = prompt_file.read_text(encoding="utf-8")
            print(f"📄 Loaded backend prompt: {prompt_name}")
        
        return self._prompt_cache[prompt_name]
    
    def format_prompt(self, prompt_name: str, **kwargs) -> str:
        """Load and format prompt with variables"""
        template = self.load_prompt(prompt_name)
        try:
            return template.format(**kwargs)
        except KeyError as e:
            raise ValueError(f"Missing required variable {e} for backend prompt {prompt_name}")
    
    def reload_prompts(self):
        """Clear cache to reload prompts from files"""
        self._prompt_cache.clear()
        print("🔄 Backend prompt cache cleared - will reload from files")
    
    def list_available_prompts(self) -> list:
        """List all available backend prompt files"""
        return [f.stem for f in self.prompts_dir.glob("*.txt")]


class BackendJSONParser:
    """Robust JSON parser specifically for backend LLM responses"""
    
    @staticmethod
    def parse_gemini_json(response_text: str) -> list:
        """Parse JSON from Gemini responses with comprehensive error handling"""
        
        def clean_text(text: str) -> str:
            return text.strip().replace('\r\n', '\n').replace('\r', '\n')
        
        def extract_from_markdown(text: str) -> str:
            """Extract JSON from markdown code blocks - FIXED VERSION"""
            # Remove the opening markdown
            if text.startswith('```json'):
                text = text[7:]  # Remove ```
            elif text.startswith('```'):
                text = text[3:]  # Remove ```
            
            # Remove the closing markdown
            if text.endswith('```'):
                text = text[:-3]  # Remove trailing ```
            
            # Clean up any remaining newlines
            text = text.strip()
            
            return text
        
        def fix_common_json_issues(text: str) -> str:
            """Fix common JSON formatting issues"""
            # Remove trailing commas before closing braces/brackets
            text = re.sub(r',(\s*[}$$])', r'\1', text)
            # Fix single quotes to double quotes for keys
            text = re.sub(r"'([^']*)'(\s*:)", r'"\1"\2', text)
            # Remove any extra whitespace
            text = text.strip()
            return text
        
        def parse_with_fallbacks(text: str):
            """Try multiple parsing strategies"""
            strategies = [
                lambda x: json.loads(x),  # Direct parsing
                lambda x: json.loads(fix_common_json_issues(x)),  # With fixes
            ]
            
            for i, strategy in enumerate(strategies):
                try:
                    result = strategy(text)
                    print(f"✅ JSON parsed successfully with strategy {i+1}")
                    return result if isinstance(result, list) else [result]
                except json.JSONDecodeError as e:
                    print(f"⚠️ Strategy {i+1} failed: {e}")
                    continue
                except Exception as e:
                    print(f"⚠️ Strategy {i+1} error: {e}")
                    continue
            return None
        
        try:
            print(f"🔍 Raw response text: {repr(response_text[:200])}")  # Debug log
            
            cleaned_text = clean_text(response_text)
            
            # Extract from markdown if present
            if '```' in cleaned_text:
                print("📝 Extracting from markdown...")
                cleaned_text = extract_from_markdown(cleaned_text)
                print(f"📝 Extracted text: {repr(cleaned_text[:200])}")
            
            # Try parsing
            result = parse_with_fallbacks(cleaned_text)
            
            if result is not None:
                print("✅ Successfully parsed backend JSON:", result)
                return result
            
            print("⚠️ All parsing strategies failed")
            print(f"⚠️ Final cleaned text was: {repr(cleaned_text)}")
            return [{"action": "none", "reason": "json_parsing_failed"}]
            
        except Exception as e:
            print(f"⚠️ Critical backend JSON parsing error: {e}")
            print(f"⚠️ Raw input was: {repr(response_text)}")
            return [{"action": "none", "reason": f"parsing_error: {str(e)}"}]


# Global backend instances
backend_prompt_manager = BackendPromptManager()
backend_json_parser = BackendJSONParser()

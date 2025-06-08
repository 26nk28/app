import asyncio
import json
from typing import List, Dict
from langchain_google_genai import ChatGoogleGenerativeAI
from ..utils.config import GEMINI_API_KEY

class MealRecommender:
    """AI-powered meal recommendation engine for groups"""
    
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(
            api_key=GEMINI_API_KEY,
            model="gemini-2.5-flash-preview-05-20",
            temperature=0.3
        )
    
    async def recommend_meals(self, aggregated_data: Dict, group_id: str) -> List[Dict]:
        """Generate 4 meal recommendations for the group"""
        print(f"🤖 Generating AI meal recommendations for group {group_id[:8]}...")
        
        # Create recommendation prompt
        prompt = self._create_recommendation_prompt(aggregated_data)
        
        try:
            response = await self.llm.ainvoke(prompt)
            meal_suggestions = self._parse_meal_response(response.content)
            
            # Enhance suggestions with compatibility info
            enhanced_suggestions = []
            for suggestion in meal_suggestions:
                enhanced = await self._enhance_suggestion_with_compatibility(
                    suggestion, aggregated_data
                )
                enhanced_suggestions.append(enhanced)
            
            return enhanced_suggestions[:4]  # Return top 4
            
        except Exception as e:
            print(f"❌ Error generating meal recommendations: {e}")
            return self._get_fallback_recommendations()
    
    def _create_recommendation_prompt(self, data: Dict) -> str:
        """Create AI prompt for meal recommendations"""
        
        # Extract key information
        combined_prefs = data['combined_preferences']
        restrictions = data['dietary_restrictions']
        calendar_patterns = data['group_calendar_patterns']
        
        prompt = f"""
You are a professional nutritionist and meal planner. Create 4 diverse meal recommendations for a group of {len(data['group_personas'])} people.

GROUP PREFERENCES:
- Likes: {combined_prefs.get('likes', [])}
- Dislikes: {combined_prefs.get('dislikes', [])}
- Allergies: {combined_prefs.get('allergies', [])}
- Dietary Restrictions: {combined_prefs.get('dietary_restrictions', [])}

DIETARY RESTRICTIONS BY MEMBER:
{json.dumps(restrictions, indent=2)}

EATING PATTERNS:
{json.dumps(calendar_patterns, indent=2)}

REQUIREMENTS:
1. Each meal must be safe for ALL group members (respect all allergies and restrictions)
2. Include variety in cuisine types and cooking methods
3. Consider different difficulty levels (easy to moderate)
4. Provide balanced nutrition
5. Include preparation time estimates

RESPOND WITH EXACTLY 4 MEAL SUGGESTIONS IN THIS JSON FORMAT:
[
  {{
    "name": "Meal Name",
    "description": "Brief description",
    "ingredients": ["ingredient1", "ingredient2", "..."],
    "cuisine_type": "Italian/Asian/etc",
    "prep_time": 30,
    "difficulty": "easy/medium/hard",
    "dietary_tags": ["vegetarian", "gluten-free", "etc"],
    "nutrition_highlights": ["high protein", "low carb", "etc"],
    "cooking_method": "baking/stir-fry/etc"
  }}
]

RESPOND ONLY WITH THE JSON ARRAY:
"""
        return prompt
    
    def _parse_meal_response(self, response_content: str) -> List[Dict]:
        """Parse AI response into meal suggestions"""
        try:
            # Clean response content
            content = response_content.strip()
            
            # Remove markdown formatting if present
            if content.startswith("```"):
                content = content[7:]
            if content.startswith('```'):
                content = content[3:]
            if content.endswith('```'):
                content = content[:-3]
            
            content = content.strip()
            
            # Parse JSON
            meals = json.loads(content)
            
            if isinstance(meals, list) and len(meals) > 0:
                return meals
            else:
                print("⚠️ Invalid meal response format")
                return self._get_fallback_recommendations()
                
        except json.JSONDecodeError as e:
            print(f"⚠️ Failed to parse meal recommendations: {e}")
            print(f"Raw response: {response_content[:200]}...")
            return self._get_fallback_recommendations()
    
    async def _enhance_suggestion_with_compatibility(self, suggestion: Dict, data: Dict) -> Dict:
        """Enhance meal suggestion with group compatibility information"""
        
        # Check which members can eat this meal
        compatible_members = []
        incompatible_reasons = {}
        
        for member_data in data['group_personas']:
            user_id = member_data['user_id']
            persona = member_data['persona']
            
            is_compatible, reasons = self._check_meal_compatibility(suggestion, persona)
            
            if is_compatible:
                compatible_members.append(user_id)
            else:
                incompatible_reasons[user_id] = reasons
        
        # Add compatibility information
        suggestion['compatible_members'] = compatible_members
        suggestion['incompatible_reasons'] = incompatible_reasons
        suggestion['compatibility_score'] = len(compatible_members) / len(data['group_personas'])
        
        return suggestion
    
    def _check_meal_compatibility(self, meal: Dict, persona: Dict) -> tuple:
        """Check if a meal is compatible with a member's restrictions"""
        incompatible_reasons = []
        
        meal_ingredients = [ing.lower() for ing in meal.get('ingredients', [])]
        meal_tags = [tag.lower() for tag in meal.get('dietary_tags', [])]
        
        # Check allergies
        allergies = [allergy.lower() for allergy in persona.get('allergies', [])]
        for allergy in allergies:
            if any(allergy in ingredient for ingredient in meal_ingredients):
                incompatible_reasons.append(f"Contains allergen: {allergy}")
        
        # Check dietary restrictions
        restrictions = [rest.lower() for rest in persona.get('dietary_restrictions', [])]
        for restriction in restrictions:
            if restriction == 'vegetarian' and any(meat in ' '.join(meal_ingredients) for meat in ['chicken', 'beef', 'pork', 'fish']):
                incompatible_reasons.append("Contains meat (vegetarian restriction)")
            elif restriction == 'vegan' and any(animal in ' '.join(meal_ingredients) for animal in ['milk', 'cheese', 'egg', 'butter', 'chicken', 'beef']):
                incompatible_reasons.append("Contains animal products (vegan restriction)")
        
        # Check dislikes (less strict)
        dislikes = persona.get('preferences', {}).get('dislikes', [])
        for dislike in dislikes:
            if dislike.lower() in ' '.join(meal_ingredients):
                incompatible_reasons.append(f"Contains disliked ingredient: {dislike}")
        
        return len(incompatible_reasons) == 0, incompatible_reasons
    
    def _get_fallback_recommendations(self) -> List[Dict]:
        """Provide fallback meal recommendations if AI fails"""
        return [
            {
                "name": "Mediterranean Quinoa Bowl",
                "description": "Healthy quinoa with vegetables and olive oil dressing",
                "ingredients": ["quinoa", "cucumber", "tomatoes", "olive oil", "lemon", "herbs"],
                "cuisine_type": "Mediterranean",
                "prep_time": 25,
                "difficulty": "easy",
                "dietary_tags": ["vegetarian", "gluten-free", "healthy"],
                "nutrition_highlights": ["high protein", "fiber rich"],
                "cooking_method": "boiling and mixing"
            },
            {
                "name": "Vegetable Stir Fry",
                "description": "Quick and healthy mixed vegetable stir fry",
                "ingredients": ["mixed vegetables", "soy sauce", "garlic", "ginger", "oil"],
                "cuisine_type": "Asian",
                "prep_time": 15,
                "difficulty": "easy",
                "dietary_tags": ["vegetarian", "quick"],
                "nutrition_highlights": ["vitamin rich", "low calorie"],
                "cooking_method": "stir-frying"
            },
            {
                "name": "Pasta Primavera",
                "description": "Light pasta with seasonal vegetables",
                "ingredients": ["pasta", "zucchini", "bell peppers", "olive oil", "herbs"],
                "cuisine_type": "Italian",
                "prep_time": 20,
                "difficulty": "easy",
                "dietary_tags": ["vegetarian"],
                "nutrition_highlights": ["carbohydrates", "vegetables"],
                "cooking_method": "boiling and sautéing"
            },
            {
                "name": "Green Salad with Protein",
                "description": "Fresh salad with choice of protein",
                "ingredients": ["mixed greens", "tomatoes", "cucumber", "dressing"],
                "cuisine_type": "International",
                "prep_time": 10,
                "difficulty": "easy",
                "dietary_tags": ["healthy", "fresh"],
                "nutrition_highlights": ["vitamins", "low calorie"],
                "cooking_method": "no cooking required"
            }
        ]

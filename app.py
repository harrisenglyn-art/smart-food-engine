import streamlit as pd
import streamlit as st
import requests

def get_recipe_details(recipe_id):
    """Fetches full recipe metadata explicitly containing instruction step matrices."""
    SPOONACULAR_API_KEY = st.secrets.get("SPOONACULAR_API_KEY", "").strip()
    url = f"https://spoonacular.com{recipe_id}/information"
    params = {"apiKey": SPOONACULAR_API_KEY}
    try:
        response = requests.get(url, params=params)
        return response.json()
    except Exception as e:
        return {}

def search_recipes_by_ingredients(ingredients_string):
    """Fetches matching recipes from Spoonacular based on matching raw text lists."""
    SPOONACULAR_API_KEY = st.secrets.get("SPOONACULAR_API_KEY", "").strip()
    url = "https://spoonacular.comfindByIngredients"
    params = {
        "apiKey": SPOONACULAR_API_KEY,
        "ingredients": ingredients_string,
        "number": 5
    }
    try:
        response = requests.get(url, params=params)
        return response.json()
    except Exception as e:
        st.error(f"Error fetching recipe database query: {e}")
        return []
# Initialize session memory arrays securely
if "recipes" not in st.session_state:
    st.session_state.recipes = []

# --- 6. MAIN APP INTERFACE LAYER ---
# Adjust this container logic block level if you utilize an outer onboarding auth flow
st.title("🍳 Smart Food Recommendation Engine")
st.write("Solve your daily food dilemma instantly. Tell us what you're craving!")

# --- TWO INITIAL OPTIONS: THE TOP NAVIGATION TABS ---
tab_cook, tab_go_out = st.tabs(["🔍 Cook at Home", "🚗 Go Out to Eat"])
# =============================================================================
# 🔍 TAB 1: COOK AT HOME
# =============================================================================
with tab_cook:
    st.header("Cook a Perfect Meal")
    
    user_ingredients = st.text_input(
        "Enter your available ingredients (separated by commas):", 
        key="ingredients_input"
    )

    col1, col2 = st.columns(2)
    with col1:
        cuisine_cook = st.selectbox("Cuisine Choice", ["Any", "Italian", "Mexican", "Asian", "American", "Mediterranean"])
        mood_cook = st.selectbox("Current Mood", ["Comfort Food", "Quick & Easy", "Healthy & Light", "Cozy"], key="m_cook")
    with col2:
        health_goal = st.selectbox("Dietary Targets", ["None", "Gluten Free", "Ketogenic", "Vegan", "Vegetarian"], key="h_goal")
        servings = st.number_input("Number of Servings Needed", min_value=1, max_value=20, value=2, step=1, key="s_cook")

    max_time = st.slider("Max Prep/Cooking Time (Minutes)", min_value=10, max_value=120, value=60, step=5, key="t_c")
    # # 1. Unified User Search Trigger Engine
    if st.button("Generate Home Recipes", type="primary", key="cook_tab_primary_generator"):
        if not user_ingredients:
            st.warning("Please input ingredients to match!")
        else:
            SPOONACULAR_API_KEY = st.secrets.get("SPOONACULAR_API_KEY", "").strip()
            
            if not SPOONACULAR_API_KEY:
                st.error("🛑 Connection Aborted: Your Spoonacular API Key is missing or unconfigured in your Cloud Settings panel!")
            else:
                with st.spinner("Searching and parsing recipe instructions..."):
                    raw_results = search_recipes_by_ingredients(user_ingredients)
                    
                    hydrated_recipes = []
                    for item in raw_results:
                        full_detail = get_recipe_details(item["id"])
                        if full_detail:
                            hydrated_recipes.append(full_detail)
                    
                    st.session_state.recipes = hydrated_recipes

    # Render Active Hydrated Cards Below Search Operation
    if st.session_state.recipes:
        for recipe in st.session_state.recipes:
            with st.expander(f"📖 {recipe.get('title', 'Unknown Recipe')}"):
                if recipe.get("image"):
                    st.image(recipe["image"])
                
                st.markdown("### 📋 Step-by-Step Instructions")
                analyzed = recipe.get("analyzedInstructions")
                
                if analyzed and isinstance(analyzed, list) and len(analyzed) > 0:
                    steps = analyzed[0].get("steps", [])
                    if steps:
                        for step in steps:
                            st.write(f"**Step {step.get('number')}:** {step.get('step')}")
                    else:
                        st.write("Directions are missing structural data rows.")
                elif recipe.get("instructions"):
                    st.write(recipe["instructions"])
                else:
                    st.write("Mix ingredients well and cook thoroughly according to taste!")
# =============================================================================
# 🚗 TAB 2: GO OUT TO EAT
# =============================================================================
with tab_go_out:
    st.header("Order Take Out or Delivery")
    st.write("Find excellent choices nearby to satisfy your cravings without cooking!")
    
    # 🟢 PLACE ALL YOUR TAKE OUT INPUT PARAMETERS & MAP INTERACTION CODE DIRECTLY HERE
    takeout_zip = st.text_input("Enter Delivery ZIP Code or Address:", key="takeout_location_tracker")
    cuisine_takeout = st.selectbox("What food type are you hunting?", ["Any", "Burgers", "Pizza", "Sushi", "Thai", "Tacos"], key="t_cuisine")
    
    st.info("Restaurant recommendations mapping modules will deploy securely right inside this panel area.")

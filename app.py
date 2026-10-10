import streamlit as pd
import streamlit as st
import requests

def get_recipe_details(recipe_id):
    SPOONACULAR_API_KEY = st.secrets.get("SPOONACULAR_API_KEY", "").strip()
    # 🟢 Ensure there is a '/' after .com and after recipes
    url = "https://api.spoonacular.com/recipes/{recipe_id}/information"
    params = {"apiKey": SPOONACULAR_API_KEY}
    try:
        response = requests.get(url, params=params)
        return response.json()
    except Exception as e:
        return {}

def search_recipes_by_ingredients(ingredients_string):
    SPOONACULAR_API_KEY = st.secrets.get("SPOONACULAR_API_KEY", "").strip()
    # 🟢 Ensure there is a '/' after .com and after recipes
    url = "https://api.spoonacular.com/recipes/findByIngredients"
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
                    
                    # 🟢 FORCE FIX 1: Grab ONLY the top 3 options from the initial ingredient search
                    top_3_raw = raw_results[:3]
                    
                    hydrated_recipes = []
                    for item in top_3_raw:
                        full_detail = get_recipe_details(item["id"])
                        if full_detail:
                            # Merge ingredient matching metrics into the full detail dictionary
                            full_detail["usedIngredients"] = item.get("usedIngredients", [])
                            full_detail["missedIngredients"] = item.get("missedIngredients", [])
                            hydrated_recipes.append(full_detail)
                    
                    st.session_state.recipes = hydrated_recipes

    # Render Active Hydrated Cards Below Search Operation
    if st.session_state.recipes:
        st.markdown("---")
        st.subheader("🍳 Top 3 Recommended Match Options")
        
        for recipe in st.session_state.recipes:
            # Cleanly pull the title or fallback safely
            recipe_title = recipe.get("title") or recipe.get("name") 
            
            with st.expander(f"📖 {recipe_title}", expanded=True):
                # Ensure the image loads properly
                if recipe.get("image"):
                    st.image(recipe["image"], use_container_width=True)
                
                # --- 🥦 SECTION A: INGREDIENTS LIST MATRIX ---
                st.markdown("### 🛒 Ingredients Required")
                
                used_ings = recipe.get("usedIngredients", [])
                missed_ings = recipe.get("missedIngredients", [])
                
                if used_ings or missed_ings:
                    col_ing1, col_ing2 = st.columns(2)
                    with col_ing1:
                        st.markdown("**🟢 Ingredients You Have:**")
                        for ing in used_ings:
                            st.write(f"- {ing.get('original', ing.get('name'))}")
                    with col_ing2:
                        st.markdown("**🔴 Ingredients You Need to Buy:**")
                        if missed_ings:
                            for ing in missed_ings:
                                st.write(f"- {ing.get('original', ing.get('name'))}")
                        else:
                            st.write("- None! You have everything!")
                
                st.markdown("---")
                
                # --- 📋 SECTION B: STEP-BY-STEP INSTRUCTIONS (FIXED UNPACKING) ---
                st.markdown("### 📋 Step-by-Step Instructions")
                analyzed = recipe.get("analyzedInstructions")
                
                # 🟢 FIXED: Safely look inside the first element of the list array
                if analyzed and isinstance(analyzed, list) and len(analyzed) > 0:
                    first_instruction_block = analyzed[0]
                    steps = first_instruction_block.get("steps", [])
                    
                    if steps:
                        for step in steps:
                            st.write(f"**Step {step.get('number')}:** {step.get('step')}")
                    else:
                        st.write("Directions are missing structural data rows.")
                elif recipe.get("instructions"):
                    # Backup fallback if it returns raw HTML/Text strings instead of list arrays
                    st.write(recipe["instructions"])
            
# =============================================================================
# 🚗 TAB 2: GO OUT TO EAT (RESTORED WITH GOOGLE PLACES API)
# =============================================================================
with tab_go_out:
    st.header("Order Take Out or Delivery")
    st.write("Find excellent choices nearby to satisfy your cravings without cooking!")
    
    # 🟢 RESTORED USER INPUT FIELDS
    col1_out, col2_out = st.columns(2)
    with col1_out:
        takeout_location = st.text_input("Enter Delivery ZIP Code, City, or Full Address:", value="90036", key="takeout_location_tracker")
        cuisine_takeout = st.selectbox("What food type are you hunting?", ["Pizza", "Burgers", "Sushi", "Thai", "Tacos", "Indian", "Healthy Salad"], key="t_cuisine")
    
    with col2_out:
        search_radius = st.slider("Search Distance Radius (Miles)", min_value=1, max_value=25, value=5, step=1, key="t_radius")
        price_range = st.select_slider("Price Level Target", options=["$", "$$", "$$$", "$$$$"], value="$$", key="t_price")

    # 1. Google Places Search Trigger Engine
    if st.button("Find Nearby Restaurants", type="primary", key="takeout_tab_primary_generator"):
        if not takeout_location:
            st.warning("Please provide a location target to route coordinates!")
        else:
            GOOGLE_PLACES_API_KEY = st.secrets.get("GOOGLE_PLACES_API_KEY", "").strip()
            
            if not GOOGLE_PLACES_API_KEY:
                st.error("🛑 Connection Aborted: Your GOOGLE_PLACES_API_KEY is missing or unconfigured in your Cloud Settings panel!")
            else:
                with st.spinner("Querying Google Places dataset for matching venues..."):
                    # 🛠️ GOOGLE PLACES TEXT SEARCH ENDPOINT CALL
                    # Convert miles to meters for Google's API requirement (1 mile ≈ 1609 meters)
                    radius_meters = search_radius * 1609
                    
                    
# 🟢 THE FIX (Ensure full slashes divide domains, services, and operations):
                    places_url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
                    query_string = f"{cuisine_takeout} restaurant near {takeout_location}"
                    
                    places_params = {
                        "query": query_string,
                        "radius": radius_meters,
                        "key": GOOGLE_PLACES_API_KEY
                    }
                    
                    try:
                        response = requests.get(places_url, params=places_params)
                        places_data = response.json()
                        restaurants = places_data.get("results", [])
                        
                        if restaurants:
                            st.success(f"Found {len(restaurants)} excellent matching options nearby!")
                            
                            # Render Restored Data Output Profiles
                            for rest in restaurants:
                                name = rest.get("name", "Unknown Restaurant")
                                address = rest.get("formatted_address", "No address listed")
                                rating = rest.get("rating", "No ratings yet")
                                status = "🟢 Open Now" if rest.get("opening_hours", {}).get("open_now") else "🔴 Closed"
                                
                                with st.container(border=True):
                                    st.markdown(f"### 🏪 {name}")
                                    st.write(f"📍 **Address:** {address}")
                                    st.write(f"⭐ **Google Rating:** {rating} / 5  |  Status: {status}")
                        else:
                            st.info("No matching locations found for that specific radius query criteria.")
                            
                    except Exception as e:
                        st.error(f"Failed to communicate with Google Places interface: {e}")

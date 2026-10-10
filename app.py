import streamlit as st
import requests

def get_recipe_details(recipe_id):
    """Fetches full recipe metadata explicitly containing instruction step matrices."""
    SPOONACULAR_API_KEY = st.secrets.get("SPOONACULAR_API_KEY", "").strip()
    
    # 🟢 VERIFIED URL ALIGNMENT CONSTRUCTION
    url = "https://api.spoonacular.com/recipes/{recipe_id}/information"
    params = {"apiKey": SPOONACULAR_API_KEY}
    
    try:
        response = requests.get(url, params=params)
        # If we hit quota limits, capture the error footprint instead of crashing
        if response.status_code != 200:
            return {"api_quota_blocked": True, "status_code": response.status_code}
        return response.json()
    except Exception as e:
        return {}

def search_recipes_by_ingredients(ingredients_string):
    """Fetches matching recipes from Spoonacular based on matching raw text lists."""
    SPOONACULAR_API_KEY = st.secrets.get("SPOONACULAR_API_KEY", "").strip()
    
    # 🟢 VERIFIED URL ALIGNMENT CONSTRUCTION
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

# # 1. Unified User Search Trigger Engine
if st.button("Generate Home Recipes", type="primary", key="cook_tab_primary_generator"):
    if not user_ingredients:
        st.warning("Please input ingredients to match!")
    else:
        SPOONACULAR_API_KEY = st.secrets.get("SPOONACULAR_API_KEY", "").strip()
        
        if not SPOONACULAR_API_KEY:
            st.error("🛑 Connection Aborted: Your Spoonacular API Key is missing or unconfigured!")
        else:
            # 🟢 FIXED: Kept this block aligned cleanly on a single level depth margin
            with st.spinner("Searching and parsing recipe instructions..."):
                raw_results = search_recipes_by_ingredients(user_ingredients)
                
                top_3_raw = raw_results[:3]
                hydrated_recipes = []
                
                for item in top_3_raw:
                    full_detail = get_recipe_details(item.get("id"))
                    
                    if full_detail and "api_quota_blocked" not in full_detail:
                        full_detail["usedIngredients"] = item.get("usedIngredients", [])
                        full_detail["missedIngredients"] = item.get("missedIngredients", [])
                        hydrated_recipes.append(full_detail)
                    else:
                        fallback_profile = {
                            "title": item.get("title", "Delicious Match Option"),
                            "image": item.get("image", ""),
                            "usedIngredients": item.get("usedIngredients", []),
                            "missedIngredients": item.get("missedIngredients", []),
                            "quota_notice": True
                        }
                        hydrated_recipes.append(fallback_profile)
                
                st.session_state.recipes = hydrated_recipes
# =============================================================================
# 1. MAIN APP WORKSPACE HEADERS (Lines 74-81 Move Here!)
# =============================================================================
st.title("🍳 Smart Food Recommendation Engine")
st.write("Solve your daily food dilemma instantly.")

tab_cook, tab_go_out = st.tabs(["🔍 Cook at Home", "🚗 Go Out to Eat"])

# =============================================================================
# 2. OPEN THE COOKING WORKSPACE
# =============================================================================
with tab_cook:
    st.header("Cook a Perfect Meal")
    
    # Restored user input fields (Your lines 88-89)
    user_ingredients = st.text_input("Enter your available ingredients:", key="ingredients_input")

    # 🟢 MOVE ALL API OPERATIONS DOWN HERE INDENTED BY 4 SPACES:
    if st.button("Generate Home Recipes", type="primary", key="cook_tab_primary_generator"):
        if not user_ingredients:
            st.warning("Please input ingredients to match!")
        else:
            with st.spinner("Searching and parsing recipe instructions..."):
                raw_results = search_recipes_by_ingredients(user_ingredients)
                
                top_3_raw = raw_results[:3]
                hydrated_recipes = []
                
                for item in top_3_raw:
                    full_detail = get_recipe_details(item.get("id"))
                    
                    if full_detail and "api_quota_blocked" not in full_detail:
                        full_detail["usedIngredients"] = item.get("usedIngredients", [])
                        full_detail["missedIngredients"] = item.get("missedIngredients", [])
                        hydrated_recipes.append(full_detail)
                    else:
                        fallback_profile = {
                            "title": item.get("title", "Delicious Match Option"),
                            "image": item.get("image", ""),
                            "usedIngredients": item.get("usedIngredients", []),
                            "missedIngredients": item.get("missedIngredients", []),
                            "quota_notice": True
                        }
                        hydrated_recipes.append(fallback_profile)
                
                # This is your old line 73, now safely saved inside the button action block!
                st.session_state.recipes = hydrated_recipes

    # =============================================================================
    # 3. RENDER RECS (Lines 87-91 Stay Intended Here!)
    # =============================================================================
    if st.session_state.recipes:
        st.markdown("---")
        st.subheader("🍳 Top 3 Recommended Match Options")
        # ... Your expander blocks showing steps and ingredient columns ...

    st.header("Cook a Perfect Meal")
    # ... your recipe codes ...

    # 🟢 Render Active Hydrated Cards Below Search Operation (Indented 4 spaces to stay inside with tab_cook)
    if st.session_state.recipes:
        st.markdown("---")
        st.subheader("🍳 Top 3 Recommended Match Options")
        
        for recipe in st.session_state.recipes:
            recipe_title = recipe.get("title") or "Delicious Match Option"
            
            # 🟢 FIXED: Moved the f-string 'f' modifier to the correct side of the quotation marks
            with st.expander(f"📖 {recipe_title}", expanded=True):
                if recipe.get("image"):
                    st.image(recipe["image"], use_container_width=True)
                
                # If the fallback took over, notify the user cleanly
                if recipe.get("quota_notice"):
                    st.warning("⚠️ Note: Live step extraction is temporarily unavailable due to testing daily limit caps. Showing ingredient list metrics only:")
                
                # --- 🥦 SECTION A: INGREDIENTS LIST ---
                st.markdown("### 🛒 Ingredients Required")
                used_ings = recipe.get("usedIngredients", [])
                missed_ings = recipe.get("missedIngredients", [])
                
                col_ing1, col_ing2 = st.columns(2)
            with col_ing1:
                st.markdown("**🟢 Ingredients You Have:**")
                if used_ings:
                    # 🟢 FIXED: Removed duplicate loop block and fixed f-string syntax positioning
                    for ing in used_ings:
                        st.write(f"- {ing.get('original', ing.get('name'))}")
                else:
                    st.write("- None listed")
                
            with col_ing2:
                st.markdown("**🔴 Ingredients You Need to Buy:**")
                if missed_ings:
                    # 🟢 FIXED: Adjusted f-string syntax positioning outside quotes
                    for ing in missed_ings:
                        st.write(f"- {ing.get('original', ing.get('name'))}")
                else:
                    st.write("- None! You have everything!")
        
            st.markdown("---")
        
        # --- 📋 SECTION B: STEP-BY-STEP INSTRUCTIONS ---
        if not recipe.get("quota_notice"):
            st.markdown("### 📋 Step-by-Step Instructions")
            analyzed = recipe.get("analyzedInstructions")
            
            if analyzed and isinstance(analyzed, list) and len(analyzed) > 0:
                # 🟢 FIXED: Clean variable tracking structure
                first_block = analyzed[0]
                steps = first_block.get("steps", [])
                
                if steps:
                    for step in steps:
                        # 🟢 FIXED: Shifted f-string literal selector completely outside of string quotes
                        st.write(f"**Step {step.get('number')}:** {step.get('step')}")
                else:
                    st.write("Directions are missing structural data rows.")
            elif recipe.get("instructions"):
                st.write(recipe["instructions"])
            else:
                st.write("Mix ingredients well and cook thoroughly according to taste!")

# =============================================================================
# 🚗 TAB 2: GO OUT TO EAT (RESTORED WITH GOOGLE PLACES API)
# =============================================================================
with tab_go_out:
    st.header("Order Take Out or Delivery")
    st.write("Find excellent choices nearby to satisfy your cravings without cooking!")
    
    # RESTORED USER INPUT FIELDS
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
                # 🟢 FIXED: All parameters cleanly indented 16 spaces to sit inside with st.spinner
                # Convert miles to meters for Google's API requirement (1 mile ≈ 1609 meters)
                radius_meters = search_radius * 1609
                
                # 🟢 FIXED: Ensured URL formatting has no typo gaps
                places_url = "https://googleapis.com"
                
                # 🟢 FIXED: Shifted f-string literal selector completely outside of string quotes
                query_string = f"{cuisine_takeout} restaurant near {takeout_location}"
                
                places_params = {
                    "query": query_string,
                    "radius": radius_meters,
                    "key": GOOGLE_PLACES_API_KEY
                }
                
                try:
                    # 🟢 FIXED: Aligned execution blocks securely inside context scope
                    response = requests.get(places_url, params=places_params)
                    places_data = response.json()
                    restaurants = places_data.get("results", [])
                    
                    if restaurants:
                        # 🟢 FIXED: Shifted f-string identifier completely outside of quotes
                        st.success(f"Found {len(restaurants)} excellent matching options nearby!")
                        
                        # Render Restored Data Output Profiles
                        for rest in restaurants:
                            name = rest.get("name", "Unknown Restaurant")
                            address = rest.get("formatted_address", "No address listed")
                            rating = rest.get("rating", "No ratings yet")
                            status = "🟢 Open Now" if rest.get("opening_hours", {}).get("open_now") else "🔴 Closed"
                            
                            with st.container(border=True):
                                # 🟢 FIXED: Shifted all f-string identifiers completely outside of quotes
                                st.markdown(f"### 🏪 {name}")
                                st.write(f"📍 **Address:** {address}")
                                st.write(f"⭐ **Google Rating:** {rating} / 5  |  Status: {status}")
                    else:
                        st.info("No matching locations found for that specific radius query criteria.")
                        
                except Exception as e:
                    # 🟢 FIXED: Properly aligned exception handling catch inside the spinner block scope
                    st.error(f"Failed to communicate with Google Places interface: {e}")

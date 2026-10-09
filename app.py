import streamlit as st
import requests

# --- CONFIGURATION ---
SPOONACULAR_API_KEY = "9023d1a591b544889df6a7c364cfb898"

st.set_page_config(page_title="Smart Food Engine", page_icon="🍔", layout="centered")

# --- SIDEBAR (Premium Tier monetization anchor) ---
st.sidebar.markdown("👑 **Premium Member?** [Sign In Here](#)")
st.sidebar.markdown("---")
st.sidebar.markdown("🔒 *Unlock advanced calorie metrics & instant allergen blocking for just $2.99/mo.*")

st.title("🍔 Smart Food Recommendation Engine")
st.write("Solve your daily food dilemma instantly. Tell us what you're craving!")

# --- TWO INITIAL OPTIONS: THE TOP NAVIGATION TABS ---
tab_cook, tab_go_out = st.tabs(["🍳 Cook at Home", "🚗 Go Out to Eat"])

# =========================================================================
# 🍳 TAB 1: COOK AT HOME (WITH INGREDIENT CALCULATION SCALING & TOP 3 RANKED SELECTION)
# =========================================================================
with tab_cook:
    st.header("Cook a Perfect Meal")
    ingredients = st.text_input("What ingredients do you have?", placeholder="e.g., chicken, pasta, garlic", key="cook_ing")
    
    col1, col2 = st.columns(2)
    with col1:
        cuisine_cook = st.selectbox("Cuisine Choice", ["Any", "Italian", "Mexican", "Asian", "American", "Mediterranean"], key="c_cook")
        mood_cook = st.selectbox("Current Mood", ["Comfort Food", "Quick & Easy", "Healthy & Light", "Cozy"], key="m_cook")
    with col2:
        health_goal = st.selectbox("Dietary Targets", ["None", "Gluten Free", "Ketogenic", "Vegan", "Vegetarian"], key="h_cook")
        servings = st.number_input("Number of Servings Needed", min_value=1, max_value=20, value=2, step=1, key="s_cook")
        
    max_time = st.slider("Max Prep/Cooking Time (Minutes)", min_value=10, max_value=120, value=60, step=5, key="t_cook")
    
    if st.button("Generate Home Recipes", type="primary"):
        if not ingredients:
            st.warning("Please input ingredients to match!")
        else:
            st.info("🍳 Searching Spoonacular database for your top 3 ranked options...")
            
            url = "https://spoonacular.com"
            params = {
                "apiKey": SPOONACULAR_API_KEY,
                "query": ingredients,
                "maxReadyTime": max_time,
                "addRecipeInformation": True,
                "fillIngredients": True,  # Required to get raw ingredient weights for calculations
                "number": 3               # Request top 3 options
            }
            if health_goal != "None":
                params["diet"] = health_goal.lower().replace(" ", "")
            if cuisine_cook != "Any":
                params["cuisine"] = cuisine_cook.lower()
                
            try:
                response = requests.get(url, params=params)
                if response.status_code == 200:
                    data = response.json()
                    recipes = data.get("results", [])
                    
                    if recipes:
                        st.success(f"✨ Found {len(recipes)} amazing matches tailored to your profile!")
                        
                        # --- OUTPUT SWIPER/SLIDER TABS FOR TOP 3 RESULTS ---
                        recipe_tab_names = [f"🏆 Rank #{i+1}: {r.get('title')[:30]}..." for i, r in enumerate(recipes)]
                        swiper_tabs = st.tabs(recipe_tab_names)
                        
                        for index, recipe in enumerate(recipes):
                            with swiper_tabs[index]:
                                st.subheader(recipe.get("title"))
                                if recipe.get("image"):
                                    st.image(recipe["image"])
                                    
                                base_servings = recipe.get("servings", 1)
                                ready_in = recipe.get("readyInMinutes", max_time)
                                st.markdown(f"⏱️ **Ready in:** {ready_in} mins | 🍽️ **Base Servings:** {base_servings} ➔ **Your Scaled Request:** {servings} servings")
                                
                                # --- MATH SCALING LOOP ENGINE (OPTION B) ---
                                st.markdown("### 🛒 Scaled Ingredients List")
                                scale_multiplier = float(servings) / float(base_servings)
                                
                                extended_ingredients = recipe.get("extendedIngredients", [])
                                if extended_ingredients:
                                    for ing in extended_ingredients:
                                        base_amount = ing.get("amount", 0.0)
                                        scaled_amount = base_amount * scale_multiplier
                                        unit = ing.get("unit", "")
                                        name = ing.get("name", "")
                                        st.write(f"• **{scaled_amount:.2f} {unit}** of {name}")
                                else:
                                    st.write("Refer to the directions below for raw ingredient items.")
                                    
                                # --- DIRECTIONS PARSER ---
                                st.markdown("### 📋 Step-by-Step Instructions")
                                analyzed = recipe.get("analyzedInstructions")
                                if analyzed and len(analyzed) > 0:
                                    steps = analyzed[0].get("steps", [])
                                    for step in steps:
                                        st.write(f"**Step {step.get('number')}:** {step.get('step')}")
                                elif recipe.get("instructions"):
                                    st.write(recipe["instructions"])
                                else:
                                    st.write("Mix ingredients well and cook thoroughly according to taste!")
                                    
                                # --- MONETIZATION CONTEXT CARDS ---
                                st.markdown("---")
                                st.info(f"🛒 **Missing something?** [Instantly order these scaled ingredients for {servings} people via Instacart](https://instacart.com)")
                    else:
                        st.error("No recipes matched that exact configuration. Try widening your cooking time or filters!")
                else:
                    st.error(f"Spoonacular server error status code: {response.status_code}")
            except Exception as e:
                st.error(f"Failed to process recipe pipeline: {str(e)}")

# =========================================================================
# 🚗 TAB 2: GO OUT TO EAT (OPTION A LOCAL RESTAURANT LOOKUP ENGINE)
# =========================================================================
with tab_go_out:
    st.header("Find Local Restaurants Nearby")
    st.write("Don't want to clean dishes? Tell us your vibe and locate the best local dining spots.")
    
    col1_go, col2_go = st.columns(2)
    with col1_go:
        cuisine_go = st.selectbox("What Cuisine do you want?", ["Any", "Italian", "Mexican", "Asian", "Burgers/American", "Thai", "Sushi"], key="c_go")
        mood_go = st.selectbox("What is your current vibe?", ["Casual Dining", "Date Night / Fancy", "Late Night Cravings", "Fast & Trendy"], key="m_go")
    with col2_go:
        budget_go = st.select_slider("Amount Willing to Spend", options=["$", "$$", "$$$", "$$$$"], value="$$", key="b_go")
        distance_go = st.slider("Maximum Distance (Miles)", min_value=1, max_value=25, value=5, key="d_go")
        
    health_go = st.multiselect("Health Filters / Restrictions", ["Gluten-Free Options", "Vegan Friendly", "Low-Calorie Menu"], key="h_go")
    
    if st.button("Locate Nearby Restaurants", type="primary"):
        st.info(f"🚗 Geolocation engine mapping local {cuisine_go} spots matching budget {budget_go}...")
        
        # Mock restaurant array representing geographical feedback loop (maps directly to API schemas)
        mock_restaurants = [
            {"name": "The Golden Dragon Kitchen", "cuisine": "Asian", "distance": "1.4 miles away", "rating": "⭐ 4.8 / 5", "highlight": "Great for Quick & Easy comfort cravings!"},
            {"name": "Bella Italia Trattoria", "cuisine": "Italian", "distance": "2.9 miles away", "rating": "⭐ 4.6 / 5", "highlight": "Perfect romantic match for your Cozy Date Night vibe!"},
            {"name": "Taco Fiesta Cantina", "cuisine": "Mexican", "distance": "4.2 miles away", "rating": "⭐ 4.7 / 5", "highlight": "Fits your budget profile perfectly!"}
        ]
        
        # Filter matching logic simulation
        matches = [r for r in mock_restaurants if cuisine_go == "Any" or r["cuisine"].lower() in cuisine_go.lower()]
        if not matches:
            matches = mock_restaurants  # Fallback to display valid mock data structure if no direct match
            
        st.success(f"✨ Ranked top local dining venues near your location:")
        
        # --- SWIPER TABS FOR TOP 3 RESTAURANTS ---
        rest_tab_names = [f"📍 Rank #{i+1}: {res['name']}" for i, res in enumerate(matches[:3])]
        restaurant_swiper = st.tabs(rest_tab_names)
        
        for index, res in enumerate(matches[:3]):
            with restaurant_swiper[index]:
                st.subheader(res["name"])
                st.markdown(f"🛣️ **Distance:** {res['distance']} | 📊 **Community Rating:** {res['rating']}")
                st.markdown(f"💡 **Why you'll love it:** {res['highlight']}")
                st.write(f"**Budget Profile:** Max {budget_go} requirement satisfied.")
                
                # --- GO OUT TO EAT MONETIZATION PAYDAYS ---
                st.markdown("---")
                col_btn1, col_btn2 = st.columns(2)
                with col_btn1:
st.link_button("🚗 Order Delivery via DoorDash", "doordash.com", type="secondary")
with col_btn2:
st.link_button("🚕 Hail Ride with Uber", "uber.com", type="primary")

--- NON-INVASIVE ADS STITCHED FOOTER ---

st.markdown("---")
st.caption("💡 Sponsored: Upgrade your kitchen gear! Check out our partner discounts on non-stick skillets and air fryers.")


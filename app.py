import streamlit as st
import requests

# --- 1. CONFIGURATION & ENCRYPTED KEYS ---
SPOONACULAR_API_KEY = st.secrets.get("SPOONACULAR_KEY", "")

st.set_page_config(page_title="Smart Food Engine", page_icon="🍔", layout="centered")

# --- 2. UI STYLE UPGRADES (UX/Aesthetics) ---
st.markdown("""
    <style>
    .stButton>button {
        border-radius: 20px;
        font-weight: bold;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        transform: scale(1.02);
    }
    .premium-box {
        background-color: #fff3cd;
        padding: 15px;
        border-radius: 10px;
        border-left: 5px solid #ffc107;
    }
    </style>
""", unsafe_allow_html=True)

# --- 3. INITIALIZE SESSION STATE FOR ACCOUNT TRACKING ---
if "user_tier" not in st.session_state:
    st.session_state["user_tier"] = "Free"

# --- 4. SIDEBAR (Premium Tier Monetization Anchor) ---
st.sidebar.markdown(f"👤 **Account Tier:** `{st.session_state['user_tier']}`")
if st.session_state["user_tier"] == "Free":
    st.sidebar.markdown("---")
    st.sidebar.markdown('<div class="premium-box">👑 <b>Unlock Advanced Macros</b><br>Instant allergen blockers and calorie calendars for $2.99/mo.</div>', unsafe_allow_html=True)
    if st.sidebar.button("✨ Register for Paid Membership"):
        st.session_state["show_registration"] = True
st.sidebar.markdown("---")

# --- 5. PREMIUM MEMBER REGISTRATION FLOW ---
if st.session_state.get("show_registration"):
    st.header("👑 Join the Premium Membership Tier")
    st.write("Create your account and unlock hyper-personalized food recommendations.")
    
    with st.form("reg_form"):
        new_email = st.text_input("Email Address")
        new_pass = st.text_input("Password", type="password")
        payment_mock = st.checkbox("Agree to monthly subscription billing ($2.99/mo)")
        
        submit_reg = st.form_submit_button("Proceed to Secure Checkout")
        if submit_reg:
            if new_email and new_pass and payment_mock:
                st.session_state["user_tier"] = "Premium"
                st.session_state["show_registration"] = False
                st.success("🎉 Welcome aboard! Your Premium account is fully active.")
                st.rerun()
            else:
                st.warning("Please complete all registration fields.")
                
    if st.button("Cancel & Return to App"):
        st.session_state["show_registration"] = False
        st.rerun()

# --- 6. MAIN APP INTERFACE LAYER ---
else:
    st.title("🍔 Smart Food Recommendation Engine")
    st.write("Solve your daily food dilemma instantly. Tell us what you're craving!")

    # --- TWO INITIAL OPTIONS: THE TOP NAVIGATION TABS ---
    tab_cook, tab_go_out = st.tabs(["🍳 Cook at Home", "🚗 Go Out to Eat"])

    # =========================================================================
    # 🍳 TAB 1: COOK AT HOME
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
                    "fillIngredients": True,  
                    "number": 3               
                }
                if health_goal != "None":
                    params["diet"] = health_goal.lower().replace(" ", "")
                if cuisine_cook != "Any":
                    params["cuisine"] = cuisine_cook.lower()
                    
                try:
                    # Clear out the key message check
                    if not SPOONACULAR_API_KEY:
                        st.error("🔴 Spoonacular API Key missing! Please add SPOONACULAR_KEY to your Streamlit Cloud Secrets dashboard.")
                    else:
                        response = requests.get(url, params=params, timeout=10)
                        
                        if response.status_code == 401:
                            st.error("🔴 API Key Authorization Failed. Please check your key characters inside your Secrets dashboard!")
                        elif response.status_code == 402:
                            st.error("🔴 Daily Free Limit Reached! Your Spoonacular developer quota transforms automatically at midnight.")
                        elif response.status_code != 200:
                            st.error(f"🔴 Spoonacular Server Error: Code {response.status_code}. Raw message: {response.text}")
                    
                        else:
                            # 🟢 SAFE EXTRACTION CHECK: Only parse if it's structural JSON data
                            try:
                                data = response.json()
                                recipes = data.get("results", [])
                            except ValueError:
                                st.error("🔴 Server sent back an invalid data format.")
                                # This line reveals the exact issue (e.g., "Daily Quota Exceeded" or "Invalid API Key")
                                st.warning(f"Message from Spoonacular: {response.text}")
                                recipes = []
                            
                            if recipes:
                                st.success(f"✨ Found {len(recipes)} amazing matches tailored to your profile!")
                                
                                recipe_tab_names = [f"🏆 Rank #{i+1}: {r.get('title')[:25]}..." for i, r in enumerate(recipes)]
                                swiper_tabs = st.tabs(recipe_tab_names)
                                
                                for index, recipe in enumerate(recipes):
                                    with swiper_tabs[index]:
                                        st.subheader(recipe.get("title"))
                                        if recipe.get("image"):
                                            st.image(recipe["image"])
                                            
                                        base_servings = recipe.get("servings", 1)
                                        ready_in = recipe.get("readyInMinutes", max_time)
                                        st.markdown(f"⏱️ **Ready in:** {ready_in} mins | 🍽️ **Base Servings:** {base_servings} ➔ **Your Scaled Request:** {servings} servings")
                                        
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
                                            st.write("Refer to directions below for items.")
                                            
                                        st.markdown("### 📋 Step-by-Step Instructions")
                                        analyzed = recipe.get("analyzedInstructions")
                                        if analyzed and len(analyzed) > 0:
                                            steps = analyzed[0].get("steps", []) # Fix array targeting profile
                                            for step in steps:
                                                st.write(f"**Step {step.get('number')}:** {step.get('step')}")
                                        elif recipe.get("instructions"):
                                            st.write(recipe["instructions"])
                                        else:
                                            st.write("Mix ingredients well and cook thoroughly according to taste!")
                                            
                                        st.markdown("---")
                                        st.info(f"🛒 **Missing something?** [Instantly order these scaled ingredients for {servings} people via Instacart](https://instacart.com)")
                            else:
                                st.error("No recipes matched that exact configuration. Try widening your cooking time or filters!")
                except Exception as e:
                    st.error(f"Failed to process recipe pipeline data safely. System message: {str(e)}")

    # =========================================================================
    # 🚗 TAB 2: GO OUT TO EAT (LIVE GOOGLE PLACES API INTEGRATION)
    # =========================================================================
    with tab_go_out:
        st.header("Find Local Restaurants Nearby")
        st.write("Don't want to clean dishes? Tell us your vibe and locate the best local dining spots.")
        
        user_location = st.text_input("Enter your current City or Zip Code:", placeholder="e.g., Los Angeles, CA", key="loc_go")
        
        col1_go, col2_go = st.columns(2)
        with col1_go:
            cuisine_go = st.selectbox("What Cuisine do you want?", ["Any", "Italian", "Mexican", "Asian", "Burgers/American", "Thai", "Sushi"], key="c_go")
            mood_go = st.selectbox("What is your current vibe?", ["Casual Dining", "Date Night", "Late Night Cravings", "Fast & Trendy"], key="m_go")
        with col2_go:
            budget_go = st.select_slider("Amount Willing to Spend", options=["$", "$$", "$$$", "$$$$"], value="$$", key="b_go")
            distance_go = st.slider("Maximum Distance (Miles)", min_value=1, max_value=25, value=5, key="d_go")

            
        health_go = st.multiselect("Health Filters / Restrictions", ["Gluten-Free Options", "Vegan Friendly", "Low-Calorie Menu"], key="h_go")
        
        if st.button("Locate Nearby Restaurants", type="primary"):
            if not user_location:
                st.warning("Please enter your city or zip code so we can find places near you!")
            else:
                st.info(f"🚗 Querying Google Places database for live food spots near {user_location}...")
                
                GOOGLE_KEY = st.secrets.get("GOOGLE_PLACES_KEY", "")
                
                if not GOOGLE_KEY:
                    st.error("🔴 Google Places API Key missing! Please add GOOGLE_PLACES_KEY to your Streamlit Cloud Secrets dashboard.")
                else:
                    # 1. Google's actual active production endpoint path
                    google_url = "https://places.googleapis.com/v1/places:searchText"
                    
                    # 2. Re-map payload parameters to follow current property metrics
                    query_string = f"{cuisine_go if cuisine_go != 'Any' else ''} {mood_go} restaurant near {user_location}"
                    
                    payload = {
                        "textQuery": query_string,
                        "maxResultCount": 3
                    }
                    
                    # 1. Update the headers with the explicit request for places.displayName
                    headers = {
                        "Content-Type": "application/json",
                        "X-Goog-Api-Key": GOOGLE_KEY,
                        "X-Goog-FieldMask": "places.displayName,places.formattedAddress,places.rating,places.userRatingCount,places.priceLevel,places.currentOpeningHours"
                    }
                    
                    try:
                        # Production calls use POST instead of GET
                        response = requests.post(google_url, json=payload, headers=headers, timeout=10)
                        
                        if response.status_code == 200:
                            data = response.json()
                            raw_places = data.get("places", [])
                            
                            if raw_places:
                                st.success(f"✨ Found live dining venues matched to your profile!")
                                
                                # Extract the human-readable text title for the tab headers safely
                                rest_tab_names = [f"📍 Rank #{i+1}: {res.get('displayName', {}).get('text', 'Restaurant')[:15]}..." for i, res in enumerate(raw_places)]
                                restaurant_swiper = st.tabs(rest_tab_names)
                                
                                for index, res in enumerate(raw_places):
                                    with restaurant_swiper[index]:
                                        # Pull the actual name field now provided by our mask update
                                        display_name = res.get("displayName", {}).get("text", "Local Venue")
                                        st.subheader(display_name)
                                        
                                        address = res.get("formattedAddress", "Address unavailable")
                                        rating = res.get("rating", "No reviews yet")
                                        total_reviews = res.get("userRatingCount", 0)
                                        
                                        # Decode the new price metrics smoothly
                                        google_price_tier = res.get("priceLevel", "PRICE_LEVEL_UNSPECIFIED")
                                        price_symbols = {
                                            "PRICE_LEVEL_INEXPENSIVE": "$", 
                                            "PRICE_LEVEL_MODERATE": "$$", 
                                            "PRICE_LEVEL_EXPENSIVE": "$$$", 
                                            "PRICE_LEVEL_VERY_EXPENSIVE": "$$$$"
                                        }
                                        google_price = price_symbols.get(google_price_tier, "$$")
                                        
                                        st.markdown(f"📍 **Address:** {address}")

                                        st.markdown(f"📊 **Community Rating:** ⭐ {rating} / 5 ({total_reviews} reviews) | 💰 **Price Level:** `{google_price}`")
                                        
                                        # Open/Closed structural evaluation
                                        open_now = res.get("currentOpeningHours", {}).get("openNow")
                                        if open_now is True:
                                            st.markdown("🟢 **Status:** Open right now! Doors are ready.")
                                        elif open_now is False:
                                            st.markdown("🔴 **Status:** Currently closed. Double-check hours before driving out!")
                                            
                                        st.markdown("---")
                                        col_btn1, col_btn2 = st.columns(2)
                                        with col_btn1:
                                            # Clean route extraction fallback links
                                            clean_name = res.get("displayName", {}).get("text", "Restaurant").replace(" ", "+")
                                            maps_link = f"https://google.com{clean_name}+{address.replace(' ', '+')}"
                                            st.link_button("🗺️ Open in Google Maps", maps_link, type="primary")
                                        with col_btn2:
                                            st.link_button("🚗 Order Delivery via DoorDash", "https://doordash.com")
                            else:
                                st.error("No venues matched your criteria. Try adjustments to your selection filters!")
                        else:
                            st.error(f"🔴 Google API Server Error: Status Code {response.status_code}")
                            if response.status_code == 403:
                                st.info("💡 Tip: Ensure 'Places API (New)' status is toggled ON inside your Google Cloud Console Library dashboard.")
                    except Exception as e:
                        st.error(f"Failed to pull live restaurant data safely. System message: {str(e)}")

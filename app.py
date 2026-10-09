import streamlit as st
import requests

# --- 1. CONFIGURATION & ENCRYPTED KEYS ---
SPOONACULAR_API_KEY = "9023d1a591b544889df6a7c364cfb898"

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
                    response = requests.get(url, params=params, timeout=10)
                    
                    if response.status_code == 401:
                        st.error("🔴 API Key Authorization Failed. Please check your key characters inside the code!")
                    elif response.status_code == 402:
                        st.error("🔴 Daily Free Limit Reached! Your Spoonacular developer quota transforms automatically at midnight.")
                    elif response.status_code != 200:
                        st.error(f"🔴 Spoonacular Server Error: Code {response.status_code}. Try removing some filters.")
                    else:
                        data = response.json()
                        recipes = data.get("results", [])
                        
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
                                    
                                    # --- MATH SCALING LOOP ENGINE ---
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
                                        steps = analyzed[0].get("steps", [])
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
                    query_string = f"{cuisine_go if cuisine_go != 'Any' else ''} {mood_go} restaurant near {user_location}"
                    
                   budget_map = {"$": 1, "$$": 2, "$$$": 3, "$$$$": 4}
                    max_price_tier = budget_map.get(budget_go, 2)
                    
                    google_url = "https://googleapis.com"
                    google_params = {
                        "query": query_string,
                        "key": GOOGLE_KEY
                    }
                    
                    try:
                        response = requests.get(google_url, params=google_params, timeout=10)
                        
                        if response.status_code == 200:
                            data = response.json()
                            raw_places = data.get("results", [])
                            
                            filtered_places = [
                                place for place in raw_places 
                                if place.get("price_level", 0) <= max_price_tier
                            ]
                            
                            final_matches = filtered_places[:3]
                            
                            if final_matches:
                                st.success(f"✨ Found live dining venues matched to your profile!")
                                
                                rest_tab_names = [f"📍 Rank #{i+1}: {res.get('name')[:20]}..." for i, res in enumerate(final_matches)]
                                restaurant_swiper = st.tabs(rest_tab_names)
                                
                                for index, res in enumerate(final_matches):
                                    with restaurant_swiper[index]:
                                        st.subheader(res.get("name"))
                                        
                                        address = res.get("formatted_address", "Address unavailable")
                                        rating = res.get("rating", "No reviews yet")
                                        total_reviews = res.get("user_ratings_total", 0)
                                        google_price = "\$" * res.get("price_level", 1)
                                        
                                        st.markdown(f"📍 **Address:** {address}")
                                        st.markdown(f"📊 **Community Rating:** ⭐ {rating} / 5 ({total_reviews} reviews) | 💰 **Price Level:** `{google_price}`")
                                        
                                        open_now = res.get("opening_hours", {}).get("open_now")
                                        if open_now is True:
                                            st.markdown("🟢 **Status:** Open right now! Doors are ready.")
                                        elif open_now is False:
                                            st.markdown("🔴 **Status:** Currently closed. Double-check hours before driving out!")
                                            
                                        st.markdown("---")
                                        col_btn1, col_btn2 = st.columns(2)
                                        with col_btn1:
                                            maps_link = f"https://google.com{res.get('name').replace(' ', '+')}+{address.replace(' ', '+')}"
                                            st.link_button("🗺️ Open in Google Maps", maps_link, type="primary")
                                        with col_btn2:
                                            st.link_button("🚗 Order Delivery via DoorDash", "https://doordash.com")
                            else:
                                st.error("No open restaurants matched your specific budget or criteria nearby. Try increasing your budget slider or picking 'Any' cuisine!")
                        else:
                            st.error(f"🔴 Google API Server Error: Status Code {response.status_code}")
                    except Exception as e:
                        st.error(f"Failed to pull live restaurant data safely. System message: {str(e)}")

    # --- NON-INVASIVE ADS STITCHED FOOTER ---
    st.markdown("---")
    st.caption("💡 Sponsored: Upgrade your kitchen gear! Check out our partner discounts on non-stick skillets and air fryers.")

   

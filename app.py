import streamlit as st
import requests

# --- CONFIGURATION ---
# TODO: REPLACE THIS WITH YOUR REAL, ACTUAL 32-CHARACTER SPOONACULAR KEY!
API_KEY = "9023d1a591b544889df6a7c364cfb898"

st.set_page_config(page_title="Smart Chef", page_icon="🍳", layout="centered")

# --- SIDEBAR (Premium Monetization Track) ---
st.sidebar.markdown("👑 **Premium Member?** [Sign In Here](#)")
st.sidebar.markdown("---")

st.title("🍳 Cook at Home Planner")
st.write("Tell us what's in your kitchen, and we'll scale the perfect recipe.")

# --- USER INPUT CONTROLS ---
ingredients = st.text_input("What ingredients do you have?", placeholder="e.g., chicken, broccoli, garlic")

col1, col2 = st.columns(2)
with col1:
    cuisine = st.selectbox("Cuisine Choice", ["Any", "Italian", "Mexican", "Asian", "American", "Mediterranean"])
    mood = st.selectbox("Current Mood", ["Comfort Food", "Quick & Easy", "Healthy & Light", "Cozy"])
with col2:
    health_goal = st.selectbox("Dietary Targets", ["None", "Gluten Free", "Ketogenic", "Vegan", "Vegetarian"])
    servings = st.number_input("Number of Servings Needed", min_value=1, max_value=20, value=2, step=1)

max_time = st.slider("Max Prep/Cooking Time (Minutes)", min_value=10, max_value=120, value=45, step=5)

# --- ENGINE TRIGGER ---
if st.button("Generate My Perfect Recipe", type="primary"):
    if not ingredients:
        st.warning("Please enter at least one ingredient to get started!")
    else:
        st.info("🍳 Searching Spoonacular database for matches...")
        
        url = "https://spoonacular.com"
        params = {
            "apiKey": API_KEY,
            "includeIngredients": ingredients,
            "maxReadyTime": max_time,
            "addRecipeInformation": True,  
            "number": 1                    
        }
        
        if health_goal != "None":
            params["diet"] = health_goal.lower().replace(" ", "")
        if cuisine != "Any":
            params["cuisine"] = cuisine.lower()

        try:
            response = requests.get(url, params=params)
            
            # --- DEBUG BLOCK: Let's see exactly what Spoonacular is saying ---
            if response.status_code != 200:
                st.error(f"🔴 API Server Error! Status Code: {response.status_code}")
                st.warning(f"Server Message: {response.text}")
            else:
                data = response.json()
                if data.get("results"):
                    recipe = data["results"][0]  
                    
                    st.success("✨ Found a match!")
                    st.header(recipe["title"])
                    
                    if "image" in recipe:
                        st.image(recipe["image"])
                    
                    st.markdown(f"⏱️ **Ready in:** {recipe['readyInMinutes']} minutes")
                    st.markdown(f"🍽️ **Base Servings:** {recipe['servings']} | **Target Servings Requested:** {servings}")
                    
                    st.markdown("### 📋 Step-by-Step Instructions")
                    if recipe.get("analyzedInstructions") and len(recipe["analyzedInstructions"]) > 0:
                        steps = recipe["analyzedInstructions"][0]["steps"]
                        for step in steps:
                            st.write(f"**Step {step['number']}:** {step['step']}")
                    else:
                        st.write("Please check the full recipe link for direct instructions.")
                    
                    st.markdown("---")
                    st.info(f"🛒 **Need groceries?** [Order ingredients scaled for {servings} people via Instacart](https://instacart.com)")
                    st.caption("🔒 *Want to unlock nutritional macros (Protein/Carbs) for this meal? [Upgrade to Premium for $2.99/mo](#)*")
                else:
                    st.error("No recipes found matching those ingredients and filters. Try widening your cooking time or changing filters.")
                    
        except Exception as e:
            st.error(f"Failed to compile layout. System error message: {str(e)}")

st.markdown("---")
st.caption("💡 Advertisement: Support our free tier by checking out our cooking gear sponsors!")

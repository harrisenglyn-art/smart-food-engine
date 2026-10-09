import streamlit as st
import requests

# --- CONFIGURATION ---
# TODO: Paste your actual Spoonacular API key inside the quotes below!
API_KEY = "d1a32c1d8fb42388712a2d829f784a1e62a7e474"

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
        
        # 1. Structure the API Request URL
        url = "https://spoonacular.com"
        
        # 2. Pass user inputs directly into Spoonacular's filter parameters
        params = {
            "apiKey": API_KEY,
            "includeIngredients": ingredients,
            "maxReadyTime": max_time,
            "addRecipeInformation": True,  # Gives us full cooking instructions
            "number": 1                    # Bring back the single best match
        }
        
        # Apply health filters if selected
        if health_goal != "None":
            params["diet"] = health_goal.lower().replace(" ", "")
        if cuisine != "Any":
            params["cuisine"] = cuisine.lower()

        # 3. Fetch the data live from their servers
        try:
            response = requests.get(url, params=params)
            data = response.json()
            
            if data.get("results"):
                recipe = data["results"][0]  # Grab the first actual recipe from the matching list
                
                st.success("✨ Found a match!")
                st.header(recipe["title"])
                
                # Display Recipe Image
                if "image" in recipe:
                    st.image(recipe["image"])
                
                # Summary and Specs
                st.markdown(f"⏱️ **Ready in:** {recipe['readyInMinutes']} minutes")
                st.markdown(f"🍽️ **Base Servings:** {recipe['servings']} | **Target Servings Requested:** {servings}")
                
                # Instruction Steps
                st.markdown("### 📋 Step-by-Step Instructions")
                if recipe.get("analyzedInstructions"):
                    steps = recipe["analyzedInstructions"][0]["steps"]
                    for step in steps:
                        st.write(f"**Step {step['number']}:** {step['step']}")
                else:
                    st.write("Please check the full recipe link for direct instructions.")
                
                # --- AFFILIATE & PREMIUM MONETIZATION CARDS ---
                st.markdown("---")
                st.info(f"🛒 **Need groceries?** [Order ingredients scaled for {servings} people via Instacart](https://instacart.com)")
                st.caption("🔒 *Want to unlock nutritional macros (Protein/Carbs) for this meal? [Upgrade to Premium for $2.99/mo](#)*")
                
            else:
                st.error("No recipes found matching those ingredients and filters. Try widening your cooking time or changing filters.")
                
        except Exception as e:
            st.error("Failed to connect to the data server. Double check your API key!")

# --- DISPLAY AD REVENUE ELEMENT ---
st.markdown("---")
st.caption("💡 Advertisement: Support our free tier by checking out our cooking gear sponsors!")

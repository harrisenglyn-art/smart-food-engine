import streamlit as st
import requests

# --- CONFIGURATION ---
# TODO: REPLACE THIS WITH YOUR REAL, REVEALED 32-CHARACTER SPOONACULAR KEY!
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

max_time = st.slider("Max Prep/Cooking Time (Minutes)", min_value=10, max_value=120, value=60, step=5)

# --- ENGINE TRIGGER ---
if st.button("Generate My Perfect Recipe", type="primary"):
    if not ingredients:
        st.warning("Please enter at least one ingredient to get started!")
    else:
        st.info("🍳 Searching Spoonacular database for matches...")
        
        # We target complexSearch to filter by diet/cuisine and return full information cleanly
        url = "https://spoonacular.com"
        params = {
            "apiKey": API_KEY,
            "query": ingredients,
            "maxReadyTime": max_time,
            "addRecipeInformation": True,  
            "instructionsRequired": True,
            "number": 1                    
        }
        
        if health_goal != "None":
            params["diet"] = health_goal.lower().replace(" ", "")
        if cuisine != "Any":
            params["cuisine"] = cuisine.lower()

        try:
            response = requests.get(url, params=params)
            
            # Catch API blockages or quota outages early
            if response.status_code == 401:
                st.error("🔴 API Key Authorization Failed. Please check that your key was copied correctly without hidden spaces!")
            elif response.status_code == 402:
                st.error("🔴 Daily Free Limit Reached! Your Spoonacular developer quota will reset completely at midnight.")
            elif response.status_code != 200:
                st.error(f"🔴 Server returned an error code: {response.status_code}. Try removing some filters.")
            else:
                data = response.json()
                results = data.get("results", [])
                
                if results and len(results) > 0:
                    recipe = results[0] # Safely target the first match from the list
                    
                    st.success("✨ Found a match!")
                    st.header(recipe.get("title", "Delicious Recipe"))
                    
                    if recipe.get("image"):
                        st.image(recipe["image"])
                    
                    # Display specs safely
                    ready_time = recipe.get("readyInMinutes", max_time)
                    base_servings = recipe.get("servings", 2)
                    st.markdown(f"⏱️ **Ready in:** {ready_time} minutes")
                    st.markdown(f"🍽️ **Original Recipe Servings:** {base_servings} | **Your Target Servings:** {servings}")
                    
                    # Safely extract and format instructions
                    st.markdown("### 📋 Step-by-Step Instructions")
                    instructions = recipe.get("analyzedInstructions")
                    
                    if instructions and len(instructions) > 0 and "steps" in instructions[0]:
                        steps = instructions[0]["steps"]
                        for step in steps:
                            st.write(f"**Step {step.get('number')}:** {step.get('step')}")
                    elif recipe.get("instructions"):
                        # Alternative look up if structured steps aren't formatted by the chef
                        st.write(recipe["instructions"])
                    else:
                        st.write("No direct step-by-step instructions provided. Enjoy mixing your fresh ingredients!")
                    
                    # --- AFFILIATE & PREMIUM MONETIZATION CARDS ---
                    st.markdown("---")
                    st.info(f"🛒 **Need groceries?** [Order ingredients scaled for {servings} people via Instacart](https://instacart.com)")
                    st.caption("🔒 *Want to unlock nutritional macros (Protein/Carbs) for this meal? [Upgrade to Premium for $2.99/mo](#)*")
                else:
                    st.error("No recipes found matching that specific combination. Try widening your cooking time or switching Cuisine Choice to 'Any'!")
                    
        except Exception as e:
            st.error(f"Failed to process recipe. System message: {str(e)}")

st.markdown("---")
st.caption("💡 Advertisement: Support our free tier by checking out our cooking gear sponsors!")

from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
import io

def generate_recipe_pdf(recipe):
    """Compiles title, ingredient columns, and comprehensive steps into an instant download-ready PDF file buffer."""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=54, leftMargin=54, topMargin=54, bottomMargin=54)
    story = []
    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'RecipeTitle', 
        parent=styles['Heading1'], 
        fontSize=24, 
        textColor=colors.HexColor("#D32F2F"), 
        spaceAfter=15
    )
    section_style = ParagraphStyle(
        'RecipeSection', 
        parent=styles['Heading2'], 
        fontSize=14, 
        textColor=colors.HexColor("#1976D2"), 
        spaceBefore=10, 
        spaceAfter=5
    )
    body_style = ParagraphStyle('RecipeBody', parent=styles['BodyText'], fontSize=10, spaceAfter=4)
    
    # Render Title Header
    story.append(Paragraph(recipe.get("title", "Delicious Recommendation Option"), title_style))
    story.append(Spacer(1, 10))
    
    # Render Ingredients Matrix
    story.append(Paragraph("🛒 Ingredients Matrix", section_style))
    for ing in recipe.get("usedIngredients", []) + recipe.get("missedIngredients", []):
        story.append(Paragraph(f"• {ing.get('original', ing.get('name'))}", body_style))
    if not recipe.get("usedIngredients") and not recipe.get("missedIngredients"):
        for ing in recipe.get("extendedIngredients", []):
            story.append(Paragraph(f"• {ing.get('original')}", body_style))
            
    story.append(Spacer(1, 15))
    
    # Render Step-by-Step Context Instructions
    story.append(Paragraph("📋 Cooking Execution Steps", section_style))
    analyzed = recipe.get("analyzedInstructions")
    
    if analyzed and isinstance(analyzed, list) and len(analyzed) > 0:
        steps_list = analyzed[0].get("steps", [])
        if steps_list:
            for step in steps_list:
                story.append(Paragraph(f"<b>Step {step.get('number')}:</b> {step.get('step')}", body_style))
        else:
            story.append(Paragraph("Directions are missing deep structural data row files.", body_style))
    elif recipe.get("instructions"):
        story.append(Paragraph(recipe["instructions"], body_style))
    else:
        story.append(Paragraph("Mix elements well and prepare thoroughly according to taste parameters.", body_style))
        
    doc.build(story)
    buffer.seek(0)
    return buffer
import streamlit as st
import requests
# 🟢 INITIALIZE MEMORY ARRAYS SECURELY AT THE GLOBAL LAYER (Far left margin, no spaces)
if "recipes" not in st.session_state:
    st.session_state.recipes = []

def get_recipe_details(recipe_id):
    """Fetches full recipe metadata explicitly containing instruction step matrices."""
    SPOONACULAR_API_KEY = st.secrets.get("SPOONACULAR_API_KEY", "").strip()
    
    # 🟢 VERIFIED URL ALIGNMENT CONSTRUCTION
    url = f"https://api.spoonacular.com/recipes/{recipe_id}/information"
    params = {"apiKey": SPOONACULAR_API_KEY}
    
    try:
        response = requests.get(url, params=params)
        # If we hit quota limits, capture the error footprint instead of crashing
        if response.status_code != 200:
            return {"api_quota_blocked": True, "status_code": response.status_code}
        return response.json()
    except Exception as e:
        return {}

def search_recipes_by_ingredients(ingredients_string, cuisine="Any", diet="None", max_time=60):
    """Fetches matching recipes from Spoonacular while filtering by custom cuisine, diet, and cooking time parameters."""
    SPOONACULAR_API_KEY = st.secrets.get("SPOONACULAR_API_KEY", "").strip()
    
    # Switch to complexSearch to natively support multi-parameter matrix filters
    url = "https://api.spoonacular.com/recipes/complexSearch"
    
    params = {
        "apiKey": SPOONACULAR_API_KEY,
        "includeIngredients": ingredients_string,
        "number": 3,
        "addRecipeInformation": True,
        "fillIngredients": True
    }
    
    # Dynamically inject advanced selection tags from the user's dropdowns
    if cuisine != "Any":
        params["cuisine"] = cuisine
    if diet != "None":
        params["diet"] = diet
    if max_time:
        params["maxReadyTime"] = max_time
        
    try:
        response = requests.get(url, params=params)
        data = response.json()
        return data.get("results", [])
    except Exception as e:
        st.error(f"Error fetching filtered recipe database query: {e}")
        return []
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
    
    # 🟢 STEP 1: RENDER ALL WIDGET INPUT FIELDS FIRST SO THE VARIABLES EXIST
    user_ingredients = st.text_input("Enter your available ingredients:", key="ingredients_input")

    col1, col2 = st.columns(2)
    with col1:
        cuisine_cook = st.selectbox(
            "Cuisine Choice", 
            [
                "Any", "African", "American", "Asian", "British", "Cajun", "Caribbean", 
                "Chinese", "Eastern European", "European", "French", "German", "Greek", 
                "Indian", "Irish", "Italian", "Japanese", "Jewish", "Korean", 
                "Latin American", "Mediterranean", "Mexican", "Middle Eastern", "Nordic", 
                "Southern", "Spanish", "Thai", "Vietnamese"
            ],
            key="c_cook_dropdown"
        )
        mood_cook = st.selectbox("Current Mood", ["Comfort Food", "Quick & Easy", "Healthy & Light", "Cozy"], key="m_cook_dropdown")
        
    with col2:
        health_goal = st.selectbox(
            "Dietary Targets", 
            [
                "None", "Gluten Free", "Ketogenic", "Vegetarian", "Lacto-Vegetarian", 
                "Ovo-Vegetarian", "Vegan", "Pescetarian", "Paleo", "Primal", 
                "Low FODMAP", "Whole30"
            ], 
            key="h_goal_dropdown"
        )
        servings = st.number_input("Number of Servings Needed", min_value=1, max_value=20, value=2, step=1, key="s_cook_input")

    max_time = st.slider("Max Prep/Cooking Time (Minutes)", min_value=10, max_value=120, value=60, step=5, key="t_c_slider")

    # 🟢 STEP 2: UNIFIED USER SEARCH TRIGGER (Everything nested cleanly inside)
    if st.button("Generate Home Recipes", type="primary", key="cook_tab_primary_generator_v3"):
        if not user_ingredients:
            st.warning("Please input ingredients to match!")
        else:
            with st.spinner("Searching and parsing recipe instructions..."):
                # 🟢 FIXED: Kept all parameters perfectly indented to stay inside the button context loop
                raw_results = search_recipes_by_ingredients(
                    user_ingredients,
                    cuisine=cuisine_cook,
                    diet=health_goal,
                    max_time=max_time
                )

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

    # Render Active Clean Cards Below Search Operation
    if st.session_state.recipes:
        st.markdown("---")
        st.subheader("🍳 Top 3 Recommended Match Options")
        
        for index, recipe in enumerate(st.session_state.recipes):
            recipe_title = recipe.get("title") or "Delicious Match Option"
            
            # 🟢 RESTORED CONTAINER: This holds everything and fixes your indentation
            with st.expander(f"📖 {recipe_title}", expanded=True):
                
                # 🚫 PHOTOS REMOVED: st.image logic has been completely left out here
                
                # # 2. Side-by-Side Ingredient Breakdown Columns
                st.markdown("### 🛒 Ingredients Required")
                used_ings = recipe.get("usedIngredients", [])
                missed_ings = recipe.get("missedIngredients", [])
                
                col_ing1, col_ing2 = st.columns(2)
                with col_ing1:
                    st.markdown("**🟢 Ingredients You Have:**")
                    if used_ings:
                        for ing in used_ings:
                            # 🟢 FIXED syntax error: f-string 'f' is outside the quotes
                            st.write(f"- {ing.get('original', ing.get('name'))}")
                    else:
                        st.write("- None listed")
                        
                with col_ing2:
                    st.markdown("**🔴 Ingredients You Need to Buy:**")
                    if missed_ings:
                        for ing in missed_ings:
                            st.write(f"- {ing.get('original', ing.get('name'))}")
                    else:
                        st.write("- None! You have everything!")
                
                st.markdown("---")
                
                # 🟢 3. INSTANT DOWNLOADABLE PDF BUTTON (Hides long text clutter on your site)
                try:
                    pdf_data = generate_recipe_pdf(recipe)
                    clean_filename = recipe_title.lower().replace(" ", "_")
                    
                    st.download_button(
                        label="📥 Download Printable Recipe Guide (PDF)",
                        data=pdf_data,
                        file_name=f"{clean_filename}_guide.pdf",
                        mime="application/pdf",
                        key=f"dl_pdf_btn_{index}_{recipe.get('id', index)}" # Fully unique context iteration key
                    )
                except Exception as e:
                    st.error("Print layout compiling engine temporarily updating.")
                    
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

    # 1. Google Places Search Trigger Engine (Migrated to Places API New)
    if st.button("Find Nearby Restaurants", type="primary", key="takeout_tab_final_launch_button_v3"):
        if not takeout_location:
            st.warning("Please provide a location target to route coordinates!")
        else:
            GOOGLE_PLACES_API_KEY = st.secrets.get("GOOGLE_PLACES_API_KEY", "").strip()
            
            if not GOOGLE_PLACES_API_KEY:
                st.error("🛑 Connection Aborted: Your GOOGLE_PLACES_API_KEY is missing or unconfigured in your Cloud Settings panel!")
            else:
                with st.spinner("Querying Google Places (New) dataset for matching venues..."):
                    
                    # 🟢 NEW COMPATIBLE GOOGLE MAPS ENDPOINT
                    places_url = "https://places.googleapis.com/v1/places:searchText"
                    
                    # Modern APIs pass data in a JSON body rather than raw URL parameters
                    payload_data = {
                        "textQuery": f"{cuisine_takeout} restaurant near {takeout_location}"
                    }
                    
                    # Modern APIs require headers specifying your key and the exact data fields you want to return
                    headers = {
                        "Content-Type": "application/json",
                        "X-Goog-Api-Key": GOOGLE_PLACES_API_KEY,
                        # This specifies the fields we want back (saves your billing costs!)
                        "X-Goog-FieldMask": "places.displayName,places.formattedAddress,places.rating"
                    }
                    
                    try:
                        # Send a POST request to the new endpoint
                        response = requests.post(places_url, json=payload_data, headers=headers)
                        
                        if response.status_code == 403:
                            st.error("🛑 Google Access Denied: Make sure 'Places API (New)' is fully enabled in your Google Cloud Console library!")
                        elif response.status_code != 200:
                            st.error(f"🛑 Google API Error: Received HTTP Status {response.status_code} from server.")
                        else:
                            places_data = response.json()
                            restaurants = places_data.get("places", [])
                            
                            if restaurants:
                                valid_count = 0
                                for rest in restaurants:
                                    # The new API nests names inside a 'displayName' dictionary
                                    name = rest.get("displayName", {}).get("text", "Unknown Restaurant")
                                    address = rest.get("formattedAddress", "No address listed")
                                    rating = rest.get("rating", "No ratings yet")
                                    
                                    with st.container(border=True):
                                        st.markdown(f"### 🏪 {name}")
                                        st.write(f"📍 **Address:** {address}")
                                        st.write(f"⭐ **Google Rating:** {rating} / 5")
                                    valid_count += 1
                                    
                                st.success(f"Successfully unpacked {valid_count} excellent matching options nearby!")
                            else:
                                st.info("No matching locations found for that specific query layout.")
                                
                    except Exception as e:
                        st.error(f"Failed to communicate with Google Places interface: {e}")

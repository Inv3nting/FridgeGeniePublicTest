import streamlit as st
import datetime
import os
import json
import calendar

# Initial setup
def initialize():
    if not os.path.exists("data"):
        os.makedirs("data")
    if not os.path.exists("photos"):
        os.makedirs("photos")
    if not os.path.exists("data/users.json"):
        with open("data/users.json", "w") as f:
            json.dump({}, f)

# Authentication functions (no changes needed here)
def load_users():
    with open("data/users.json", "r") as f:
        return json.load(f)

def save_users(users):
    with open("data/users.json", "w") as f:
        json.dump(users, f)

def authenticate(username, password):
    users = load_users()
    if username in users and users[username]["password"] == password:
        return True
    return False

def register_user(username, password):
    users = load_users()
    if username in users:
        return False
    users[username] = {
        "password": password,
        "items": []  # Changed 'photos' to 'items' to be more general
    }
    save_users(users)
    return True

def save_item_metadata(username, item_id, item_name, expiration_date=None, timestamp=None):
    users = load_users()
    if timestamp is None:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Check if item exists, update if it does
    for item in users[username]["items"]:
        if item["id"] == item_id:
            item["name"] = item_name
            item["timestamp"] = timestamp
            if expiration_date:
                item["expiration_date"] = expiration_date.strftime('%Y-%m-%d')
            else:
                item.pop("expiration_date", None) # Remove if no expiration date provided
            save_users(users)
            return

    # Add new item if it doesn't exist
    new_item = {
        "id": item_id,
        "name": item_name,
        "timestamp": timestamp
    }
    if expiration_date:
        new_item["expiration_date"] = expiration_date.strftime('%Y-%m-%d')
    users[username]["items"].append(new_item)
    save_users(users)

def get_user_items(username):
    users = load_users()
    return users[username]["items"]

def update_item_name(username, item_id, new_name):
    users = load_users()
    for item in users[username]["items"]:
        if item["id"] == item_id:
            item["name"] = new_name
            save_users(users)
            return True
    return False

# Photo capture and management (renamed to item capture)
def save_photo(image_data, item_id):
    with open(f"photos/{item_id}.jpg", "wb") as f:
        f.write(image_data)

def get_photo(item_id):
    with open(f"photos/{item_id}.jpg", "rb") as f:
        return f.read()

# Preset item names with estimated shelf lives (in days)
PRESET_ITEMS = {
    "Milk (refrigerated)": 8,
    "Eggs (refrigerated)": 28,
    "Hard Cheese (cheddar, parmesan, etc.)": 21,
    "Soft Cheese (brie, ricotta, etc.)": 10,
    "Yogurt (refrigerated)": 10,
    "Bananas": 5,
    "Apples": 45,
    "Berries (strawberries, blueberries, raspberries)": 5,
    "Tomatoes": 6,
    "Lettuce": 10,
    "Carrots": 18,
    "Potatoes": 60,
    "Onions": 45,
    "Sliced Bread": 6,
    "Whole Grain Bread": 8,
    "Pasta (dry)": 730, # Roughly 2 years
    "Rice (dry, white)": 1825, # Roughly 5 years
    "Rice (dry, brown)": 365, # Roughly 1 year
    "Cereal (unopened)": 365,
    "Chicken (raw, refrigerated)": 1,
    "Beef (raw, refrigerated)": 4,
    "Pork (raw, refrigerated)": 4,
    "Deli Meats (opened)": 4,
    "Chips (opened)": 10,
    "Pretzels (opened)": 21,
    "Crackers (opened)": 21,
    "Popcorn (unpopped kernels)": 1825,
    "Bottled Water (unopened)": 1825,
    "Soft Drinks (unopened)": 270,
    "Coffee (ground, opened)": 21,
    "Coffee (whole beans, opened)": 21,
    "Tea (bags or loose leaf)": 540,
    "Juice (refrigerated, opened)": 8,
    "Frozen Vegetables (unopened)": 365,
    "Frozen Pizza (unopened)": 540,
    "Frozen Ready-to-Eat Meals (unopened)": 270,
    "Ice Cream (opened)": 45,
    "Canned Vegetables (unopened)": 1095,
    "Canned Fruits (unopened)": 730,
    "Canned Soups (unopened)": 1095,
    "Canned Beans (unopened)": 1095,
    "Canned Tuna (unopened)": 730,
    "Ketchup (opened)": 120,
    "Mustard (opened)": 540,
    "Mayonnaise (opened)": 90,
    "Salad Dressing (opened)": 90,
}
PRESET_ITEM_NAMES = [""] + list(PRESET_ITEMS.keys()) # Add an empty string for manual input

# Main app
def main():
    initialize()

    st.set_page_config(page_title="Fridge Genie", page_icon="🗄️") # Updated title and icon

    # Session state initialization
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
    if "username" not in st.session_state:
        st.session_state.username = ""

    # Authentication section
    if not st.session_state.logged_in:
        st.title("🗄️ Food Expiration Tracker")

        tab1, tab2 = st.tabs(["Login", "Register"])

        with tab1:
            st.subheader("Login")
            username = st.text_input("Username", key="login_username")
            password = st.text_input("Password", type="password", key="login_password")

            if st.button("Login"):
                if authenticate(username, password):
                    st.session_state.logged_in = True
                    st.session_state.username = username
                    st.success("Login successful!")
                    st.rerun()
                else:
                    st.error("Invalid username or password")

        with tab2:
            st.subheader("Register")
            new_username = st.text_input("Username", key="register_username")
            new_password = st.text_input("Password", type="password", key="register_password")
            confirm_password = st.text_input("Confirm Password", type="password")

            if st.button("Register"):
                if new_password != confirm_password:
                    st.error("Passwords do not match")
                elif not new_username or not new_password:
                    st.error("Username and password cannot be empty")
                else:
                    if register_user(new_username, new_password):
                        st.success("Registration successful! You can now login.")
                    else:
                        st.error("Username already exists")

    else:
        # User is logged in
        st.title(f"🍎 Food Expiration Tracker - Welcome, {st.session_state.username}!") # Updated title

        # Logout button in sidebar
        if st.sidebar.button("Logout"):
            st.session_state.logged_in = False
            st.session_state.username = ""
            st.rerun()

        # Main tabs
        tab1, tab2, tab3 = st.tabs(["Add Item", "My Items", "Expiration Calendar"]) # Updated tab names

        with tab1:
            st.subheader("Add a New Item")
            st.write("Capture an image of your food item (optional) and set its name and potential expiration.")

            img_file = st.camera_input("Capture Image (Optional)")

            selected_preset = st.selectbox("Or choose a preset item name:", PRESET_ITEM_NAMES, index=0) # Set default index to 0 (empty string)
            manual_name = st.text_input("Item Name (or edit the preset):", value=selected_preset if selected_preset else "")

            # Calculate expiration date based on preset selection
            if selected_preset and selected_preset in PRESET_ITEMS:
                shelf_life = PRESET_ITEMS[selected_preset]
                today = datetime.date.today()
                estimated_expiration = today + datetime.timedelta(days=shelf_life)
                expiration_date = st.date_input("Estimated Expiration Date (Optional)", value=estimated_expiration)
            else:
                expiration_date = st.date_input("Estimated Expiration Date (Optional)")

            if st.button("Save Item"):
                item_name = manual_name.strip()
                if not item_name:
                    st.error("Item name cannot be empty.")
                else:
                    item_id = f"{st.session_state.username}_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"
                    expiration = expiration_date if expiration_date else None

                    if img_file:
                        save_photo(img_file.getvalue(), item_id)

                    save_item_metadata(st.session_state.username, item_id, item_name, expiration)
                    st.success(f"'{item_name}' saved successfully!")
                    st.rerun()

        with tab2:
            st.subheader("My Items")

            user_items = get_user_items(st.session_state.username)

            if not user_items:
                st.info("You haven't added any items yet. Go to the 'Add Item' tab to add some!")
            else:
                for item in user_items:
                    with st.expander(f"{item['name']} - Added: {item['timestamp']}{f' - Expires: {item.get('expiration_date')}' if 'expiration_date' in item else ''}"):
                        # Display the image if it exists
                        photo_path = f"photos/{item['id']}.jpg"
                        if os.path.exists(photo_path):
                            try:
                                image_data = get_photo(item['id'])
                                st.image(image_data, caption=item['name'])
                            except Exception as e:
                                st.error(f"Error displaying image: {str(e)}")

                        # Edit name
                        new_name = st.text_input("Edit name:", value=item['name'], key=f"name_{item['id']}")

                        if st.button("Update Name", key=f"update_{item['id']}"):
                            if update_item_name(st.session_state.username, item['id'], new_name):
                                st.success("Name updated successfully!")
                                st.rerun()
                            else:
                                st.error("Failed to update name")

                        st.write(f"Added on: {item['timestamp']}")
                        if 'expiration_date' in item:
                            st.write(f"Estimated Expiration: {item['expiration_date']}")

        with tab3:
            st.subheader("Expiration Calendar")
            user_items = get_user_items(st.session_state.username)

            # Extract expiration dates of the items
            expiration_dates = {}
            for item in user_items:
                if 'expiration_date' in item and item['expiration_date']:
                    exp_date = datetime.datetime.strptime(item['expiration_date'], '%Y-%m-%d').date()
                    if exp_date not in expiration_dates:
                        expiration_dates[exp_date] = []
                    expiration_dates[exp_date].append(item['name'])

            now = datetime.datetime.now()
            year = st.number_input("Year", min_value=now.year - 5, max_value=now.year + 5, value=now.year)
            month = st.number_input("Month", min_value=1, max_value=12, value=now.month)

            cal = calendar.monthcalendar(year, month)
            month_name = calendar.month_name[month]
            st.write(f"### {month_name} {year}")

            # Display the calendar
            cols = st.columns(7)
            days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
            for i, day in enumerate(days):
                cols[i].write(day)

            for week in cal:
                week_cols = st.columns(7)
                for i, day in enumerate(week):
                    if day != 0:
                        date_obj = datetime.date(year, month, day)
                        if date_obj in expiration_dates:
                            items_expiring = expiration_dates[date_obj]
                            week_cols[i].markdown(
                                f"<div style='border: 1px solid red; padding: 2px; border-radius: 3px;'>"
                                f"{day}<br>"
                                f"<small>{', '.join(items_expiring)}</small>"
                                f"</div>",
                                unsafe_allow_html=True,
                            )
                        else:
                            week_cols[i].write(str(day))
                    else:
                        week_cols[i].write("")

if __name__ == "__main__":
    main()
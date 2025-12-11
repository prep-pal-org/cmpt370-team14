
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
import sqlite3
import bcrypt
import os
import string, random

from werkzeug.utils import secure_filename
from cmpt370_project_user_management.Model.Recipe import Recipe
from cmpt370_project_user_management.FlaskConnections.RecipeManager import RecipeManager
from cmpt370_project_user_management.db.setup_database import database_connection, create_tables, update_tables
from cmpt370_project_user_management.Model.calendar_service import CalendarService, CalendarError

app = Flask(__name__, static_folder='static', template_folder='templates')
app.secret_key = "saucy"

# Calculate absolute path to DB to avoid errors
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_NAME = os.path.join(BASE_DIR, "db", "saucyapp.db")

calendar_service = CalendarService()


# -------------------------------------------------------------
# HELPER: Python-side Filtering (for My Recipes / Favorites)
# -------------------------------------------------------------
def filter_list_python(recipes, sort_by, diet_filter):
    # 1. Filter
    if diet_filter == "gluten_free":
        recipes = [r for r in recipes if r.category and "Gluten Free" in r.category]
    elif diet_filter == "lactose_free":
        recipes = [r for r in recipes if r.category and "Lactose Free" in r.category]
    elif diet_filter == "peanut_allergy":
        recipes = [r for r in recipes if r.category and "Peanut Allergy" in r.category]

    # 2. Sort
    if sort_by == "az":
        recipes.sort(key=lambda x: x.name.lower())
    elif sort_by == "za":
        recipes.sort(key=lambda x: x.name.lower(), reverse=True)

    return recipes


# -------------------------------------------------------------
# ROUTE: New Updated Home Page - Randi
# -------------------------------------------------------------
@app.route('/')
def home():
    return render_template('use_home_page.html')

# Old home page (legacy)
@app.route('/old_home')
def old_home():
    return render_template('homePage.html')

@app.route('/about_us')
def about_us():
    return render_template('about_us.html')


# -------------------------------------------------------------
# ROUTES: Grocery List - Soham
# -------------------------------------------------------------
@app.route('/grocery-list')
def grocery_list():
    # Check if user is logged in
    if 'username' not in session:
        flash("You must be logged in to see your grocery list.")
        return redirect(url_for('login'))

    conn = database_connection(DB_NAME)
    cursor = conn.cursor()

    try:
        # Get the user_id from the session username
        cursor.execute("SELECT user_id FROM user_profile WHERE username = ?", (session['username'],))
        user_result = cursor.fetchone()

        # If user not found (shouldn't happen if logged in), log them out
        if not user_result:
            flash("Error finding user. Please log in again.")
            return redirect(url_for('logout'))

        current_user_id = user_result[0]

        # Fetch items for the *current* user
        cursor.execute("SELECT item_id, item_text, quantity FROM grocery_list WHERE user_id = ?", (current_user_id,))
        items_tuples = cursor.fetchall()

    except sqlite3.Error as e:
        print("Error fetching grocery list:", e)
        flash("An error occurred while fetching your list.")
        items_tuples = []  # Ensure items_tuples is defined even if try fails
    finally:
        conn.close()

    # Convert list of tuples to a list of dicts
    items_list = []
    for row in items_tuples:
        items_list.append({"id": row[0], "item_text": row[1], "quantity": row[2]})

    return render_template('grocery_list.html', items=items_list)


# Route to add an item to the grocery list
@app.route('/add_grocery_item', methods=['POST'])
def add_grocery_item():
    # Check if user is logged in
    if 'username' not in session:
        flash("You must be logged in to add items.")
        return redirect(url_for('login'))

    if request.method == 'POST':
        item_text = request.form['item_text']
        quantity = request.form['quantity']

        if item_text:
            conn = database_connection(DB_NAME)
            cursor = conn.cursor()
            try:
                # Get the user_id from the session username
                cursor.execute("SELECT user_id FROM user_profile WHERE username = ?", (session['username'],))
                user_result = cursor.fetchone()

                if not user_result:
                    flash("Error finding user. Please log in again.")
                    return redirect(url_for('logout'))

                current_user_id = user_result[0]

                # Insert the item with the *current* user's ID
                cursor.execute("INSERT INTO grocery_list (user_id, item_text, quantity) VALUES (?, ?, ?)",
                               (current_user_id, item_text, quantity))
                conn.commit()
            except sqlite3.Error as e:
                print("Error adding grocery item:", e)
                flash("Error adding item to list.")
            finally:
                conn.close()

        # Redirect back to the grocery list page
        return redirect(url_for('grocery_list'))


@app.route('/remove_grocery_item', methods=['POST'])
def remove_grocery_item():
    # Check if user is logged in
    if 'username' not in session:
        flash("You must be logged in to remove items.")
        return redirect(url_for('login'))

    if request.method == 'POST':
        item_id = request.form['item_id']

        conn = database_connection(DB_NAME)
        cursor = conn.cursor()
        try:
            # Get the user_id from the session username
            cursor.execute("SELECT user_id FROM user_profile WHERE username = ?", (session['username'],))
            user_result = cursor.fetchone()

            if not user_result:
                flash("Error finding user. Please log in again.")
                return redirect(url_for('logout'))

            current_user_id = user_result[0]

            # Securely delete the item
            # This query ensures a user can ONLY delete their own items
            cursor.execute("DELETE FROM grocery_list WHERE item_id = ? AND user_id = ?", (item_id, current_user_id))
            conn.commit()

            # Check if any row was actually deleted
            if cursor.rowcount == 0:
                flash("Error: Item not found or you do not have permission to remove it.")
            else:
                flash("Item removed.")

        except sqlite3.Error as e:
            print("Error removing grocery item:", e)
            flash("Error removing item.")
        finally:
            conn.close()

    # Redirect back to the grocery list page
    return redirect(url_for('grocery_list'))


# -------------------------------------------------------------
# ROUTES: USER PROFILE / LOGIN - Randi
# -------------------------------------------------------------
@app.route('/create_profile', methods=['GET', 'POST'])
def createProfile():
    if request.method == 'POST':
        userName = request.form['username']
        email = request.form['email']
        password = request.form['password']

        hash_password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
        try:
            with sqlite3.connect(DB_NAME) as conn:
                cur = conn.cursor()
                cur.execute(" INSERT INTO user_profile (username, email, password) VALUES (?, ?,?)",
                            (userName, email, hash_password))
                conn.commit()
                flash("Profile created successfully")
                return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash("Username already taken.")
            return redirect(url_for('createProfile'))

    return render_template('create_profile.html')


# Login page -Randi
@app.route('/login_page', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        userName = request.form['username']
        entered_password = request.form['password']

        with sqlite3.connect(DB_NAME) as conn:
            cur = conn.cursor()
            cur.execute("SELECT password FROM user_profile WHERE username = ?", (userName,))
            result = cur.fetchone()

        if result is None:
            flash('Invalid username. Try again.')
            return render_template('login_page.html')

        stored_hash = result[0]
        if isinstance(stored_hash, str):
            stored_hash = stored_hash.encode("utf-8")

        if bcrypt.checkpw(entered_password.encode("utf-8"), stored_hash):
            with sqlite3.connect(DB_NAME) as conn:
                cur = conn.cursor()
                user_id = cur.execute("""SELECT user_id FROM user_profile WHERE username =?""",
                                      (userName,)).fetchone()[0]
            session['username'] = userName
            session.permanent=True
            session['user_id'] = user_id
            return redirect(url_for('login_landing_page'))  # ✅ redirect after successful login
        else:
            flash("Invalid password. Try again.")
            return render_template('login_page.html')

    # GET request
    return render_template('login_page.html')


# Login landing page - Randi (Updated with Filters)
@app.route('/login_landing_page')
def login_landing_page():
    if 'username' not in session:
        return redirect(url_for('login'))

    user_name = session['username']

    # Get Filter Params
    sort_by = request.args.get('sort', 'newest')
    diet_filter = request.args.get('diet', '')

    with sqlite3.connect(DB_NAME) as conn:
        cur = conn.cursor()
        creator_id = cur.execute(
            "SELECT user_id FROM user_profile WHERE username = ?",
            (user_name,)).fetchone()
        if not creator_id:
            flash("User not found")
            return redirect(url_for('login'))
        user_id = creator_id[0]

    manager = RecipeManager()

    # 1. ALL RECIPES (Use SQL Filtering)
    all_recipes = manager.getFilteredRecipes(search_query="", sort_by=sort_by, diet_filter=diet_filter)
    all_recipes = view_comment(all_recipes)
    all_recipes = view_reaction(all_recipes)

    # 2. MY RECIPES (Fetch then Python Filter)
    my_recipes = manager.getRecipesByUser(user_id)
    my_recipes = filter_list_python(my_recipes, sort_by, diet_filter)
    my_recipes = view_comment(my_recipes)
    my_recipes = view_reaction(my_recipes)

    # 3. FAVORITE RECIPES (Fetch then Python Filter)
    fav_recipes = manager.getFavoriteRecipesByUser(user_id)
    fav_recipes = filter_list_python(fav_recipes, sort_by, diet_filter)
    fav_recipes = view_comment(fav_recipes)
    fav_recipes = view_reaction(fav_recipes)

    with sqlite3.connect(DB_NAME) as conn:
        cur = conn.cursor()
        for r in all_recipes + my_recipes + fav_recipes:
            # Optimization: This query inside loop is slow, but keeping existing logic for safety
            cur.execute("SELECT user_id FROM recipe WHERE recipe_id = ?", (r.recipe_id,))
            res = cur.fetchone()
            if res: r.user_id = res[0]

    # Only shuffle if sorting is NOT active (Newest/Default)
    if sort_by == 'newest':
        random.shuffle(my_recipes)
        random.shuffle(fav_recipes)
        random.shuffle(all_recipes)

    my_recipes = my_recipes[:4]
    fav_recipes = fav_recipes[:4]
    all_recipes = all_recipes[:4]



    return render_template(
        'login_landing_page.html',
        all_recipes=all_recipes, my_recipes=my_recipes, fav_recipes=fav_recipes,
        username=user_name, user_id=user_id,
        current_sort=sort_by, current_diet=diet_filter)


# User logout. -Randi
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


# User list for testing purposes - Randi
@app.route('/user_list_for_testing')
def user_list_for_testing():
    connect = sqlite3.connect(DB_NAME)
    cur = connect.cursor()
    cur.execute(" SELECT * FROM user_profile")
    rows = cur.fetchall()
    return render_template("user_list_for_testing.html", data=rows)

# -------------------------------------------------------------
# ROUTES: MEAL PLAN CREATION, VIEWING AND SHARING - Randi
# -------------------------------------------------------------

# Create a new meal plan - Randi
@app.route('/create_meal_plan', methods=['GET', 'POST'])
def create_meal_plan():
    print("DEBUG route triggered, request.form:", request.form)
    print("DEBUG route triggered, request.args:", request.args)
    # Check if user is logged in.
    username = session.get('username')
    if not username:
        flash("You must be logged in to create a meal plan.")
        return redirect(url_for('login'))

    if request.method == 'POST':
        print("DEBUG form keys:", request.form.keys())
        plan_name = request.form.get('plan_name')
        print("DEBUG plan_name:", plan_name)

        # Get user ID
        with sqlite3.connect(DB_NAME) as conn:
            cur = conn.cursor()
            creator_id = cur.execute(
                "SELECT user_id FROM user_profile WHERE username = ?",
                (username,)
            ).fetchone()

            if creator_id is None:
                flash("You must be logged in to create meal plan.")
                return redirect(url_for('login'))

            user_id = creator_id[0]

            # Count how many meal plans user has access to.
            creator_count = cur.execute("""SELECT COUNT(*) FROM meal_plan WHERE creator_id = ?""",
                                        (user_id,)).fetchone()[0]

            invited_count = cur.execute("""SELECT COUNT(*) FROM meal_plan_access WHERE user_id = ?""",
                                        (user_id,)).fetchone()[0]

            count = creator_count + invited_count

            # Enforce the 50-plan limit
            if count >= 50:
                flash("You can only have up to 50 meal plans. Please delete or leave some plans.")
                return redirect(url_for('list_meal_plans'))

            # Create unique invite code
            invite_code = generate_invite_code()

            # Insert the new plan
            cur.execute("""INSERT INTO meal_plan (plan_name, creator_id, invite_code) VALUES (?, ?, ?)""",
                        (plan_name, user_id, invite_code))
            meal_plan_id = cur.lastrowid  # <-- get the new meal_plan_id

            # Automatically give creator access
            cur.execute("""INSERT INTO meal_plan_access (meal_plan_id, user_id)VALUES (?, ?)""",
                        (meal_plan_id, user_id))
            conn.commit()

        flash("Meal plan created!")
        return redirect(url_for('view_meal_plan', meal_plan_id=meal_plan_id))

    return render_template("create_meal_plan.html",)


# Generate the invite code - Randi
def generate_invite_code():
    chars = string.ascii_letters + string.digits
    code = ''.join(random.choices(chars, k=6))

    with sqlite3.connect(DB_NAME) as conn:
        cur = conn.cursor()
        while cur.execute("SELECT 1 FROM meal_plan WHERE invite_code = ?",
                          (code,)).fetchone():
            code = ''.join(random.choices(chars, k=6))

    return code


# Allowed users view meal plan
@app.route('/meal_plan/<int:meal_plan_id>')
def view_meal_plan(meal_plan_id):
    # Check if user is logged in.
    username = session.get('username')
    if not username:
        flash("You must be logged in to view a meal plan.")
        return redirect(url_for('login'))

    with sqlite3.connect(DB_NAME) as conn:
        cur = conn.cursor()
        user = cur.execute("""SELECT user_id FROM user_profile WHERE username = ?""",
                           (session['username'],)).fetchone()

        if user is None:
            flash("You must be logged in.")
            return redirect(url_for('login'))

        user_id = user[0]

        # Check access permission
        if not user_has_access(user_id, meal_plan_id):
            flash("You do not have permission to view this meal plan.")
            return redirect(url_for('list_meal_plans'))

        # If allowed → show the plan
        meal_plan = cur.execute("""SELECT plan_name, creator_id, invite_code FROM meal_plan WHERE meal_plan_id = ?""",
                                (meal_plan_id,)).fetchone()

        if meal_plan is None:
            flash("Meal plan no longer exists. Creator may have deleted the plan. Select a different plan.")
            return redirect(url_for('list_meal_plans'))

        creator_name = cur.execute("""SELECT username FROM user_profile WHERE user_id = ?""",
                                   (meal_plan[1],)).fetchone()

        meal_plan_name = meal_plan[0]
        code = meal_plan[2]

        calendar_id = calendar_service.create_or_get_calendar(conn, meal_plan_id)
        session["calendar_id"] = calendar_id

        return render_template("calendar.html", meal_plan_name=meal_plan_name, meal_plan_id=meal_plan_id,
                           creator_name=creator_name[0], username=username, code=code)


# Permission Checks - Randi
def user_has_access(user_id, meal_plan_id):
    with sqlite3.connect(DB_NAME) as conn:
        cur = conn.cursor()
        result = cur.execute("""SELECT 1 FROM meal_plan_access WHERE user_id = ? AND meal_plan_id = ?""",
                             (user_id, meal_plan_id)).fetchone()
        return result is not None


# Join Meal Plan - Randi
@app.route('/join_meal_plan', methods=['GET', 'POST'])
def join_meal_plan():
    # Check if user is logged in.
    username = session.get('username')
    if not username:
        flash("You must be logged in to join a meal plan.")
        return redirect(url_for('login'))

    if request.method == 'POST':
        code = request.form.get('invite_code', '').strip()

        if not code:
            flash("Invite code cannot be empty.")
            return redirect(url_for('join_meal_plan'))

        with sqlite3.connect(DB_NAME) as conn:
            cur = conn.cursor()

            # Find plan by code
            plan = cur.execute("""SELECT meal_plan_id FROM meal_plan WHERE invite_code = ?""",
                               (str(code),)).fetchone()

            if plan is None:
                flash("Invalid invite code. Please check code and try again.")
                return redirect(url_for('join_meal_plan'))

            meal_plan_id = plan[0]

            # Find the user
            user = cur.execute("""SELECT user_id FROM user_profile WHERE username = ?""",
                               (session['username'],)).fetchone()

            if user is None:
                session.clear()
                flash("Error: Can not find an existing user. You have been logged out, please log back in.")
                return redirect(url_for('login'))

            user_id = user[0]

            # Add access and check is access already exists to avoid duplicates.
            cur.execute("""INSERT OR IGNORE INTO meal_plan_access (meal_plan_id, user_id) VALUES (?, ?)""",
                        (meal_plan_id, user_id))

            conn.commit()

        flash("Joined meal plan!")
        return redirect(url_for('view_meal_plan', meal_plan_id=meal_plan_id))

    return render_template('join_meal_plan.html')

# Leave a meal plan
@app.route('/leave_meal_plan/<int:meal_plan_id>', methods=['POST'])
def leave_meal_plan(meal_plan_id):
    # Check if user is logged in
    username = session.get('username')
    if not username:
        flash("You must be logged in to leave a meal plan.")
        return redirect(url_for('login'))

    with sqlite3.connect(DB_NAME) as conn:
        cur = conn.cursor()

        # Find the user ID
        user = cur.execute("SELECT user_id FROM user_profile WHERE username = ?", (username,)).fetchone()
        if user is None:
            session.clear()
            flash("Error: Cannot find user. You have been logged out, please log back in.")
            return redirect(url_for('login'))

        user_id = user[0]

        # Remove access to the meal plan
        cur.execute("DELETE FROM meal_plan_access WHERE meal_plan_id = ? AND user_id = ?", (meal_plan_id, user_id))
        conn.commit()

    flash("You have left the meal plan.")
    return redirect(url_for('list_meal_plans'))



# List Meal Plans - Randi
@app.route('/meal_plans')
def list_meal_plans():
    username = session.get('username')
    if not username:
        flash("You must be logged in to view your meal plans.")
        return redirect(url_for('login'))

    with sqlite3.connect(DB_NAME) as conn:
        cur = conn.cursor()

        # Get logged-in user ID
        user = cur.execute("""SELECT user_id FROM user_profile WHERE username = ?""",
                           (session['username'],)).fetchone()

        if user is None:
            flash("You must be logged in to view your meal plans.")
            return redirect(url_for('login'))

        user_id = user[0]

        # Meal plans created by the user
        created = cur.execute("""
            SELECT meal_plan_id, plan_name, creator_id, invite_code
            FROM meal_plan
            WHERE creator_id = ?
        """, (user_id,)).fetchall()

        # Meal plans user was invited to (but did not create)
        invited = cur.execute("""
            SELECT mp.meal_plan_id, mp.plan_name, mp.creator_id, u.username AS creator_name
            FROM meal_plan mp
            JOIN meal_plan_access mpa ON mp.meal_plan_id = mpa.meal_plan_id
            JOIN user_profile u ON mp.creator_id = u.user_id
            WHERE mpa.user_id = ? AND mp.creator_id != ?
        """, (user_id, user_id)).fetchall()

        # Add creator names for created plans
        created_with_names = []
        for plan in created:
            creator_name = cur.execute("SELECT username FROM user_profile WHERE user_id = ?",
                                       (plan[2],)).fetchone()[0]
            created_with_names.append({
                "meal_plan_id": plan[0],
                "plan_name": plan[1],
                "creator_name": creator_name,
                "invite_code": plan[3]
            })

        invited_with_names = []
        for plan in invited:
            invited_with_names.append({
                "meal_plan_id": plan[0],
                "plan_name": plan[1],
                "creator_name": plan[3]
            })

    return render_template("list_meal_plans.html",
                           created=created_with_names,
                           invited=invited_with_names, username=username)


# Delete a meal plan - only creator allowed
@app.route('/delete_meal_plan/<int:meal_plan_id>', methods=['POST'])
def delete_meal_plan(meal_plan_id):
    username = session.get('username')
    if not username:
        flash("You must be logged in to delete a meal plan.")
        return redirect(url_for('login'))

    with sqlite3.connect(DB_NAME) as conn:
        cur = conn.cursor()

        # Get logged-in user id
        user = cur.execute(
            "SELECT user_id FROM user_profile WHERE username = ?",
            (username,)).fetchone()
        if user is None:
            flash("You must be logged in.")
            return redirect(url_for('login'))

        user_id = user[0]

        # Check if user is the creator
        creator = cur.execute(
            "SELECT creator_id FROM meal_plan WHERE meal_plan_id = ?",
            (meal_plan_id,)
        ).fetchone()

        if creator is None:
            flash("Meal plan not found.")
            return redirect(url_for('list_meal_plans'))

        if creator[0] != user_id:
            flash("Only the creator can delete this meal plan.")
            return redirect(url_for('list_meal_plans'))

        # Delete related access entries first
        cur.execute(
            "DELETE FROM meal_plan_access WHERE meal_plan_id = ?",
            (meal_plan_id,)
        )

        # Delete the meal plan itself
        cur.execute(
            "DELETE FROM meal_plan WHERE meal_plan_id = ?",
            (meal_plan_id,)
        )

        conn.commit()
    print("Session contents:", dict(session))

    flash("Meal plan deleted successfully!")
    return redirect(url_for('list_meal_plans'))


# -------------------------------------------------------------
# ROUTES: CREATE AND VIEW COMMENTS AND REACTIONS - Randi
# -------------------------------------------------------------
# Create a comment - Randi
@app.route('/create_comment/<int:recipe_id>', methods=['POST'])
def create_comment(recipe_id):
    # Check if user is logged in.
    username = session.get('username')
    if not username:
        flash("You must be logged in to create a comment.")
        return redirect(url_for('login'))

    comment = request.form.get('comment')
    if comment is None:
        return redirect(request.referrer)

    with sqlite3.connect(DB_NAME) as conn:
        cur = conn.cursor()
        user = cur.execute("""SELECT user_id FROM user_profile WHERE username = ?""",
                           (session['username'],)).fetchone()
        if user is None:
            flash("User not found")
            return redirect(request.referrer)
        user_id = user[0]

        cur.execute(""" INSERT INTO recipe_comment (user_id, recipe_id, comment) VALUES (?, ?, ?)""",
                    (user_id, recipe_id, comment,))
        conn.commit()


    print("Comment added successfully!")
    return redirect(request.referrer)


# View a comment - Randi
def view_comment(recipe_list):
    """Attach comments to each recipe object in recipe_list."""
    if not recipe_list:
        return recipe_list

    recipe_ids = [r.recipe_id for r in recipe_list]
    placeholders = ','.join(['?'] * len(recipe_ids))

    with sqlite3.connect(DB_NAME) as conn:
        cur = conn.cursor()
        rows = cur.execute(f"""
            SELECT rc.recipe_id, rc.comment, u.username, rc.created_at
            FROM recipe_comment rc
            JOIN user_profile u ON rc.user_id = u.user_id
            WHERE rc.recipe_id IN ({placeholders})
            ORDER BY rc.created_at DESC
        """, recipe_ids).fetchall()

    comments_by_recipe = {}
    for recipe_id, comment, username, created_at in rows:
        comments_by_recipe.setdefault(recipe_id, []).append((comment, username, created_at))

    # Attach to recipe objects
    for r in recipe_list:
        r.comments = comments_by_recipe.get(r.recipe_id, [])

    return recipe_list


# Create a reaction - Randi
@app.route('/create_reaction/<int:recipe_id>', methods=['POST'])
def create_reaction(recipe_id):
    # Check if user is logged in.
    username = session.get('username')
    if not username:
        flash("You must be logged in to add a reaction.")
        return redirect(url_for('login'))

    reaction = request.form.get('reaction')
    if reaction not in ['like', 'dislike']:
        flash("Invalid Reaction")
        return redirect(request.referrer)

    with sqlite3.connect(DB_NAME) as conn:
        cur = conn.cursor()
        user = cur.execute("""SELECT user_id FROM user_profile WHERE username = ?""",
                           (session['username'],)).fetchone()
        if user is None:
            flash("User not found")
            return redirect(request.referrer)
        user_id = user[0]

        cur.execute(""" INSERT INTO use_recipe_reaction (user_id, recipe_id, reaction) VALUES (?, ?, ?) 
                    ON CONFLICT (recipe_id, user_id) DO UPDATE SET 
                    reaction = excluded.reaction, created_at = CURRENT_TIMESTAMP""",
                    (user_id, recipe_id, reaction,))

        conn.commit()
    print(f"User {user_id} reacted {reaction} to recipe {recipe_id}")
    print("Reaction added successfully!")
    return redirect(request.referrer)



def view_reaction(recipe_list):
    """Attach reaction counts to each recipe object in recipe_list."""
    if not recipe_list:
        return recipe_list

    recipe_ids = [r.recipe_id for r in recipe_list if hasattr(r, 'recipe_id') and r.recipe_id is not None]
    if not recipe_ids:
        return recipe_list

    placeholders = ','.join(['?'] * len(recipe_ids))

    with sqlite3.connect(DB_NAME) as conn:
        cur = conn.cursor()
        query = f"""
            SELECT recipe_id, reaction, COUNT(*) 
            FROM use_recipe_reaction
            WHERE recipe_id IN ({placeholders})
            GROUP BY recipe_id, reaction
        """
        rows = cur.execute(query, recipe_ids).fetchall()

    # Build dict of reactions for each recipe
    reactions_by_recipe = {rid: {} for rid in recipe_ids}
    for recipe_id, reaction, count in rows:
        reactions_by_recipe[recipe_id][reaction] = count

    # Attach reactions to each recipe object
    for r in recipe_list:
        r.reactions_dict = reactions_by_recipe.get(r.recipe_id, {})
        # Optionally, also keep list of tuples for backwards compatibility
        r.reactions = list(r.reactions_dict.items())

    return recipe_list


@app.route('/favorite_recipe/<int:recipe_id>', methods=["POST"])
def favorite_recipe(recipe_id):
    # Check if user is logged in.
    username = session.get('username')
    if not username:
        flash("You must be logged in to add a recipe to favorites.")
        return redirect(url_for('login'))
    if request.method == "POST":
        with sqlite3.connect(DB_NAME) as conn:
            cur = conn.cursor()
            user = cur.execute("""SELECT user_id FROM user_profile WHERE username = ?""",
                               (session['username'],)).fetchone()
            if user is None:
                flash("User not found")
                return redirect(url_for('favorite_recipe'))
            user_id = user[0]

            already_a_favorite = cur.execute("""SELECT 1 FROM favorite_recipes_use WHERE
                                                user_id = ? AND recipe_id = ?""",
                                             (user_id, recipe_id)).fetchone()
            if already_a_favorite:
                cur.execute("""DELETE FROM favorite_recipes_use WHERE user_id = ? AND recipe_id = ?""",
                            (user_id, recipe_id))
                flash("Recipe removed from favorites")

            else:
                cur.execute(""" INSERT INTO favorite_recipes_use (user_id, recipe_id) VALUES (?, ?)""",
                            (user_id, recipe_id,))
                flash("Recipe has been added to favorites")

            conn.commit()

    return redirect(request.referrer)


# -------------------------------------
# ROUTE: View Recipe List (Added Search Functionality - Soham)
# -------------------------------------
@app.route('/recipes')
def recipe_list():
    search_query = request.args.get('search_query', '')
    sort_by = request.args.get('sort', 'newest')
    diet_filter = request.args.get('diet', '')

    manager = RecipeManager()

    try:
        # Use the new advanced filter method
        recipes = manager.getFilteredRecipes(search_query, sort_by, diet_filter)
        recipes = view_comment(recipes)
        recipes = view_reaction(recipes)

    except sqlite3.Error as e:
        print(f"Error searching recipes: {e}")
        flash("An error occurred while searching for recipes.")
        recipes = []

    return render_template('recipe_list.html', recipes=recipes,
                           search_query=search_query,
                           current_sort=sort_by,
                           current_diet=diet_filter)


# -------------------------------------------------------------
# ADD RECIPE — Baraa (with validation + optional images)
# -------------------------------------------------------------
@app.route('/recipes/add', methods=['GET', 'POST'])
def add_recipe():
    """Display the add recipe form and handle submission."""
    if request.method == 'POST':
        name = request.form['name'].strip()
        ingredients = request.form['ingredients'].strip()
        instructions = request.form['instructions'].strip()
        diet_tags = request.form.getlist('diet[]')
        category = ",".join(diet_tags)

        # Required text fields validation
        if not name or not ingredients or not instructions:
            flash("All fields are required.")
            return redirect(url_for('add_recipe'))

        # Get user_id
        conn = database_connection(DB_NAME)
        cur = conn.cursor()
        cur.execute("SELECT user_id FROM user_profile WHERE username = ?", (session['username'],))
        user_id = cur.fetchone()[0]
        conn.close()

        # Create recipe
        new_recipe = Recipe(None, name, ingredients, instructions)
        new_recipe.category = category
        new_recipe.user_id = user_id

        manager = RecipeManager()
        recipe_id = manager.addRecipe(new_recipe)

        # --------------------------------------------
        # CREATE  AND SAVE STEPS FROM INSTRUCTIONS
        # --------------------------------------------kayo
        from Model.step_helper import split_into_steps, extract_duration

        steps_raw = split_into_steps(instructions)

        final_steps = []
        for i, s in enumerate(steps_raw, start=1):
            d = extract_duration(s)  # None if no timing
            final_steps.append((i, s, d))

        manager.saveSteps(recipe_id, final_steps)

        # ---------------------------
        # Handle images (with validation)
        # ---------------------------
        files = request.files.getlist('recipe_images')

        if files:
            upload_folder = os.path.join(app.static_folder, 'recipe_images')
            os.makedirs(upload_folder, exist_ok=True)

            with sqlite3.connect(DB_NAME) as conn:
                cur = conn.cursor()

                for file in files:
                    if not file or file.filename == "":
                        continue

                    # Validate extension
                    if not allowed_file(file.filename):
                        flash("Invalid file skipped (allowed: png, jpg, jpeg, gif).")
                        continue

                    # Validate size
                    if file_too_big(file):
                        flash("Image skipped: file too large (max 3MB). Please resize the image before uploading.")
                        continue

                    safe = secure_filename(file.filename)
                    base_name = f"recipe_{recipe_id}_{safe}"

                    # Prevent overwriting
                    unique = generate_unique_filename(upload_folder, base_name)

                    abs_path = os.path.join(upload_folder, unique)
                    rel_path = f"recipe_images/{unique}"

                    file.save(abs_path)

                    cur.execute("""
                        INSERT INTO recipe_image (recipe_id, image_path, upload_date)
                        VALUES (?, ?, DATE('now'))
                    """, (recipe_id, rel_path))

                conn.commit()

        return redirect(request.referrer)

    return render_template('recipe_add.html')



# -------------------------------------------------------------
# VIEW RECIPE — Kayo
# -------------------------------------------------------------
@app.route('/recipes/<int:recipe_id>')
def view_recipe(recipe_id):
    manager = RecipeManager()
    recipe = manager.getRecipeById(recipe_id)

    if not recipe:
        return "Recipe not found", 404

    # Recipe steps + images
    steps = manager.getSteps(recipe_id)
    images = manager.getImagesForRecipe(recipe_id)

    # Attach comments + reactions
    recipe_list = [recipe]
    view_comment(recipe_list)
    view_reaction(recipe_list)

    # Determine viewer user (used for enabling/disabling edit button)
    current_user_id = session.get('user_id')

    return render_template(
        'recipe_view.html',
        recipe=recipe,
        steps=steps,
        images=images,
        current_user_id=current_user_id  # pass this to template
    )



# -------------------------------------------------------------
# EDIT RECIPE — Baraa (with validation + images list)
# -------------------------------------------------------------
@app.route('/recipes/edit/<int:recipe_id>', methods=['GET', 'POST'])
def edit_recipe(recipe_id):
    # Must be logged in
    if 'user_id' not in session:
        flash("You must be logged in to edit a recipe.")
        return redirect(url_for('login'))

    manager = RecipeManager()
    recipe = manager.getRecipeById(recipe_id)

    if recipe is None:
        return "Recipe not found", 404

    # Security check: user must OWN the recipe
    if recipe.user_id != session['user_id']:
        flash("You cannot edit another user's recipe.")
        return redirect(url_for('view_recipe', recipe_id=recipe_id))

    # -------------------------
    # POST: Save updated recipe
    # -------------------------
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        ingredients = request.form.get('ingredients', '').strip()
        instructions = request.form.get('instructions', '').strip()

        if not name or not ingredients or not instructions:
            flash("All fields (name, ingredients, instructions) are required.")
            return redirect(url_for('edit_recipe', recipe_id=recipe_id))

        updated_recipe = Recipe(recipe_id, name, ingredients, instructions)
        manager.editRecipe(recipe_id, updated_recipe)

        flash("Recipe updated.")
        return redirect(request.referrer)

    # GET: render edit page
    images = manager.getImagesForRecipe(recipe_id)
    return render_template('recipe_edit.html', recipe=recipe, images=images)




# -------------------------------------------------------------
# DELETE RECIPE — Baraa (also delete images)
# -------------------------------------------------------------
@app.route('/delete_recipe/<int:recipe_id>', methods=['POST'])
def delete_recipe(recipe_id):
    # Delete images from disk + DB first
    upload_root = app.static_folder  # e.g., cmpt370_project_user_management/static

    with sqlite3.connect(DB_NAME) as conn:
        cur = conn.cursor()
        cur.execute("SELECT image_path FROM recipe_image WHERE recipe_id = ?", (recipe_id,))
        rows = cur.fetchall()

        for (image_path,) in rows:
            abs_path = os.path.join(upload_root, image_path)
            if os.path.exists(abs_path):
                os.remove(abs_path)

        cur.execute("DELETE FROM recipe_image WHERE recipe_id = ?", (recipe_id,))
        conn.commit()

    # Delete recipe row
    manager = RecipeManager()
    manager.deleteRecipe(recipe_id)

    flash("Recipe and its images deleted.")
    return redirect(url_for('recipe_list'))


# -------------------------------------
# ROUTE: Upload Recipe Image(s) - Baraa
# -------------------------------------
@app.route('/recipes/<int:recipe_id>/upload_image', methods=['POST'])
def upload_image(recipe_id):
    manager = RecipeManager()
    if manager.getRecipeById(recipe_id) is None:
        flash("Recipe not found.")
        return redirect(url_for('recipe_list'))

    files = request.files.getlist('recipe_images')
    if not files:
        flash("No files selected.")
        return redirect(url_for('edit_recipe', recipe_id=recipe_id))

    upload_folder = os.path.join(app.static_folder, 'recipe_images')
    os.makedirs(upload_folder, exist_ok=True)

    saved_any = False

    with sqlite3.connect(DB_NAME) as conn:
        cur = conn.cursor()

        for file in files:
            if not file or file.filename == "":
                continue

            # Extension check
            if not allowed_file(file.filename):
                flash("Skipped: invalid file type.")
                continue

            # Size check
            if file_too_big(file):
                flash("Skipped: one or more images exceeded 3MB. Please resize before uploading.")
                continue

            safe_name = secure_filename(file.filename)
            base_name = f"recipe_{recipe_id}_{safe_name}"
            unique = generate_unique_filename(upload_folder, base_name)

            abs_path = os.path.join(upload_folder, unique)
            rel_path = f"recipe_images/{unique}"

            file.save(abs_path)

            cur.execute("""
                INSERT INTO recipe_image (recipe_id, image_path, upload_date)
                VALUES (?, ?, DATE('now'))
            """, (recipe_id, rel_path))

            saved_any = True

        conn.commit()

    flash("Image(s) uploaded." if saved_any else "No valid images uploaded.")
    return redirect(url_for('edit_recipe', recipe_id=recipe_id))



# -------------------------------------
# ROUTE: Delete a single Recipe Image - Baraa
# -------------------------------------
@app.route('/recipes/<int:recipe_id>/images/<int:image_id>/delete', methods=['POST'])
def delete_image(recipe_id, image_id):
    upload_root = app.static_folder

    with sqlite3.connect(DB_NAME) as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT image_path
            FROM recipe_image
            WHERE image_id = ? AND recipe_id = ?
        """, (image_id, recipe_id))
        row = cur.fetchone()

        if not row:
            flash("Image not found.")
            return redirect(url_for('edit_recipe', recipe_id=recipe_id))

        image_path = row[0]
        abs_path = os.path.join(upload_root, image_path)

        if os.path.exists(abs_path):
            os.remove(abs_path)

        cur.execute("DELETE FROM recipe_image WHERE image_id = ?", (image_id,))
        conn.commit()

    flash("Image deleted.")
    return redirect(url_for('edit_recipe', recipe_id=recipe_id))



# -------------------------------------
# ROUTE: Integrating Grocery list - Baraa
# -------------------------------------
@app.route('/add_ingredient_to_list', methods=['POST'])
def add_ingredient_to_list():
    if 'username' not in session:
        flash("Login required.")
        return redirect(url_for('login'))

    ingredient = request.form['ingredient'].strip()
    quantity = request.form.get('quantity', '1').strip()

    if ingredient == "":
        flash("Invalid ingredient.")
        return redirect(request.referrer)

    conn = database_connection(DB_NAME)
    cur = conn.cursor()

    cur.execute("SELECT user_id FROM user_profile WHERE username = ?", (session['username'],))
    user_id = cur.fetchone()[0]

    cur.execute("""
            INSERT INTO grocery_list (user_id, item_text, quantity)
            VALUES (?, ?, ?)
        """, (user_id, ingredient, quantity))

    conn.commit()
    conn.close()

    flash(f"Added '{ingredient}' to grocery list ✔")
    return redirect(request.referrer)



# -------------------------------------------------------------
# MY RECIPES — Only show recipes created by this user
# -------------------------------------------------------------
@app.route('/my_recipes')
def my_recipes():
    if 'username' not in session:
        return redirect(url_for('login'))

    search_query = request.args.get('search_query', '')
    sort_by = request.args.get('sort', 'newest')
    diet_filter = request.args.get('diet', '')

    # find the logged-in user's ID
    with sqlite3.connect(DB_NAME) as conn:
        cur = conn.cursor()
        cur.execute("SELECT user_id FROM user_profile WHERE username = ?", (session['username'],))
        result = cur.fetchone()

        if not result:
            flash("Error: Could not find user.")
            return redirect(url_for('logout'))

        user_id = result[0]

    manager = RecipeManager()
    recipes = manager.getRecipesByUser(user_id)
    recipes = filter_list_python(recipes, sort_by, diet_filter)
    recipes = view_comment(recipes)
    recipes = view_reaction(recipes)

    with sqlite3.connect(DB_NAME) as conn:
        cur = conn.cursor()
        for r in recipes:
            cur.execute("""SELECT user_id FROM recipe WHERE recipe_id = ?""",
                        (r.recipe_id,))
            r.user_id = cur.fetchone()[0]

    return render_template('my_recipes.html', recipes=recipes)


# -------------------------------------------------------------
# FAVORITE RECIPES — Show a users favorite recipes
# -------------------------------------------------------------
@app.route('/favorite_recipes')
def favorite_recipes():
    if 'username' not in session:
        return redirect(url_for('login'))


    sort_by = request.args.get('sort', 'newest')
    diet_filter = request.args.get('diet', '')

    # find the logged-in user's ID
    with sqlite3.connect(DB_NAME) as conn:
        cur = conn.cursor()
        cur.execute("SELECT user_id FROM user_profile WHERE username = ?", (session['username'],))
        result = cur.fetchone()

        if not result:
            flash("Error: Could not find user.")
            return redirect(url_for('logout'))

        user_id = result[0]

    manager = RecipeManager()
    recipes = manager.getFavoriteRecipesByUser(user_id)
    recipes = filter_list_python(recipes, sort_by, diet_filter)
    recipes = view_comment(recipes)
    recipes = view_reaction(recipes)


    with sqlite3.connect(DB_NAME) as conn:
        cur = conn.cursor()
        for r in recipes:
            cur.execute("""SELECT user_id FROM recipe WHERE recipe_id = ?""",
                        (r.recipe_id,))
            r.user_id = cur.fetchone()[0]

    return render_template('favorite_recipes.html', recipes=recipes)


# -------------------------------------------------------------
# MY RECIPES — Only show recipes created by this user
# -------------------------------------------------------------
@app.route('/all_recipes')
def all_recipes():
    if 'username' not in session:
        return redirect(url_for('login'))

    # find the logged-in user's ID
    with sqlite3.connect(DB_NAME) as conn:
        cur = conn.cursor()
        cur.execute("SELECT user_id FROM user_profile WHERE username = ?", (session['username'],))
        result = cur.fetchone()

        if not result:
            flash("Error: Could not find user.")
            return redirect(url_for('logout'))

        user_id = result[0]

    manager = RecipeManager()
    recipes = manager.getAllRecipes()
    recipes = view_comment(recipes)
    recipes = view_reaction(recipes)

    return render_template('recipe_list.html', recipes=recipes)


# -------------------------------------------------------------
# Calendar Routes - Jordan
# -------------------------------------------------------------
# calendar view - used for render calendar from recipe_view with preloaded recipe_id
@app.route('/calendar', methods=["POST"])
def calendar_view():
    # Get recipe_id, ensure user and calendar both in session or redirect
    recipe_id = request.args.get('recipe_id')
    username = session.get('username')
    if username is None:
        flash("You need to login first.")
        return redirect(url_for('login'))
    calendar_id = session.get('calendar_id')
    if calendar_id is None:
        flash("Calendar not loaded, select meal plan first")
        return redirect(url_for('list_meal_plans'))

    # Open database connection
    connection = sqlite3.connect(DB_NAME)
    try:
        #get user_id, meal_plan_id and other parameters for calendar render
        cursor = connection.cursor()
        cursor.execute("SELECT user_id FROM user_profile WHERE username = ?", (username,))
        user_id = cursor.fetchone()
        cursor.execute("SELECT meal_plan_id FROM calendar_schedule WHERE calendar_id = ?", (calendar_id,))
        meal_plan_id = cursor.fetchone()

        # Check for error in getting user_id / meal_plan_id
        if not meal_plan_id:
            print("Error in calendar view route - meal_plan_id missing")
            return redirect(url_for("home"))

        # Check access permission
        if not user_has_access(user_id[0], meal_plan_id[0]):
            flash("You do not have permission to view this meal plan.")
            return redirect(url_for('list_meal_plans'))

        # If allowed → show the plan
        meal_plan = cursor.execute("""SELECT plan_name, creator_id, invite_code FROM meal_plan WHERE meal_plan_id = ?""",
                                (meal_plan_id[0],)).fetchone()

        if meal_plan is None:
            flash("Meal plan no longer exists. Creator may have deleted the plan. Select a different plan.")
            return redirect(url_for('list_meal_plans'))

        creator_name = cursor.execute("""SELECT username FROM user_profile WHERE user_id = ?""",
                                   (meal_plan[1],)).fetchone()

        meal_plan_name = meal_plan[0]
        code = meal_plan[2]

        return render_template("calendar.html", calendar_id=calendar_id, recipe_id=recipe_id, meal_plan_name=meal_plan_name, meal_plan_id=meal_plan_id[0],
                           creator_name=creator_name[0], username=username, code=code)
    finally:
        # Close connection when done
        connection.close()

# load calendar events - FullCalendar API route to load all events for current calendar_id - Jordan
@app.route("/api/events")
def api_events():
    # Open database connection
    connection = sqlite3.connect(DB_NAME)
    try:
        # Get calendar_id from session
        if "calendar_id" not in session:
            return redirect(url_for('home'))
        calendar_id = session["calendar_id"]
        # Pull events from database
        events = calendar_service.get_calendar_events(connection, calendar_id)
        # return all calendar events in FullCalendar format
        full_calendar_events = []
        for event in events:
            full_calendar_events.append({
                "id": event["event_id"],
                "title": event["event_name"],
                "start": event["event_date"],
                "extendedProps": {
                    "timeSlot": event["event_time"],
                    "recipe_id": event["recipe_id"],
                    "recurrence_id": event["recurrence_id"]
                }
            })
        # return all calendar events
        return jsonify(full_calendar_events)
    finally:
        # Close connection when done
        connection.close()

# load calendar recipes - FullCalendar API route to load all recipes into calendar - Jordan
@app.route("/api/recipes")
def api_recipes():
    connection = sqlite3.connect(DB_NAME)
    cursor = connection.cursor()
    try:
        cursor.execute("SELECT recipe_id, recipe_name FROM recipe ORDER BY recipe_id;")
        rows = cursor.fetchall()
        all_recipes=[]
        for id,name in rows:
            all_recipes.append({"recipe_id": id, "recipe_name": name})
        return jsonify(all_recipes)
    except sqlite3.OperationalError:
        return jsonify([])
    finally:
        connection.close()

# add calendar event - FullCalendar API route to add new event for current calendar_id - Jordan
@app.route("/api/events", methods=["POST"])
def api_add_event():
    connection = sqlite3.connect(DB_NAME)
    try:
        # Get calendar_id from session
        if "calendar_id" not in session:
            return redirect(url_for('home'))
        calendar_id = session["calendar_id"]
        # Create event using calendar service
        data = request.json
        event_id = calendar_service.insert_calendar_event(
            connection,
            recipe_id=data["recipe_id"],
            calendar_id=calendar_id,
            event_name=data["recipe_name"],
            event_date=data["event_date"],
            event_time=data["event_time"]
        )
        return jsonify({"event_id": event_id})
    except CalendarError as e:
        return jsonify({"error": str(e)}), 409
    finally:
        # Close connection when done
        connection.close()

# delete calendar event - FullCalendar API route to delete event for current calendar_id - Jordan
@app.route("/api/events/<int:event_id>", methods=["DELETE"])
def api_delete_event(event_id):
    # Open database connection
    connection = sqlite3.connect(DB_NAME)
    try:
        # Get calendar_id from session - not required but check for still in session
        if "calendar_id" not in session:

            return redirect(url_for('home'))
        deleted_event = calendar_service.delete_calendar_event(connection, event_id)
        #return True
        return jsonify({"event_deleted": True})
    finally:
        # Close connection when done
        connection.close()

# update calendar event - FullCalendar API route to update event for current calendar_id - Jordan
@app.route("/api/events/<int:event_id>", methods=["PATCH"])
def api_update_event(event_id):
    # Open database connection
    connection = sqlite3.connect(DB_NAME)
    try:
        # Get calendar_id from session
        if "calendar_id" not in session:
            return redirect(url_for('home'))
        # Get request update data
        data = request.json
        # Update event and return True
        calendar_service.update_event(
            connection,
            event_id,
            new_date=data.get("event_date"),
            new_time=data.get("event_time"),
            recipe_id=data.get("recipe_id")
        )
        return jsonify({"event_updated": True})
    except CalendarError as e:
        return jsonify({"error": str(e)}), 409
    finally:
        # Close connection when done
        connection.close()

# add recurring event - FullCalendar API route to add new recurring event for current calendar_id - Jordan
@app.route("/api/recurring", methods=["POST"])
def api_add_recurring():
    connection = sqlite3.connect(DB_NAME)
    try:
        # Get calendar_id from session
        if "calendar_id" not in session:
            return redirect(url_for('home'))
        calendar_id = session["calendar_id"]
        # Get data from request
        data = request.json
        parent_event_id = data["parent_event_id"]
        frequency = data["frequency"]
        duration = data["duration"]
        start_date = data["start_date"]
        #Insert recurring event details into database recurring_event table
        recurring_event_id = calendar_service.insert_recurring_event(connection, parent_event_id, frequency, duration, start_date)
        #Generate calendar events based on recurrence details
        calendar_service.generate_recurring_events(connection,parent_event_id, recurring_event_id,frequency, duration, start_date)
        return jsonify({"recurring_event_id": recurring_event_id})
    except CalendarError as e:
        return jsonify({"error": str(e)}), 409
    finally:
        #Close connection when done
        connection.close()

# delete recurring event series - FullCalendar API route to delete all recurring event for current calendar_id & recurring_event_id
@app.route("/api/recurring/<int:recurring_event_id>", methods=["DELETE"])
def api_delete_recurring_event(recurring_event_id):
    # Open database connection
    connection = sqlite3.connect(DB_NAME)
    try:
        # Get calendar_id from session - not required but check for still in session
        if "calendar_id" not in session:
            return redirect(url_for('home'))
        # Delete event(s)
        calendar_service.delete_recurring_series(connection, recurring_event_id)
        return jsonify({"event_deleted": True})
    finally:
        # Close connection when done
        connection.close()


# --------- Baraa: Image upload config + validation ---------
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}
MAX_IMAGE_SIZE = 3 * 1024 * 1024  # 3 MB

def allowed_file(filename: str) -> bool:
    """Check if file extension is allowed."""
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def file_too_big(file) -> bool:
    """Check file size exceeds 3MB."""
    file.seek(0, os.SEEK_END)
    size = file.tell()
    file.seek(0)
    return size > MAX_IMAGE_SIZE


def generate_unique_filename(folder, base_name):
    """Avoid filename collisions by adding (1), (2), etc."""
    name, ext = os.path.splitext(base_name)
    unique = base_name
    counter = 1

    while os.path.exists(os.path.join(folder, unique)):
        unique = f"{name}({counter}){ext}"
        counter += 1

    return unique



# -------------------------------------------------------------
# STARTUP
# -------------------------------------------------------------
if __name__ == '__main__':
    conn = database_connection(DB_NAME)
    if conn is not None:
        # creates tables and apply updates
        create_tables(conn)
        update_tables(conn)
        conn.close()
    app.run(debug=True)

#Flask application setup and route definitions - Jordan
#Todo: Integrate with main web application Flask script
#Todo: debug threading error with CalendarService
import os
from calendar_service import CalendarService
from flask import Flask, render_template, request, redirect, url_for, session, jsonify

app = Flask(__name__)
app.secret_key = os.urandom(24)
service = CalendarService()

#Basic temporary index before integrating with user login function
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        #proceeding with user_id
        session["user_id"] = request.form.get("user_id")
        return redirect(url_for("calendar_view"))
    else:
        return render_template("index.html")

#Helper method to get calendar id
def get_calendar():
    user_id = session.get("user_id")
    if user_id is None:
        return None
    calendar_id = service.create_new_calendar(user_id)
    return calendar_id

#Calendar View route
@app.route('/calendar')
def calendar_view():
    if "user_id" not in session:
        return redirect(url_for("index"))
    else:
        calendar_id = get_calendar()
        return render_template("calendar.html",calendar_id=calendar_id)

#API - Get Events for current calendar
@app.route("/api/events")
def api_events():

    #Get calendar_id for user_id, then get corresponding calendar events
    calendar_id = get_calendar()
    if calendar_id is None:
        return jsonify({"error": "User not logged in"}), 401
    events = service.get_calendar_events(calendar_id)

    #Convert to FullCalendar JSON format
    full_calendar_events = []
    for event in events:
        full_calendar_events.append({
            "id": event.getEventID(),
            "title": event.getEventName(),
            "start": event.getEventDate(),
            "extendedProps":{
                "timeSlot": event.getEventTime()
            }
        })
    return jsonify(full_calendar_events)


#API - Add new event
@app.route("/api/events", methods=["POST"])
def api_add_event():
    data = request.json
    calendar_id = get_calendar()
    if calendar_id is None:
        return jsonify({"error": "no calendar id"}), 400

    #Create event using calendar service
    event_id = service.insert_calendar_event(
        recipe_id=data["recipe_id"],
        calendar_id=calendar_id,
        event_name=data["event_name"],
        event_date=data["event_date"],
        event_time=data["event_time"]
    )
    return jsonify({"event_id": event_id})

#API - delete existing event
@app.route("/api/events/<int:event_id>", methods=["DELETE"])
def api_delete_event(event_id):
    deleted_event = service.delete_calendar_event(event_id)
    if deleted_event is None:
        return jsonify({"event_deleted": False}), 404
    return jsonify({"event_deleted": True})

if __name__ == "__main__":
    app.run(debug=True)
// Linking the user and comments buttons - Randi
document.addEventListener('DOMContentLoaded', function(){
    const button1 = document.getElementById('CreateProfile')
    const button2 = document.getElementById('try_again')
    const button3 = document.getElementById('comment')
    const button4 = document.getElementById('home')
    const button5 = document.getElementById('login')
    const button6 = document.getElementById('logout')
    const button7 = document.getElementById('calendar_view')

    button1.addEventListener('click',function(event) {
        event.preventDefault()
        window.location.href = "/create_profile";

    });

    button2.addEventListener('click',function(event) {
        event.preventDefault()
        window.location.href = "/login_page";
    });

    button3.addEventListener('click',function(event){
        event.preventDefault()
        window.location.href = "/use_home_page";
    });

    button4.addEventListener('click', function (event){
        event.preventDefault()
        window.location.href = "/view_comments";
    });

    button5.addEventListener('click',function(event){
        event.preventDefault()
        window.location.href = "/login_page";
    });

    button6.addEventListener('click',function (event){
        event.preventDefault()
        window.location.href = "/login_page";
    });
    button7.addEventListener('click', function(event){
        event.preventDefault()
        window.location.href = "/calendar";
    })


});
function closePopup() {
    document.getElementById('popup').style.display = 'none';
}


/**
 * Calendar event listener system - uses FullCalender addon and event listeners to handle all interactions on Calendar and Modal Boxes
 * FullCalendar Standard is a free, open source JS Calendar - https://fullcalendar.io/ - Styling and Script loaded in calendar.html
 * Implemented by Jordan
 */

document.addEventListener('DOMContentLoaded',function(){
    //declare instance variable of the calendar element, list of all recipes
    const calendarEl = document.getElementById('calendar');
    let recipeList = [];

    /**
     * Initialize FullCalendar - Required plugins; Initial (and only) view set to day grid per one month; local timezone;
     * top toolbar navigation allows previous/next month and going back to today, no daily/weekly view navigation;
     * FC events loaded with api/events route; clicking on dates / existing events opens relevant modal boxes;
     * Setting event order to be consistent based on time slot, works for empty time slots (Breakfast->Lunch->Dinner->Snack);
     * @type {FullCalendar.Calendar}
     */
    const calendar = new FullCalendar.Calendar(calendarEl,{

        initialView: 'dayGridMonth',
        timeZone: 'local',
        headerToolbar: {
            left: 'prev,next today',
            center: 'title',
            right: ''
        },
        events: '/api/events',
        dateClick: function (info){
            openAddModal(info.dateStr);
        },
        eventClick: function (info){
            openViewModal(info.event)
        },
        eventOrder: function( a, b){
            const order = {"Breakfast": 1, "Lunch": 2, "Dinner": 3, "Snack": 4};
            const timeA = order[a.extendedProps.timeSlot] || 999;
            const timeB = order[b.extendedProps.timeSlot] || 999;
            return timeA - timeB;
        }
    });
    //Show calendar
    calendar.render();

    /**
     * loadRecipes function - used to load calendar with all recipes from api/recipes route - for adding to new events
     * only loads recipe id and recipe name
     */
    async function loadRecipes(){
        //Fetch recipes from manager
        const response = await fetch('api/recipes');

        //Check response - if ok, send to helper to populate options list
        if (response.ok) {
            recipeList = await response.json();
            populateOptions(document.getElementById('recipeSelect'), recipeList);
            populateOptions(document.getElementById('editRecipeSelect'), recipeList);
        }

        else{
            alert("Failed to Load recipes to calendar");
        }
    }

    /**
     * populateOptions helper function - used to iterate through recipeList and populate recipe selections in add/edit Modal
     * @param selectElement - Select element being populated
     * @param recipes - List of all recipe name and ids
     */
    function populateOptions(selectElement, recipes){
        //Declare select element instance variable and clear any existing content
        selectElement.innerHTML = '';
        //Iterate through recipe list, creating and adding each option
        recipes.forEach((recipe, index) => {
            const option = document.createElement('option');
            option.value = recipe.recipe_id; //ID passed to event
            option.textContent = `${index +1}. ${recipe.recipe_name}`;
            selectElement.appendChild(option)
        });
    }

    //Declare all Modal instance variables - Add, View, Edit, Error
    const addModal = document.getElementById('addModal');
    const viewModal = document.getElementById('viewModal');
    const editModal = document.getElementById('editModal');
    const alertModal = document.getElementById('alertModal');

    /**
     * showAlertModal function - used to show the alert modal, which displays error messages
     * @param message - message displayed
     * @param title
     */
    function showAlertModal(message, title = 'Error'){
        const alertTitle = document.getElementById('alert_title');
        const alertMessage = document.getElementById('alert_message');
        alertTitle.textContent = title;
        alertMessage.textContent = message;
        alertModal.classList.remove('hidden');
    }

    //Set up Close button listener for the AlertModal
    document.getElementById('alert_close').addEventListener('click', () =>{
        alertModal.classList.add('hidden');
    });

    /**
     * openAddModal function, used to show the UI for adding an event
     * Form is cleared on opening, other than date parameter
     * @param dateStr - date string YYYY-MM-DD passed from FullCalendar that was clicked on
     */
    function openAddModal(dateStr){
        document.getElementById('addForm').reset();
        //Set date based on clicked date, make read only
        const dateInput = document.getElementById('addDate');
        dateInput.value = dateStr;
        dateInput.setAttribute('readonly',true);
        //Show Add Modal
        addModal.classList.remove('hidden');
        //Load Recipe List
        if (recipeList.length ===0){
            loadRecipes();
        }
    }

    //Set up Submit button listener for the AddModal
    document.getElementById('addForm').addEventListener('submit', async (e) =>{
        e.preventDefault();
        //Declare instance variables of recipeSelect and selected option
        const recipeSelect = document.getElementById('recipeSelect');
        const selectedRecipe = recipeSelect.options[recipeSelect.selectedIndex];

        //Format user fields
        const payload = {
            recipe_id: parseInt(recipeSelect.value,10),
            recipe_name: selectedRecipe.textContent.split('. ')[1],
            event_date: document.getElementById('addDate').value,
            event_time: document.getElementById('addTimeSlot').value
        };

        //Send post request - await response
        const response = await fetch('/api/events',{
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(payload)
        });

        //Check response of adding event, if ok - update calendar and hide modal
        if (response.ok){
            const data = await response.json();
            calendar.refetchEvents();
            addModal.classList.add('hidden');
        }
        else if (response.status === 409){
            const err = await response.json();
            showAlertModal(err.error, 'Duplicate event.')
        }
        else{
            alert('Failed to add Event.');
        }
    });

    //Set up Cancel button listener for the AddModal
    document.getElementById('addCancel').addEventListener('click',() =>{
        addModal.classList.add('hidden');
    });

    /**
     * openViewModal function - used to show calendar event details and option to delete
     * details are shown, eventID is saved for delete, modal is not hidden
     * @param eventObj - event object clicked on in calendar view
     */
    function openViewModal(eventObj){
        //Pull event details from the FullCalendar event object
        document.getElementById('viewTitle').textContent = eventObj.title;
        document.getElementById('viewDate').textContent = eventObj.startStr;
        document.getElementById('viewTime').textContent = eventObj.extendedProps.timeSlot;
        document.getElementById('viewRecipe').textContent = eventObj.extendedProps.recipe_id;

        //Store event_id with delete and edit buttons, edit stores original date and time
        const deleteButton = document.getElementById('deleteBtn');
        deleteButton.dataset.eventId = eventObj.id;
        const editButton = document.getElementById('editBtn');
        editButton.dataset.eventId = eventObj.id;
        editButton.dataset.originalDate = eventObj.startStr;
        editButton.dataset.originalTime = eventObj.extendedProps.timeSlot;
        editButton.dataset.recipeId = eventObj.extendedProps.recipe_id;

        //Store parameters with recurring button
        const recurringButton = document.getElementById('recurringBtn');
        recurringButton.dataset.eventId = eventObj.id;
        recurringButton.dataset.startDate = eventObj.startStr;

        //Get recurring event id, if it exists
        const recurringId = eventObj.extendedProps.recurrenceId;
        const recurrenceInfo = document.getElementById('recurrenceInfo');

        //Check for recurring event, if exists, show recurring info
        if (recurringId != null){
            recurrenceInfo.textContent = 'Recurring_event_id: ${recurringId}';
            recurrenceInfo.classList.remove('hidden');
            document.getElementById('deleteSeriesBtn').dataset.recurrenceId = recurringId;
        } else {
            recurrenceInfo.classList.add('hidden');
        }

        //Make viewable
        viewModal.classList.remove('hidden');
    }

    //Set up Delete button listener for the View Modal
    document.getElementById('deleteBtn').addEventListener('click', async (e) =>{
        //pull event_id
        const eventId = e.target.dataset.eventId;
        if (!eventId){
            return;
        }
        if (!confirm('Delete this event?')){
            return;
        }
        //Send delete request - await response
        const response = await fetch(`/api/events/${eventId}`,{
            method: 'DELETE'
        });

        //Check response if successful, remove event from FullCalendar
        if (response.ok){
            const event_delete = calendar.getEventById(eventId);
            if(event_delete){
                event_delete.remove();
            }
            //Hide viewModal
            viewModal.classList.add('hidden');
        }
        else{
            alert('Failed to delete event.');
        }

    });

    //Set up Close button listener for the View Modal
    document.getElementById('viewClose').addEventListener('click', () =>{
        viewModal.classList.add('hidden');
    });

    //Set up Edit button listener for the View Modal - Shows editModal Todo: move into openEditModal function for consistency?
    document.getElementById('editBtn').addEventListener('click', e=>{
        //Pull data from edit button
        const eventId = e.target.dataset.eventId;
        const date = e.target.dataset.originalDate;
        const time = e.target.dataset.originalTime;
        const recipeId = e.target.dataset.recipeId;

        //Load Recipes if needed
        if (recipeList.length === 0){
            loadRecipes();
        }

        //Prepopulate the form date and time
        document.getElementById('editDate').value = date;
        document.getElementById('editTimeSlot').value = time;
        //Prepopulate recipe list with helper function - If recipeId already exists, make it the current selection
        const recipeSelection = document.getElementById('editRecipeSelect');
        populateOptions(recipeSelection,recipeList);
        if (recipeId != null){
            recipeSelection.value = recipeId;
        }

        //Pass event_id for PATCH request
        const editForm = document.getElementById('editForm');
        editForm.dataset.eventId = eventId;

        //Show edit modal
        editModal.classList.remove('hidden');
    });

    //Set up Submit button listener for the Edit Modal
    document.getElementById('editForm').addEventListener('submit', async e=>{
        e.preventDefault();

        //pull data from edit button
        const editForm = e.target;
        const eventId = editForm.dataset.eventId;
        const newDate = document.getElementById('editDate').value;
        const newTime = document.getElementById('editTimeSlot').value;
        const recipeId = parseInt(document.getElementById('editRecipeSelect').value,10)

        //build payload
        const payload = {
            event_date: newDate,
            event_time: newTime,
            recipe_id: recipeId
        };

        //Send patch request
        const response = await fetch(`/api/events/${eventId}`,{
            method: 'PATCH',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(payload)
        });

        //Check response
        if (response.ok){ //Refresh and hide modals
            calendar.refetchEvents();
            editModal.classList.add('hidden');
            viewModal.classList.add('hidden');
        }
        else if(response.status === 409){
            const errorObj = await response.json();
            showAlertModal(errorObj.error, 'Duplicate Event.');
        }
        else{
            alert('Failed to add Event.');
        }
    })

    //Set up Cancel button listener for the Edit Modal
    document.getElementById('editCancel').addEventListener('click', () =>{
        editModal.classList.add('hidden');
    });

    //Set up Recurring button listener for the View Modal Shows recurringModal Todo: move into openRecurringModal function for consistency?
    document.getElementById('recurringBtn').addEventListener('click', e =>{
        //Get data from button
        const eventId = document.getElementById('recurringBtn').dataset.eventId;
        const startDate = document.getElementById('recurringBtn').dataset.startDate;
        const recipeTitle = document.getElementById('recurringBtn').dataset.recipeTitle;
        const recurringModal = document.getElementById('recurringModal');

        //Send data to modal
        recurringModal.dataset.eventId = eventId;
        recurringModal.dataset.startDate = startDate;
        recurringModal.dataset.recipeTitle = recipeTitle;

        //Refresh the form
        document.getElementById('recurringForm').reset();

        //Show Modal
        recurringModal.classList.remove('hidden');
    });

    //Set up Submit button for recurring modal
    document.getElementById('recurringForm').addEventListener('submit', async e =>{
        e.preventDefault();
        //Declare modal and get event details
        const recurringModal = document.getElementById('recurringModal');
        const parentId = recurringModal.dataset.eventId;
        const startDate = recurringModal.dataset.startDate;

        //Get user fields
        const frequency = document.getElementById('recurringFrequency').value;
        const duration = parseInt(document.getElementById('recurringDuration').value, 10);

        //build payload
        const payload = {
            parent_event_id: parentId,
            frequency: frequency,
            duration: duration,
            start_date: startDate
        };

        //POST and await for response
        const response = await fetch('/api/recurring',{
            method: 'POST',
            headers:{ 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        //Check response
        if (response.ok){
            calendar.refetchEvents();
            recurringModal.classList.add('hidden');
        } else{
            const err = await response.json();
            showAlertModal(err.error || 'Failed to create recurring event');
        }

    });


    //Set up Cancel button for recurring modal
    document.getElementById('recurringCancel').addEventListener('click', () => {
        document.getElementById('recurringModal').classList.add('hidden');
    });

});



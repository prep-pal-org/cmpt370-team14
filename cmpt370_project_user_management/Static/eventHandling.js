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
 * Todo: Still requires UI/handlers for repeating events
 * Implemented by Jordan
 */

document.addEventListener('DOMContentLoaded',function(){
    //declare instance variable of the calendar element
    const calendarEl = document.getElementById('calendar');

    /**
     * Initialize FullCalendar
     * Monthly grid of days, local timezone, header, API events
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
        }
    });
    //Show calendar
    calendar.render();

    //Declare Modal instance variables
    const addModal = document.getElementById('addModal');
    const viewModal = document.getElementById('viewModal');
    const alertModal = document.getElementById('alertModal');
    const alertTitle = document.getElementById('alert_title');
    const alertMessage = document.getElementById('alert_message');
    const alertClose = document.getElementById('alert_close');
    /**
     * openAddModal function, used to show the UI for adding an event
     * Form is cleared on opening, other than date parameter
     * @param dateStr - date string YYYY-MM-DD passed from FullCalendar
     */
    function openAddModal(dateStr){
        document.getElementById('addForm').reset();
        const dateInput = document.getElementById('addDate');
        dateInput.value = dateStr;
        dateInput.setAttribute('readonly',true);
        addModal.classList.remove('hidden');

    }

    function showAlert(message, title = 'Error'){
        alertTitle.textContent = title;
        alertMessage.textContent = message;
        alertModal.classList.remove('hidden');
    }

    //Set up Submit and Close listeners to the AddModal
    document.getElementById('addForm').addEventListener('submit', async (e) =>{
        e.preventDefault();
        //Pull user fields
        //TODO: Recipe_ID to be replaced with search integration
        const payload = {
            recipe_id: parseInt(document.getElementById('addRecipe').value,10),
            event_name: document.getElementById('addRecipeName').value.trim(),
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
            showAlert(err.error, 'Duplicate event.')
        }
        else{
            alert('Failed to add Event.');
        }
    });
    document.getElementById('addCancel').addEventListener('click',() =>{
        addModal.classList.add('hidden');
    });
    alertClose.addEventListener('click', () =>{
        alertModal.classList.add('hidden');
    })

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

        //Make viewable
        viewModal.classList.remove('hidden');
    }

    //Add view modal event listener for delete button
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
    //Add viewModal event listener for edit button
    document.getElementById('editBtn').addEventListener('click', e=>{
        //Pull data from edit button
        const eventId = e.target.dataset.eventId;
        const date = e.target.dataset.originalDate;
        const time = e.target.dataset.originalTime;

        //Prepopulate the form
        document.getElementById('editDate').value = date;
        document.getElementById('editTimeSlot').value = time;
        document.getElementById('editForm');
        editForm.dataset.eventId = eventId;

        //Show edit modal
        editModal.classList.remove('hidden');
    });

    //Add viewModal event listener for close button
    document.getElementById('viewClose').addEventListener('click', () =>{
        viewModal.classList.add('hidden');
    });

    //Add editModal event listener for submit button
    document.getElementById('editForm').addEventListener('submit', async e=>{
        e.preventDefault();

        //pull data from edit button
        const editForm = e.target;
        const eventId = editForm.dataset.eventId;
        const newDate = document.getElementById('editDate').value;
        const newTime = document.getElementById('editTimeSlot').value;

        //build payload
        const payload = {
            event_date: newDate,
            event_time: newTime
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
            const error = await response.json();
            showAlert(error, 'Duplicate Event.');
        }
        else{
            alert('Failed to add Event.');
        }
    })

    //Add editModal event listener for cancel button
    document.getElementById('editCancel').addEventListener('click', () =>{
        editModal.classList.add('hidden');
    });

});



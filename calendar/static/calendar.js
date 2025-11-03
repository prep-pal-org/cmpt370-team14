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

    /**
     * openAddModal function, used to show the UI for adding an event
     * Form is cleared on opening, other than date parameter
     * @param dateStr - date string YYYY-MM-DD passed from FullCalendar
     */
    function openAddModal(dateStr){
        document.getElementById('addDate').value = dateStr;
        document.getElementById('addForm').reset();
        addModal.classList.remove('hidden');
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

        //Send payload
        const response = await fetch('/api/events',{
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(payload)
        });

        //Check response of adding event, if ok - update calendar and hide modal
        if (response.ok){
            const data = await response.json();
            calendar.addEvent({
                id: data.event_id,
                title: payload.event_name,
                start: payload.event_date,
                extendedProps: {
                    timeSlot: payload.event_time,
                    recipe_id: payload.recipe_id
                }
            });
            addModal.classList.add('hidden');
        }
        else{
            alert('Failed to add event.')
        }
    });
    document.getElementById('addCancel').addEventListener('click',() =>{
        addModal.classList.add('hidden');
    });

    /**
     * openViewModal function - used to show calendar event details and option to delete
     * details are shown, eventID is saved for delete, modal is not hidden
     * @param eventObj - event object clicked on in calendar view
     */
    function openViewModal(eventObj){
        document.getElementById('viewTitle').textContent = eventObj.title;
        document.getElementById('viewDate').textContent = eventObj.startStr;
        document.getElementById('viewTime').textContent = eventObj.extendedProps.timeSlot;
        document.getElementById('viewRecipe').textContent = eventObj.extendedProps.recipe_id;

        const deleteButton = document.getElementById('deleteBtn');
        deleteButton.dataset.eventId = eventObj.id;
        viewModal.classList.remove('hidden');
    }

    //Add view modal event listeners for delete and close buttons
    document.getElementById('deleteBtn').addEventListener('click', async (e) =>{
        const eventId = e.target.dataset.eventId;
        if (!eventId){
            return;
        }
        if (!confirm('Delete this event?')){
            return;
        }
        const response = await fetch(`/api/events/${eventId}`,{
            method: 'DELETE'
        });

        if (response.ok){
            const event_delete = calendar.getEventById(eventId);
            if(event_delete){
                event_delete.remove();
            }
            viewModal.classList.add('hidden');
        }
        else{
            alert('Failed to delete event.');
        }

    });
    document.getElementById('viewClose').addEventListener('click', () =>{
        viewModal.classList.add('hidden');
    });

});




#Calendar class object - Jordan
class Calendar(object):

    def __init__(self, calendar_id,user_id):
        """
        Purpose:
            To create a blank calendar linked to a user account, with no entries
        :param calendar_id:  SQL calendar ID
        :param user_id: SQL user ID associated with the calendar
        """
        self.__calendar_id = calendar_id
        self.__user_id = user_id

    def setUserID(self, user_id):
        """
        Purpose:
            To assign a user id to a calendar
        :param user_id: user id to be assigned to calendar
        :return: nothing
        """
        self.__user_id = user_id

    def getUserID(self):
        """
        Purpose:
            To return the user id associated with this calendar
        :return: user id associated with this calendar
        """
        return self.__user_id

#Calendar Event class object - Jordan
class CalendarEvent(object):

    def __init__(self, event_id, event_name, event_date, event_time, recipe_id, calendar_id, recurrence_id):
        """
        Purpose:
            To create a calendar event to be added to a calendar schedule
        :param event_id: SQL event ID
        :param event_name: Event name / recipe name
        :param event_date: Date of the recipe assignment
        :param event_time: Time of the recipe assignment (Breakfast/Lunch/Dinner/Snack)
        :param recipe_id: SQL recipe ID
        :param calendar_id: SQL calendar ID
        :param recurrence_id: SQL recurrence ID
        """
        self.__event_id = event_id
        self.__event_name = event_name
        self.__event_date = event_date
        self.__event_time = event_time
        self.__recipe_id = recipe_id
        self.__calendar_id = calendar_id
        self.__recurrence_id = recurrence_id

    def getEventID(self):
        """
        Purpose:
            To return the event id associated with this CalendarEvent
        :return: event id integer
        """
        return self.__event_id

    def getEventName(self):
        """
        Purpose:
            To return the event/recipe name associated with this CalendarEvent
        :return: event/recipe name String
        """
        return self.__event_name

    def getEventDate(self):
        """
        Purpose:
            To return the event date associated with this CalendarEvent
        :return: event date DateFormat
        """
        return self.__event_date

    def getEventTime(self):
        """
        Purpose:
            To return the event time associated with this CalendarEvent
        :return: event time String
        """
        return self.__event_time

    def getRecipeID(self):
        """
        Purpose:
            To return the recipe ID associated with this CalendarEvent
        :return: recipe ID Integer
        """
        return self.__recipe_id

    def getCalendarID(self):
        """
        Purpose:
            To return the calendar ID associated with this CalendarEvent
        :return: calendar ID Integer
        """
        return self.__calendar_id

    def getRecurrenceID(self):
        """
        Purpose:
            To return the recurrence ID associated with this CalendarEvent
        :return: recurrence ID Integer
        """
        return self.__recurrence_id

#Recurring Event class object - Jordan
class RecurringEvent(object):
    def __init__(self, event_id, calendar_id, recurrence_id, start_date, end_date, frequency):
        """
        Purpose:
            To create a recurring event to be added to a CalendarEvent
        :param event_id: SQL Calendar event ID
        :param calendar_id: SQL Calendar ID
        :param recurrence_id: SQL Recurrence ID
        :param start_date: Start Date of the recurrence
        :param end_date: End Date of the recurrence
        :param frequency: Frequency of the recurrence
        """
        self.__event_id = event_id
        self.__calendar_id = calendar_id
        self.__recurrence_id = recurrence_id
        self.__start_date = start_date
        self.__end_date = end_date
        self.__frequency = frequency

    def getEventID(self):
        """
        Purpose:
            To return the event ID associated with this RecurringEvent
        :return: Event ID Integer
        """
        return self.__event_id

    def getCalendarID(self):
        """
        Purpose:
            To return the calendar ID associated with this RecurringEvent
        :return: Calendar ID Integer
        """
        return self.__calendar_id

    def getRecurrenceID(self):
        """
        Purpose:
            To return the recurrence ID associated with this RecurringEvent
        :return: Recurrence ID Integer
        """
        return self.__recurrence_id

    def getStartDate(self):
        """
        Purpose:
            To return the start date associated with this RecurringEvent
        :return: Start Date DateFormat
        """
        return self.__start_date

    def getEndDate(self):
        """
        Purpose:
            To return the end date associated with this RecurringEvent
        :return: End Date DateFormat
        """
        return self.__end_date

    def getFrequency(self):
        """
        Purpose:
            To return the frequency associated with this RecurringEvent
        :return: frequency String
        """
        return self.__frequency



import unittest
from calendar_class import *


class TestCalendar(unittest.TestCase):
    def test_calendar_constructor(self):
        testCalendar = Calendar(1,2)
        self.assertEqual(testCalendar.getUserID(), 2,"User ID should be 2")
    def test_setUserID(self):
        testCalendar = Calendar(1, 2)
        testCalendar.setUserID(3)
        self.assertEqual(testCalendar.getUserID(),3,"User ID should be 3")

class TestCalendarEvent(unittest.TestCase):
    def test_calendar_event_constructor(self):
        testCalendarEvent = CalendarEvent(1,"Burrito","2025-10-31","Breakfast",45,"1",1)
        self.assertEqual(testCalendarEvent.getEventID(),1,"Event ID should be 1")
        self.assertEqual(testCalendarEvent.getEventDate(),"2025-10-31","Event Date should be 2025-10-31")
        self.assertEqual(testCalendarEvent.getEventTime(),"Breakfast","Event Time should be Breakfast")
        self.assertEqual(testCalendarEvent.getRecipeID(),45,"Recipe ID should be 45")
        self.assertEqual(testCalendarEvent.getRecurrenceID(),1,"Recurrence ID should be 1")

class TestRecurringEvent(unittest.TestCase):
    def test_calendar_event_constructor(self):
        testRecurringEvent = RecurringEvent(1,2,1,"2025-10-01","2025-10-15","weekly")
        self.assertEqual(testRecurringEvent.getCalendarID(),2,"Calendar ID should be 2")
        self.assertEqual(testRecurringEvent.getEventID(),1,"Event ID should be 1")
        self.assertEqual(testRecurringEvent.getRecurrenceID(),1,"Recurrence ID should be 1")
        self.assertEqual(testRecurringEvent.getStartDate(),"2025-10-01","Recurrence Start Date should be 2025-10-01")
        self.assertEqual(testRecurringEvent.getEndDate(),"2025-10-15","Recurrence End Date should be 2025-10-15")
        self.assertEqual(testRecurringEvent.getFrequency(),"weekly","Recurrence Frequency should be weekly")



if __name__ == '__main__':
    unittest.main()

from django.test import TestCase, Client

from .models import User, Recurrence, Day, Class, Homework, Preferences

# Create your tests here.
class HwAppTestCase(TestCase):
    def setUp(self):
        #create user
        user = User.objects.create(username = 'test', password='password', email='test@test.com')
        user2 = User.objects.create(username = 'test2', password='password', email='test2@test.com')

        #initialize days:
        days1 = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
        for day in days1:
            day = Day.objects.create(days=day)

        #create classes
        class_user1 = Class.objects.create(class_user = user, class_name="user1_class1", days=[Monday, Tuesday], period=1, time='01-')
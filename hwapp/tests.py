from django.test import TestCase, Client

from .models import User, Recurrence, Day, Class, Homework, Preferences, Carrier
import datetime

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
        mon = Day.objects.get(days="Monday")
        wed = Day.objects.get(days="Wednesday")
        time = datetime.datetime.now().time()
        #create classes
        class_user1 = Class(class_user = user, class_name="user1_class1", period=1, time=time)

        class_user1_again = Class(class_user = user, class_name="user1_class2", period=7, time=time)
        class_user2 = Class(class_user = user, class_name="user2_class1", period=1, time=time)
        class_user1.save()
        class_user1_again.save()
        class_user2.save()
        for day in [mon, wed]:
            class_user1.days.add(day)
            class_user1_again.days.add(day)
            class_user2.days.add(day)
        class_user1.save()
        class_user1_again.save()
        class_user2.save()
        #create carrier:
        Carrier.objects.create(carrier='T-mobile', email='nothing@testing.com')
        Carrier.objects.create(carrier='test2', email='something@testing.com')

        #create settings:
        settings1 = Preferences.objects.create(preferences_user=user, text_notifications=True, phone_number='2345678910', carrier=Carrier.objects.get(id=1))
        settings2 = Preferences.objects.create(preferences_user=user2, text_notifications=False, phone_number='2345678910', carrier=Carrier.objects.get(id=2))

        #create hw:
        hw_1_1 = Homework.objects.create(hw_user=user, hw_class=class_user1, hw_title='hw1_class1_assoc', due_date=datetime.datetime.now(), priority=7, completed=False)
        hw_1_2 = Homework.objects.create(hw_user=user, hw_class=class_user1, hw_title='hw1_class1_assoc2', due_date=datetime.datetime.now(), priority=7, completed=False)
        hw_1_3 = Homework.objects.create(hw_user=user, hw_class=class_user1, hw_title='hw1_class1_assoc3', due_date=datetime.datetime.now(), priority=7, completed=True)
        hw_1_4 = Homework.objects.create(hw_user=user, hw_class=class_user1_again, hw_title='hw1_class1_assoc', due_date=datetime.datetime.now(), priority=7, completed=True)
        hw_1_1 = Homework.objects.create(hw_user=user, hw_class=class_user1, hw_title='hw1_class1_assoc', due_date=datetime.datetime.now(), priority=7, completed=False)
        hw_1_1 = Homework.objects.create(hw_user=user, hw_class=class_user1, hw_title='hw1_class1_assoc', due_date=datetime.datetime.now(), priority=7, completed=False)
    def test_sign_in(self):
        c = Client()
        response = c.post('/login', {'username': 'test', 'password': 'password'})
        self.assertRedirects(response, '/')
    def test_class_homework_association(self):
        a = Homework.objects.filter(hw_user=User.objects.get(id=1), hw_class=Class.objects.get(id=1), completed=False)
        self.assertEqual(a.count(), 4)    
    def test_filter(self):
        c = Client()
        response = c.get('/?class=1')
        self.assertEqual(response.status, 200)
    def test_filter_access_denied(self):
        c=Client()
        response = c.get('/?class=4')
        self.assertEqual(response.status, 403)
    def test_classes(self):
        c=Client()
        response = c.get('/classes')
        self.assertEqual(response.status, 200)
    def edit_class(self):
        c=Client()
        response = c.get('/editclass/1')
        self.assertEqual(response.status, 200)
    def edit_class_access_denied(self):
        c=Client()
        response = c.get('/editclass/4')
        self.assertEqual(response.status, 403)
    def edit_class_post(self):
        c=Client()
        response = c.post('/editclass/1', {
            'class_name':'edited',
            'period':100,
            'days': 1,
            'days':2,
            'time': datetime.datetime.now()
        })
        self.assertRedirects(response, '/classes')


from django.test import TestCase
from api.models import user_registration
 

class UserRegistrationTestCase(TestCase):
    def test_example(self):
        expected = 'Admin'
        user = user_registration.objects.get(id=1)
        actual = user.name
        self.assertEqual(expected, actual, msg="The actual value should be equal to 'Admin'.")

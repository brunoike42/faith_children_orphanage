from django.test import TestCase
from django.urls import reverse

from volunteers.models import Child, VolunteerOpportunity
from volunteers.views import seed_default_content


class VolunteerContentTests(TestCase):
    def test_seed_default_content_creates_demo_children_and_opportunities(self):
        Child.objects.all().delete()
        VolunteerOpportunity.objects.all().delete()

        seed_default_content()

        self.assertTrue(Child.objects.exists())
        self.assertTrue(VolunteerOpportunity.objects.exists())

    def test_child_page_renders_demo_children(self):
        Child.objects.all().delete()
        seed_default_content()

        response = self.client.get(reverse('child_list'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Our Children')
        self.assertContains(response, 'Amina')

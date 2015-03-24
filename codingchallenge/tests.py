import requests

from django.test import TestCase
from django.core.urlresolvers import reverse

from codingchallenge.models import Category
from codingchallenge.credentials import *


def create_category(resource_uri, id, name, name_localized, short_name, short_name_localized):
    """Helper to enter a category into the test database"""
    return Category.objects.create(resource_uri=resource_uri,
                                   id=id,
                                   name=name,
                                   name_localized=name_localized,
                                   short_name=short_name,
                                   short_name_localized=short_name_localized)


def three_categories():
    """Helper to enter three categories (101, 102, and 103) into the test database"""
    create_category(resource_uri="https://www.eventbriteapi.com/v3/categories/101/",
                    id=101,
                    name="Business & Professional",
                    name_localized="Business & Professional",
                    short_name="Business",
                    short_name_localized="Business")
    create_category(resource_uri="https://www.eventbriteapi.com/v3/categories/102/",
                    id=102,
                    name="Science & Technology",
                    name_localized="Science & Technology",
                    short_name="Science & Tech",
                    short_name_localized="Science & Tech")
    create_category(resource_uri="https://www.eventbriteapi.com/v3/categories/103/",
                    id=103,
                    name="Music",
                    name_localized="Music",
                    short_name="Music",
                    short_name_localized="Music")


# Create your tests here.
class IndexTests(TestCase):
    def test_all_categories_shown(self):
        """All the categories in the database should be shown"""
        # Create a category and make sure it's shown on the page
        create_category(resource_uri="https://www.eventbriteapi.com/v3/categories/101/",
                        id=101,
                        name="Business & Professional",
                        name_localized="Business & Professional",
                        short_name="Business",
                        short_name_localized="Business")
        response = self.client.get(reverse("codingchallenge:index"))
        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(response.context["categories"], ["<Category: Business & Professional>"])

        # Create another category and test again for good measure
        create_category(resource_uri="https://www.eventbriteapi.com/v3/categories/102/",
                        id=102,
                        name="Science & Technology",
                        name_localized="Science & Technology",
                        short_name="Science & Tech",
                        short_name_localized="Science & Tech")
        response = self.client.get(reverse("codingchallenge:index"))
        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(response.context["categories"].order_by("id"), ["<Category: Business & Professional>",
                                                                                 "<Category: Science & Technology>"])


class ChooseTests(TestCase):
    def test_invalid_category_chosen(self):
        """If the user manipulates the url to request an invalid category, the user should be scolded"""
        three_categories()
        response = self.client.get("/codingchallenge/choose/?category=101&category=102&category=100")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Screw you, your sneaky tricks will not work on me")

    def test_no_categories_chosen(self):
        """If no categories are chosen, the index page is returned with the appropriate warning"""
        three_categories()
        response = self.client.get("/codingchallenge/choose/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Please select exactly 3 categories")

    def test_too_few_categories_chosen(self):
        """If too few categories are chosen, the index page is returned with the appropriate warning"""
        three_categories()
        response = self.client.get("/codingchallenge/choose/?category=101")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Please select exactly 3 categories")

    def test_too_many_categories_chosen(self):
        """If too many categories are chosen, the index page is returned with the appropriate warning"""
        three_categories()
        create_category(resource_uri="https://www.eventbriteapi.com/v3/categories/104/",
                        id=104,
                        name="Film, Media & Entertainment",
                        name_localized="Film, Media & Entertainment",
                        short_name="Film & Media",
                        short_name_localized="Film & Media")
        response = self.client.get("/codingchallenge/choose/?category=101&category=102&category=103&category=104")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Please select exactly 3 categories")

    def test_correct_number_categories_chosen(self):
        """If three categories are chosen, a HttpResponseRedirect should be returned"""
        three_categories()
        response = self.client.get("/codingchallenge/choose/?category=101&category=102&category=103")
        self.assertEqual(response.status_code, 302)  # status code for redirect


class ResultsTests(TestCase):
    def test_links_first_page(self):
        """The links on the results pages should exist. We test the first page, last page, and a middle page"""
        three_categories()
        r = requests.get("https://www.eventbriteapi.com/v3/events/search/?token=%s&categories=%s,%s,%s&page=%s" %
                         (TOKEN, 101, 102, 103, 1))
        last_page = r.json()["pagination"]["page_count"]

        # First page
        response = self.client.get(reverse("codingchallenge:results", args=(101, 102, 103, 1)))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "First Page")
        self.assertNotContains(response, "Previous Page")
        if last_page == 1:
            self.assertNotContains(response, "Next Page")
        else:
            self.assertContains(response, "Next Page")
        self.assertContains(response, "Last Page")
        self.assertContains(response, "Choose Again")

        # Last page
        response = self.client.get(reverse("codingchallenge:results", args=(101, 102, 103, last_page)))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "First Page")
        if last_page == 1:
            self.assertNotContains(response, "Previous Page")
        else:
            self.assertContains(response, "Previous Page")
        self.assertNotContains(response, "Next Page")
        self.assertContains(response, "Last Page")
        self.assertContains(response, "Choose Again")

        # Middle page
        if last_page != 1:
            response = self.client.get(reverse("codingchallenge:results", args=(101, 102, 103, 2)))
            self.assertEqual(response.status_code, 200)
            self.assertContains(response, "First Page")
            self.assertContains(response, "Previous Page")
            if last_page == 2:
                self.assertNotContains(response, "Next Page")
            else:
                self.assertContains(response, "Next Page")
            self.assertContains(response, "Last Page")
            self.assertContains(response, "Choose Again")

    def test_list_index(self):
        """The ordered list start index on the results page should be correct"""
        three_categories()
        r = requests.get("https://www.eventbriteapi.com/v3/events/search/?token=%s&categories=%s,%s,%s&page=%s" %
                         (TOKEN, 101, 102, 103, 1))
        page_size = r.json()["pagination"]["page_size"]

        # Test first page
        response = self.client.get(reverse("codingchallenge:results", args=(101, 102, 103, 1)))
        self.assertContains(response, "start=\"%i\"" % 1)

        # Test second page, if it exists
        response = self.client.get(reverse("codingchallenge:results", args=(101, 102, 103, 2)))
        self.assertContains(response, "start=\"%i\"" % (1 + int(page_size)))

    def test_result_has_correct_category(self):
        """The events on the result page should be of the correct category"""
        response = self.client.get(reverse("codingchallenge:results", args=(101, 102, 103, 1)))
        self.assertEqual(response.context["category_id_1"], "101")
        self.assertEqual(response.context["category_id_2"], "102")
        self.assertEqual(response.context["category_id_3"], "103")
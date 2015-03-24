import requests

from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse

from codingchallenge.models import Category
from codingchallenge.credentials import *


# Create your views here.
def index(request):
    categories = Category.objects.all()
    return render(request, "codingchallenge/index.html", {"categories": categories})


def choose(request):
    try:
        selected = request.GET.copy().pop('category')  # the GET request is immutable, so we must copy it to pop it
        if len(selected) != 3:
            raise KeyError

        # This is to catch users who try to manipulate the url to request a category that doesn't exist
        valid_categories = [str(category.id) for category in Category.objects.all()]
        for category in selected:
            if category not in valid_categories:
                raise NameError
    except KeyError:
        return render(request, "codingchallenge/index.html", {
            "error_message": "Please select exactly 3 categories",
            "categories": Category.objects.all(),
        })
    except NameError:
        return HttpResponse("Screw you, your sneaky tricks will not work on me")
    else:
        return HttpResponseRedirect(reverse("codingchallenge:results", args=(selected[0], selected[1], selected[2], 1)))


def results(request, category_id_1, category_id_2, category_id_3, page):
    r = requests.get("https://www.eventbriteapi.com/v3/events/search/?token=%s&categories=%s,%s,%s&page=%s" %
                     (TOKEN, category_id_1, category_id_2, category_id_3, page))
    events = r.json()["events"]
    page_info = r.json()["pagination"]
    context = {"category_id_1": category_id_1,
               "category_id_2": category_id_2,
               "category_id_3": category_id_3,
               "page_info": page_info,
               "events": events}
    return render(request, "codingchallenge/results.html", context)
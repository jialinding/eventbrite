from django import template

def add_one(value):
    return int(value)+1

def sub_one(value):
    return int(value)-1

def start_index(page):
    """Return the start index for the ordered list for a page of results"""
    return ((page["page_number"]-1) * page["page_size"]) + 1

register = template.Library()
register.filter('add_one', add_one)
register.filter('sub_one', sub_one)
register.filter('start_index', start_index)

from django import template

register = template.Library()

@register.filter
def range_filter(value):
    """
    Returns a range object from the given value.
    This is used to generate a range in Django templates.
    """
    try:
        return range(value)
    except TypeError:
        return range(0)  # Return an empty range if the value is invalid

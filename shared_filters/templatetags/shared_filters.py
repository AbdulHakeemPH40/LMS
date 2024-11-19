# shared_filters/templatetags/shared_filters.py
from urllib.parse import urlparse, parse_qs
from django import template

register = template.Library()

@register.filter(name='replace')
def replace(value, args):
    """
    Replaces occurrences of a substring within the value.
    Usage: {{ value|replace:"old,new" }}
    """
    try:
        old, new = args.split(',')
        return value.replace(old, new)
    except ValueError:
        return value

register = template.Library()

@register.filter(name='youtube_embed')
def youtube_embed(value):
    """
    Converts a YouTube URL into its embed format.
    Usage: {{ video_url|youtube_embed }}
    """
    if 'youtu.be' in value:
        video_id = value.split('/')[-1]
        return f'https://www.youtube.com/embed/{video_id}'
    elif 'youtube.com' in value:
        query = urlparse(value).query
        video_id = parse_qs(query).get('v')
        if video_id:
            return f'https://www.youtube.com/embed/{video_id[0]}'
    return value

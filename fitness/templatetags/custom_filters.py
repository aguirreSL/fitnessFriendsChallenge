from django import template

register = template.Library()

@register.filter(name='add_class')
def add_class(value, arg):
    return value.as_widget(attrs={'class': arg})

@register.filter
def stars(value):
    try:
        value = float(value)
        full_stars = int(value)
        half_star = value - full_stars >= 0.5
        stars = '⭐' * full_stars
        if half_star:
            stars += '⭐'
        return stars
    except (ValueError, TypeError):
        return ''
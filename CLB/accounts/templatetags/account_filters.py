from django import template

register = template.Library()

@register.filter(name='isinstance')
def is_instance(obj, type_name):
    """
    Check if an object is an instance of a given type.
    Usage: {% if user|isinstance:"accounts.Customer" %}
    """
    if not obj:
        return False
    
    # Get the class name of the object
    obj_class_name = obj.__class__.__name__
    
    # Check if the object is an instance of the given type
    return obj_class_name == type_name.split('.')[-1] 

@register.filter(name='multiply')
def multiply(value, arg):
    """
    Multiply the value by the argument.
    Usage: {{ value|multiply:arg }}
    """
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return 0 
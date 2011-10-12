from django.template import Library
register = Library()

@register.filter(name='mult')
def mult(value, arg):
    "Multiplies the arg and the value"
    return int(value) * int(arg)
mult.is_safe = False

@register.filter(name='sub')
def sub(value, arg):
    "Subtracts the arg from the value"
    return int(value) - int(arg)
sub.is_safe = False

@register.filter(name='div')
def div(value, arg):
    "Divides the value by the arg"
    return "%.2f" % (float(value) / float(arg))
div.is_safe = False

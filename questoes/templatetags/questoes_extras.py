from django import template

register = template.Library()

@register.filter
def zip_lists(a, b):
    return zip(a, b)

@register.filter
def get_alternativas(questao_me):
    """Retorna uma lista com as alternativas da questão"""
    return [
        questao_me.alternativa_a,
        questao_me.alternativa_b,
        questao_me.alternativa_c,
        questao_me.alternativa_d,
        questao_me.alternativa_e,
    ]

@register.filter(name='get_item')
def get_item(dictionary, key):
    if dictionary is None:
        return None
    return dictionary.get(str(key))

@register.filter(name='calculate_progress')
def calculate_progress(current, total):
    try:
        return (float(current) / float(total)) * 100
    except (ValueError, ZeroDivisionError):
        return 0
    

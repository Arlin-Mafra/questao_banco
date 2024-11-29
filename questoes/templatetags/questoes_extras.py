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

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)

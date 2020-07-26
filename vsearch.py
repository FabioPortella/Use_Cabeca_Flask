def procura_vogais(frase: str) -> set:
    """Retorna vogais em uma frase."""
    vogais = set('aeiou')
    return vogais.intersection(set(frase))


def procura_letras(frase: str, letras: str='aeiou') -> set:
    """Retorna um conjunto de 'letras' encontradas em uma frase"""
    return set(letras).intersection(set(frase))

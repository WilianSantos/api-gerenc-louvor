import html
import re

from pychord import Chord


def is_chord(value):
    """
    Verifica se um valor representa um acorde válido, incluindo acordes com extensões entre parênteses.
    """
    # Remove parênteses e qualquer conteúdo dentro deles
    clean_value = re.sub(r"\([^)]*\)", "", value).strip()

    try:
        Chord(clean_value)
        return True
    except ValueError:
        return False


def strip_html_tags(text):
    """
    Remove tags HTML do texto fornecido.
    """
    return re.sub(r"<[^>]+>", "", text)


def extract_lyrics_without_chords(raw_html):
    """
    Extrai letras da música, removendo acordes (incluindo acordes com extensões) e restaurando quebras de linha.
    """
    # Remove tags HTML e decodifica entidades HTML
    text = html.unescape(strip_html_tags(raw_html))

    # Insere quebras de linha ao redor de marcadores de seção
    text = re.sub(r"(\[[^\]]+\])", r"\n\1\n", text)

    # Remove múltiplos espaços e colapsa linhas
    lines = []
    for line in text.splitlines():
        # Divide a linha em palavras, considerando tanto acordes simples quanto com parênteses
        words = line.strip().split()

        # Filtra palavras que não são acordes
        line_clean = " ".join(word for word in words if not is_chord(word))

        if line_clean:
            lines.append(line_clean.strip())

    return "\n".join(lines)

import re
import textwrap

class TextProcessor:
    # Expressions régulières compilées pour une performance maximale (C-level)
    NOISE = re.compile(r'^(page)?\s*\d+\s*(/\s*\d+|of\s*\d+)?$', re.I)
    HYPHEN = re.compile(r'(\w+)-\s*\n+\s*(\w+)')
    CHARS = re.compile(r'[#\*(\)&%@\?"\.<>/\}\{\+_\-\\\|\^\$!~]')
    SPACE = re.compile(r'\s+')

    @classmethod
    def process_and_segment(cls, text, chunk_size=2500):
        """Nettoie le texte en un seul passage optimisé et le segmente intelligemment."""
        # 1. Filtre les numéros de page et en-têtes
        lines = [l for l in text.split('\n') if not cls.NOISE.match(l.strip())]
        # 2. Reconstruit les mots coupés (césures)
        text = cls.HYPHEN.sub(r'\1\2', '\n'.join(lines))
        # 3. Supprime les caractères spéciaux et normalise les espaces
        text = cls.SPACE.sub(' ', cls.CHARS.sub(' ', text)).strip()
        # 4. Segmente sans couper les mots via textwrap (ultra-rapide)
        return textwrap.wrap(text, width=chunk_size, break_long_words=False)

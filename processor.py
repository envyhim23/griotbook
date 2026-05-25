import re

class TextProcessor:
    @staticmethod
    def remove_layout_noise(text):
        """Supprime les en-têtes, pieds de page et numéros de page isolés."""
        lines = text.split("\n")
        cleaned_lines = []
        for line in lines:
            stripped = line.strip()
            # Ignorer les numéros de page simples (ex: "1", "Page 12", "12 / 100", "Page 12 of 30")
            if re.match(r'^(page)?\s*\d+\s*(/\s*\d+|of\s*\d+)?$', stripped, re.IGNORECASE):
                continue
            cleaned_lines.append(line)
        return "\n".join(cleaned_lines)

    @staticmethod
    def reconstruct_paragraphs(text):
        """Réassemble les lignes brisées et gère les césures (mots coupés par un tiret)."""
        # Supprimer le bruit de mise en page d'abord
        text = TextProcessor.remove_layout_noise(text)
        
        # Gérer les césures : mot coupé en fin de ligne (ex: "informa-\ntion" -> "information")
        # On cherche un tiret suivi d'un ou plusieurs retours à la ligne et d'éventuels espaces
        text = re.sub(r'(\w+)-\s*\n+\s*(\w+)', r'\1\2', text)
        
        # Séparer d'abord par double retour à la ligne pour isoler les paragraphes structurels
        paragraphs = re.split(r'\n\s*\n', text)
        reconstructed_paragraphs = []
        
        for p in paragraphs:
            # Remplacer tous les sauts de ligne simples à l'intérieur d'un paragraphe par des espaces
            clean_p = re.sub(r'\s*\n\s*', ' ', p)
            # Nettoyer les espaces doubles
            clean_p = re.sub(r'\s+', ' ', clean_p).strip()
            if clean_p:
                reconstructed_paragraphs.append(clean_p)
                
        return reconstructed_paragraphs

    @staticmethod
    def clean_special_characters(text):
        """Supprime les caractères spéciaux spécifiés par l'utilisateur par regex."""
        # Liste des caractères à supprimer :
        # #, *, (, ), &, %, @, ?, ", ., >, <, /, }, {, +, _, -, \, |, ^, $, !, ~
        # Remplacement de ces caractères par un espace pour éviter de coller les mots adjacents
        chars_to_remove = r'[#\*(\)&%@\?"\.<>/\}\{\+_\-\\\|\^\$!~]'
        cleaned = re.sub(chars_to_remove, ' ', text)
        # Supprimer les espaces multiples
        cleaned = re.sub(r'\s+', ' ', cleaned)
        return cleaned.strip()

    @staticmethod
    def process_and_segment(text, chunk_size=2000):
        """
        Prend le texte brut, le reconstruit en paragraphes,
        nettoie les caractères spéciaux, et le segmente en blocs optimisés pour la synthèse.
        """
        # 1. Reconstruire les paragraphes propres
        paragraphs = TextProcessor.reconstruct_paragraphs(text)
        
        # 2. Nettoyer les caractères spéciaux pour chaque paragraphe
        cleaned_paragraphs = [TextProcessor.clean_special_characters(p) for p in paragraphs]
        cleaned_paragraphs = [p for p in cleaned_paragraphs if p]  # Enlever les paragraphes vides
        
        # 3. Regrouper les paragraphes en blocs (chunks) ne dépassant pas chunk_size caractères
        chunks = []
        current_chunk = []
        current_len = 0
        
        for p in cleaned_paragraphs:
            # Si le paragraphe seul est plus grand que la taille max, on le coupe
            if len(p) > chunk_size:
                if current_chunk:
                    chunks.append(" ".join(current_chunk))
                    current_chunk = []
                    current_len = 0
                
                # Coupe le paragraphe long par mots
                words = p.split(" ")
                temp_chunk = []
                temp_len = 0
                for w in words:
                    if temp_len + len(w) + 1 > chunk_size:
                        if temp_chunk:
                            chunks.append(" ".join(temp_chunk))
                        temp_chunk = [w]
                        temp_len = len(w)
                    else:
                        temp_chunk.append(w)
                        temp_len += len(w) + 1
                if temp_chunk:
                    chunks.append(" ".join(temp_chunk))
            else:
                if current_len + len(p) + 1 > chunk_size:
                    chunks.append(" ".join(current_chunk))
                    current_chunk = [p]
                    current_len = len(p)
                else:
                    current_chunk.append(p)
                    current_len += len(p) + 1
                    
        if current_chunk:
            chunks.append(" ".join(current_chunk))
            
        return chunks

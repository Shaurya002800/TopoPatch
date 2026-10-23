"""Deterministic offline embeddings. These are lexical models, not pretrained neural models."""
import hashlib
import math
import re

SYNONYMS = {'automobile':'car', 'vehicle':'car', 'physician':'doctor', 'medic':'doctor',
            'purchase':'buy', 'acquire':'buy', 'canine':'dog', 'puppy':'dog',
            'feline':'cat', 'kitten':'cat', 'repair':'fix', 'mend':'fix',
            'secure':'safe', 'security':'safe', 'credentials':'password', 'credential':'password'}

class LexicalEncoder:
    def __init__(self, target=False):
        self.target = target
        self.dimension = 256 if target else 128
        self.identity = f'lexical-sha256-{self.dimension}-synonyms-v1' if target else 'lexical-sha256-128-v1'

    def encode(self, text):
        tokens = re.findall(r'[a-z0-9]+', text.lower())
        if self.target:
            tokens = [SYNONYMS.get(t, t) for t in tokens]
        vector = [0.0] * self.dimension
        for token in tokens:
            raw = hashlib.sha256(token.encode()).digest()
            vector[int.from_bytes(raw[:4], 'big') % self.dimension] += 1 if raw[4] % 2 else -1
        norm = math.sqrt(sum(v*v for v in vector))
        return [v/norm for v in vector] if norm else vector

def similarity(a, b):
    if len(a) != len(b):
        raise ValueError('Cannot compare different embedding spaces')
    return sum(x*y for x,y in zip(a,b))

class SentenceEncoder:
    """Optional adapter for a local, immutable Sentence Transformers snapshot."""
    def __init__(self, snapshot):
        from pathlib import Path
        from sentence_transformers import SentenceTransformer
        path=Path(snapshot).resolve()
        if not path.is_dir(): raise ValueError('Supply an existing local model snapshot')
        self.model=SentenceTransformer(str(path),device='cpu')
        self.dimension=self.model.get_sentence_embedding_dimension()
        self.identity=f'sentence-transformers:{path.name}:{self.dimension}'

    def encode(self,text):
        return self.model.encode(text,normalize_embeddings=True,show_progress_bar=False).tolist()

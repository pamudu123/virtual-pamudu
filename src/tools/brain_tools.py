import os
import yaml
import re
from collections import Counter

# --- CONFIGURATION ---
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
BRAIN_ROOT = os.path.join(BASE_DIR, "digital_brain")

# --- HELPERS ---
def _load_shortcuts():
    path = os.path.join(BRAIN_ROOT, "shortcuts.yaml")
    if not os.path.exists(path): return {}
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f) or {}
    except: return {}

def _read_file_safe(rel_path):
    full_path = os.path.normpath(os.path.join(BRAIN_ROOT, rel_path))
    if not full_path.startswith(BRAIN_ROOT) or not os.path.exists(full_path):
        return None
    try:
        with open(full_path, 'r', encoding='utf-8') as f:
            return f.read()
    except: return None

def _preprocess_text(text):
    if not text: return []
    text = text.lower()
    text = re.sub(r'[^a-z0-9\s]', ' ', text)
    return text.split()

# --- THE ENGINE ---

def fetch_brain_context(shortcut_keys: list, search_keywords: list, top_n: int = 3, threshold: int = 2):
    """
    Retrieves knowledge with Threshold Filtering.
    
    Args:
        threshold (int): Minimum score required to be considered a match. 
                         Default is 2 (must match at least 2 keywords).
    """
    results = []
    
    # PHASE 1: SHORTCUTS
    shortcuts_map = _load_shortcuts()
    for key in shortcut_keys:
        clean_key = key.lower().strip()
        if clean_key in shortcuts_map:
            content = _read_file_safe(shortcuts_map[clean_key])
            if content: 
                results.append({"type": "shortcut", 
                                "key": clean_key, 
                                "source_path": shortcuts_map[clean_key],
                                "content": content})

    # PHASE 2: SEARCH SCORING
    if search_keywords:
        file_scores = {}
        
        # Preprocess Query
        raw_query = " ".join(search_keywords)
        clean_query_tokens = _preprocess_text(raw_query)
        
        if clean_query_tokens:
            for root, _, files in os.walk(BRAIN_ROOT):
                for file in files:
                    if file.endswith(".md") and file != "shortcuts.yaml":
                        full_path = os.path.join(root, file)
                        rel_path = os.path.relpath(full_path, BRAIN_ROOT)
                        
                        content = _read_file_safe(rel_path)
                        if not content: continue
                        
                        # Score File
                        file_tokens = _preprocess_text(content)
                        file_token_counts = Counter(file_tokens)
                        
                        score = 0
                        for token in clean_query_tokens:
                            score += file_token_counts[token]
                        
                        # --- THE THRESHOLD CHECK ---
                        # Only keep if score meets the minimum requirement
                        if score >= threshold:
                            file_scores[rel_path] = score

            # Sort best matches first
            sorted_files = sorted(file_scores.items(), key=lambda item: item[1], reverse=True)
            
            for rel_path, score in sorted_files[:top_n]:
                content = _read_file_safe(rel_path)
                results.append({"type": "search", 
                                "key": rel_path, 
                                "score": score,
                                "source_path": rel_path,
                                "content": content})

    return results


if __name__ == "__main__":
    print(f"BRAIN_ROOT: {BRAIN_ROOT}")
    if not os.path.isdir(BRAIN_ROOT):
        print("digital_brain folder not found; smoke tests skipped.")
        raise SystemExit(0)

    shortcuts_map = _load_shortcuts()
    available_shortcuts = sorted(list((shortcuts_map or {}).keys()))

    # Scenario 1: Empty inputs
    res = fetch_brain_context(shortcut_keys=[], search_keywords=[], top_n=3)
    print(res)

    # Scenario 2: Shortcuts-only (use first 1-2 keys if present)
    shortcut_sample = available_shortcuts[:2]
    res = fetch_brain_context(shortcut_keys=shortcut_sample, search_keywords=[], top_n=3)
    print(res)

    # Scenario 3: Search-only
    res = fetch_brain_context(shortcut_keys=[], search_keywords=["resume", "skills"], top_n=3)
    print(res)

    # Scenario 4: Combined shortcuts + search
    res = fetch_brain_context(shortcut_keys=shortcut_sample, search_keywords=["projects", "experience"], top_n=3)
    print(res)


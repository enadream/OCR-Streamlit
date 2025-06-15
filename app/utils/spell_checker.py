import spacy
import contextualSpellCheck

# Cache for loaded spaCy models to avoid reloading
SPACY_MODELS = {}

def get_spacy_model(language_code: str = 'en'):
    """
    Loads and returns a spaCy model for a given language, caching it for future use.
    """
    # Maps simple language codes to spaCy's model names
    model_map = {
        'en': 'en_core_web_sm',
        'tr': 'tr_core_news_trf',
        'de': 'de_core_news_sm',
        'fr': 'fr_core_news_sm',
        'es': 'es_core_news_sm',
    }

    model_name = model_map.get(language_code)
    if not model_name:
        print(f"[WARNING]: No spaCy model mapping found for language '{language_code}'. Defaulting to English.")
        model_name = 'en_core_web_sm'
        language_code = 'en'

    if language_code in SPACY_MODELS:
        return SPACY_MODELS[language_code]

    try:
        print(f"[INFO]: Loading spaCy model '{model_name}' for language '{language_code}'...")
        nlp = spacy.load(model_name)
        contextualSpellCheck.add_to_pipe(nlp)
        SPACY_MODELS[language_code] = nlp
        print(f"[INFO]: Model '{model_name}' loaded successfully.")
        return nlp
    except OSError:
        print(f"[ERROR]: SpaCy model '{model_name}' not found.")
        print(f"[ERROR]: Please install it by running: python -m spacy download {model_name}")
        # Cache the failure to avoid retrying
        SPACY_MODELS[language_code] = None
        return None

def correct_text_with_spacy(text: str, language: str = 'en') -> str:
    """Corrects spelling in a text string using a language-specific spaCy model."""
    if not text:
        return ""

    nlp = get_spacy_model(language)
    if not nlp:
        # If the model failed to load, return the original text
        return text

    doc = nlp(text)
    return doc.text
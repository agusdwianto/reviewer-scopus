import importlib
import os
import pytest


def test_no_hardcoded_gemini_key(monkeypatch):
    # Ensure GEMINI_API_KEY is not set in the environment
    monkeypatch.delenv('GEMINI_API_KEY', raising=False)
    # Reload module to pick up environment changes
    import review
    importlib.reload(review)
    # The module-level GEMINI_API_KEY should be None (no hard-coded secret)
    assert review.GEMINI_API_KEY is None


def test_get_api_key_prefers_runtime(monkeypatch):
    # Clear env and set runtime session key
    monkeypatch.delenv('GEMINI_API_KEY', raising=False)
    import review
    importlib.reload(review)
    # set runtime key in session_state (simulate admin set)
    review.st.session_state['runtime_gemini_key'] = 'runtime-test-key'
    assert review.get_api_key() == 'runtime-test-key'
    # cleanup
    review.st.session_state.pop('runtime_gemini_key', None)

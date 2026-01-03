import pytest
import builtins

from utils import generate_pdf_report


def test_generate_pdf_requires_pdf_engine_when_missing(monkeypatch):
    """If neither reportlab nor fpdf are present, error should indicate installation guidance."""
    orig_import = builtins.__import__

    def fake_import(name, globals=None, locals=None, fromlist=(), level=0):
        if name in ('reportlab', 'fpdf'):
            raise ImportError(f"No module named '{name}'")
        return orig_import(name, globals, locals, fromlist, level)

    monkeypatch.setattr(builtins, '__import__', fake_import)
    with pytest.raises(RuntimeError, match="reportlab|fpdf"):
        generate_pdf_report("some content")


def test_generate_pdf_returns_bytes_with_reportlab():
    pytest.importorskip('reportlab')
    pdf_bytes = generate_pdf_report("hello world", user_name="Dr. Test", scores={'Total':100,'Originality':20})
    assert isinstance(pdf_bytes, (bytes, bytearray))
    assert len(pdf_bytes) > 0


def test_generate_pdf_returns_bytes_with_fpdf_fallback(monkeypatch):
    # If reportlab is missing but fpdf is present, function should still work
    try:
        pytest.importorskip('fpdf')
    except pytest.skip.Exception:
        pytest.skip("fpdf not installed, and reportlab not available in this test environment")

    orig_import = builtins.__import__

    def fake_import(name, globals=None, locals=None, fromlist=(), level=0):
        if name == 'reportlab':
            raise ImportError("No module named 'reportlab'")
        return orig_import(name, globals, locals, fromlist, level)

    monkeypatch.setattr(builtins, '__import__', fake_import)
    pdf_bytes = generate_pdf_report("hello world (fallback)", user_name="Dr. Test", scores={'Total':100,'Originality':20})
    assert isinstance(pdf_bytes, (bytes, bytearray))
    assert len(pdf_bytes) > 0

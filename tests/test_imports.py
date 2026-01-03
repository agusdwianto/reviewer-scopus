import pytest


def test_fpdf_import():
    pytest.importorskip('fpdf')
    from fpdf import FPDF
    assert FPDF is not None

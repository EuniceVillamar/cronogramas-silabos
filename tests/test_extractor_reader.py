from extractor.reader import leer_pdf


def test_leer_pdf_devuelve_texto_por_pagina(pdf_simple):
    documento = leer_pdf(pdf_simple)

    assert len(documento.paginas) == 1
    assert documento.paginas[0].numero == 1
    assert "Examen parcial 15 de marzo" in documento.texto

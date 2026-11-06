import pytest


def _pdf_con_texto(texto: str) -> bytes:
    """Arma un PDF mínimo con una línea de texto, sin depender de otra librería."""
    contenido = f"BT /F1 12 Tf 72 720 Td ({texto}) Tj ET".encode("latin-1")
    objetos = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R "
        b"/Resources << /Font << /F1 5 0 R >> >> >>",
        b"<< /Length %d >>\nstream\n%s\nendstream" % (len(contenido), contenido),
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
    ]
    pdf = bytearray(b"%PDF-1.4\n")
    posiciones = []
    for numero, cuerpo in enumerate(objetos, start=1):
        posiciones.append(len(pdf))
        pdf += b"%d 0 obj\n%s\nendobj\n" % (numero, cuerpo)
    inicio_xref = len(pdf)
    pdf += b"xref\n0 %d\n0000000000 65535 f \n" % (len(objetos) + 1)
    for posicion in posiciones:
        pdf += b"%010d 00000 n \n" % posicion
    pdf += b"trailer\n<< /Size %d /Root 1 0 R >>\n" % (len(objetos) + 1)
    pdf += b"startxref\n%d\n%%%%EOF\n" % inicio_xref
    return bytes(pdf)


@pytest.fixture
def pdf_simple(tmp_path):
    ruta = tmp_path / "silabo.pdf"
    ruta.write_bytes(_pdf_con_texto("Examen parcial 15 de marzo"))
    return ruta

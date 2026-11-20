from django import forms
from django.core.validators import FileExtensionValidator

TAMANO_MAXIMO = 10 * 1024 * 1024


def validar_pdf(archivo) -> None:
    if archivo.size > TAMANO_MAXIMO:
        raise forms.ValidationError(f"{archivo.name} pesa más de 10 MB.")
    inicio = archivo.read(5)
    archivo.seek(0)
    if inicio != b"%PDF-":
        raise forms.ValidationError(f"{archivo.name} no es un PDF válido.")


class VariosArchivosInput(forms.ClearableFileInput):
    allow_multiple_selected = True


class VariosPdfField(forms.FileField):
    widget = VariosArchivosInput

    def clean(self, data, initial=None):
        limpiar_uno = super().clean
        if isinstance(data, list | tuple):
            return [limpiar_uno(archivo, initial) for archivo in data]
        return [limpiar_uno(data, initial)] if data else []


class GenerarCalendarioForm(forms.Form):
    calendario = forms.FileField(
        label="Calendario académico (PDF)",
        validators=[FileExtensionValidator(["pdf"]), validar_pdf],
        help_text="El calendario oficial del periodo, por ejemplo CII 2026-2027.",
    )
    silabos = VariosPdfField(
        label="Sílabos (PDF)",
        required=False,
        validators=[FileExtensionValidator(["pdf"]), validar_pdf],
        help_text="Puedes elegir varios. Sin sílabos se generan solo las fechas de la universidad.",
    )
    dias_repaso = forms.IntegerField(
        label="Días de anticipación para repasar",
        min_value=1,
        max_value=21,
        initial=7,
    )

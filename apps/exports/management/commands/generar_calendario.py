from pathlib import Path

from django.core.management.base import BaseCommand, CommandError

from apps.exports.services import ArchivoIlegible, generar_planificacion


class Command(BaseCommand):
    help = "Genera un .ics a partir del calendario académico y, opcionalmente, de sílabos en PDF."

    def add_arguments(self, parser):
        parser.add_argument("calendario", type=Path, help="PDF del calendario académico.")
        parser.add_argument("silabos", nargs="*", type=Path, help="PDF de los sílabos.")
        parser.add_argument("--salida", type=Path, default=Path("calendario.ics"))
        parser.add_argument("--dias-repaso", type=int, default=7)

    def handle(self, *args, **opciones):
        rutas = [opciones["calendario"], *opciones["silabos"]]
        faltantes = [str(ruta) for ruta in rutas if not ruta.is_file()]
        if faltantes:
            raise CommandError(f"No existen: {', '.join(faltantes)}")
        try:
            plan, contenido = generar_planificacion(
                opciones["calendario"], opciones["silabos"], opciones["dias_repaso"]
            )
        except ArchivoIlegible as error:
            raise CommandError(str(error)) from error

        opciones["salida"].write_bytes(contenido)
        self.stdout.write(f"Periodo: {plan.periodo}")
        self.stdout.write(f"Eventos: {len(plan.eventos)}")
        for evento in plan.omitidos:
            self.stdout.write(
                self.style.WARNING(f"Omitido: {evento.texto_fecha}. {evento.advertencia}")
            )
        for aviso in plan.advertencias:
            self.stdout.write(self.style.WARNING(aviso))
        self.stdout.write(self.style.SUCCESS(f"Calendario guardado en {opciones['salida']}"))

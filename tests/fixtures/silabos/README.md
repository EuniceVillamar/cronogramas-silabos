# Muestra de sílabos

Cada sílabo se guarda como un par de archivos con el mismo nombre:

- `nombre.pdf`: el sílabo, sin nombres ni correos de docentes.
- `nombre.expected.json`: lo que debería extraerse, etiquetado a mano.

```json
{
  "formato": "tabla",
  "periodo": {"inicio": "2027-03-01", "fin": "2027-07-01"},
  "actividades": [
    {"titulo": "Examen parcial", "tipo": "examen", "fecha": "2027-04-15", "ponderacion": 30}
  ]
}
```

Separen de 3 a 5 sílabos que no se usen para ajustar las reglas. Con ellos se mide la precisión final.

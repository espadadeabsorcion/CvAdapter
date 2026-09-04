# -*- coding: utf-8 -*-
from django.db import migrations


def migrate_niveles_cefr(apps, schema_editor):
    """Convierte los niveles anteriores a la escala CEFR (A1-C2).

    Mapeo heredado:
      Básico      -> A1
      Intermedio  -> B1
      Avanzado    -> C1
      Nativo      -> C2
    """
    Idioma = apps.get_model('perfil', 'Idioma')
    mapping = {
        'Básico': 'A1',
        'Intermedio': 'B1',
        'Avanzado': 'C1',
        'Nativo': 'C2',
    }
    for antiguo, nuevo in mapping.items():
        Idioma.objects.filter(nivel=antiguo).update(nivel=nuevo)


def reverse_niveles(apps, schema_editor):
    """Reversa: vuelve a los niveles genéricos (best-effort, agrupa por tramo)."""
    Idioma = apps.get_model('perfil', 'Idioma')
    mapping = {
        'A1': 'Básico',
        'A2': 'Básico',
        'B1': 'Intermedio',
        'B2': 'Intermedio',
        'C1': 'Avanzado',
        'C2': 'Nativo',
    }
    for nuevo, antiguo in mapping.items():
        Idioma.objects.filter(nivel=nuevo).update(nivel=antiguo)


class Migration(migrations.Migration):

    dependencies = [
        ('perfil', '0004_perfil_ubicacion'),
    ]

    operations = [
        migrations.RunPython(migrate_niveles_cefr, reverse_niveles),
    ]

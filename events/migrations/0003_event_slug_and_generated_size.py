from django.db import migrations, models
from django.utils.text import slugify


def historical_slug(title):
    # Замороженное правило ПР10: миграция не зависит от будущих изменений utils.py.
    letters = dict(zip(
        "абвгдеёжзийклмнопрстуфхцчшщъыьэюя",
        ("a", "b", "v", "g", "d", "e", "yo", "zh", "z", "i", "y", "k", "l", "m", "n", "o", "p", "r", "s", "t", "u", "f", "kh", "ts", "ch", "sh", "shch", "", "y", "", "e", "yu", "ya"),
    ))
    return slugify("".join(letters.get(char, char) for char in title.lower()))[:190] or "event"


def fill_slugs(apps, schema_editor):
    event_model = apps.get_model("events", "Event")
    for item in event_model.objects.using(schema_editor.connection.alias).all():
        item.slug = f"{historical_slug(item.title)}-{item.pk}"
        item.save(update_fields=["slug"])


class Migration(migrations.Migration):
    dependencies = [("events", "0002_initial")]

    operations = [
        migrations.AddField(model_name="event", name="slug", field=models.SlugField("Адрес страницы", max_length=220, blank=True, null=True, unique=True)),
        migrations.RunPython(fill_slugs, migrations.RunPython.noop),
        migrations.AlterField(model_name="event", name="slug", field=models.SlugField("Адрес страницы", max_length=220, blank=True, unique=True)),
        migrations.AddField(model_name="event", name="is_large", field=models.GeneratedField(
            db_persist=True,
            expression=models.Case(models.When(max_participants__gte=100, then=models.Value(True)), default=models.Value(False)),
            output_field=models.BooleanField(), verbose_name="Масштабная акция",
        )),
    ]

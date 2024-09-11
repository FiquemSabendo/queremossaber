# Generated by Django 2.1.1 on 2019-08-14 18:21

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("foi_requests", "0012_add_public_body_level"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="publicbody",
            options={"ordering": ["name"]},
        ),
        migrations.AddField(
            model_name="foirequest",
            name="previous_protocol",
            field=models.CharField(blank=True, max_length=8),
        ),
        migrations.AlterField(
            model_name="publicbody",
            name="uf",
            field=models.CharField(
                blank=True,
                choices=[
                    ("AC", "Acre"),
                    ("AL", "Alagoas"),
                    ("AM", "Amazonas"),
                    ("AP", "Amapá"),
                    ("BA", "Bahia"),
                    ("CE", "Ceará"),
                    ("DF", "Distrito Federal"),
                    ("ES", "Espírito Santo"),
                    ("GO", "Goiás"),
                    ("MA", "Maranhão"),
                    ("MG", "Minas Gerais"),
                    ("MS", "Mato Grosso do Sul"),
                    ("MT", "Mato Grosso"),
                    ("PA", "Pará"),
                    ("PB", "Paraíba"),
                    ("PE", "Pernambuco"),
                    ("PI", "Piauí"),
                    ("PR", "Paraná"),
                    ("RJ", "Rio de Janeiro"),
                    ("RN", "Rio Grande do Norte"),
                    ("RO", "Rondônia"),
                    ("RR", "Roraima"),
                    ("RS", "Rio Grande do Sul"),
                    ("SC", "Santa Catarina"),
                    ("SE", "Sergipe"),
                    ("SP", "São Paulo"),
                    ("TO", "Tocantins"),
                ],
                max_length=2,
            ),
        ),
    ]

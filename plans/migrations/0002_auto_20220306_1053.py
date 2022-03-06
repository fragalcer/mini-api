# Generated by Django 3.2.12 on 2022-03-06 10:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('plans', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='plan',
            name='name',
            field=models.CharField(default='Basic', help_text='Name of site-wide variable', max_length=200),
        ),
        migrations.AlterField(
            model_name='plan',
            name='value',
            field=models.JSONField(blank=True, default=dict(original_image=False, temporary_link=False, thumbnail_200=True, thumbnail_400=False), help_text='Value of site-wide variable that scripts can reference - must be valid JSON', null=True),
        ),
    ]

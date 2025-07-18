# Generated by Django 5.2.1 on 2025-06-26 14:17

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0014_tripmember_role'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='TripListItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('item_type', models.CharField(choices=[('flight', 'Flight'), ('hotel', 'Hotel'), ('custom', 'Custom Item')], max_length=20)),
                ('title', models.TextField()),
                ('description', models.TextField(blank=True)),
                ('price', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('item_data', models.JSONField(blank=True, default=dict)),
                ('added_date', models.DateTimeField(auto_now_add=True)),
                ('added_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('trip', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='list_items', to='project.trip')),
            ],
            options={
                'ordering': ['-added_date'],
            },
        ),
    ]

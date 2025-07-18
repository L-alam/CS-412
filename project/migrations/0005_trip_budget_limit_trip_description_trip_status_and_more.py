# Generated by Django 5.2.1 on 2025-06-18 21:20

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0004_alter_trip_end_date_alter_trip_start_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='trip',
            name='budget_limit',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True),
        ),
        migrations.AddField(
            model_name='trip',
            name='description',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='trip',
            name='status',
            field=models.CharField(choices=[('planning', 'Planning'), ('confirmed', 'Confirmed'), ('completed', 'Completed'), ('cancelled', 'Cancelled')], default='planning', max_length=20),
        ),
        migrations.AlterField(
            model_name='trip',
            name='end_date',
            field=models.DateTimeField(),
        ),
        migrations.AlterField(
            model_name='trip',
            name='start_date',
            field=models.DateTimeField(),
        ),
        migrations.CreateModel(
            name='Plan',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('trip', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='trip_plan', to='project.trip')),
            ],
        ),
        migrations.CreateModel(
            name='Destination',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('city', models.TextField()),
                ('country', models.TextField()),
                ('plan', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='destination', to='project.plan')),
            ],
        ),
    ]

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0008_alter_booking_status'),
    ]

    operations = [
        migrations.CreateModel(
            name='PropertyMedia',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('url', models.CharField(max_length=600)),
                ('type', models.CharField(choices=[('image', 'Image'), ('video', 'Video')], default='image', max_length=10)),
                ('order', models.PositiveIntegerField(default=0)),
                ('property', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='media', to='core.property')),
            ],
        ),
    ]

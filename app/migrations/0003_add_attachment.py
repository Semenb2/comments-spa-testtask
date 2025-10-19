from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):

    dependencies = [
        ('app', '0001_initial'),  
    ]

    operations = [
        migrations.CreateModel(
            name='Attachment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file', models.FileField(upload_to='uploads/')),
                ('type', models.CharField(choices=[('image', 'image'), ('text', 'text')], max_length=10)),
                ('width', models.IntegerField(blank=True, null=True)),
                ('height', models.IntegerField(blank=True, null=True)),
                ('size_bytes', models.IntegerField()),
                ('comment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='attachments', to='app.comment')),
            ],
        ),
    ]

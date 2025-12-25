# Generated manual migration to add new fields and models
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0002_remove_profile_bio_remove_profile_location_and_more'),
    ]

    operations = [
        # Profile new fields
        migrations.AddField(
            model_name='profile',
            name='nid',
            field=models.CharField(max_length=50, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='profile',
            name='phone',
            field=models.CharField(max_length=30, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='profile',
            name='location',
            field=models.CharField(max_length=255, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='profile',
            name='is_approved',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='profile',
            name='is_banned',
            field=models.BooleanField(default=False),
        ),

        # InspectionRequest new fields
        migrations.AddField(
            model_name='inspectionrequest',
            name='req_type',
            field=models.CharField(choices=[('New Construction', 'New Construction'), ('Reinspection', 'Reinspection')], default='New Construction', max_length=30),
        ),
        migrations.AddField(
            model_name='inspectionrequest',
            name='fee',
            field=models.DecimalField(default=0, max_digits=10, decimal_places=2),
        ),
        migrations.AlterField(
            model_name='inspectionrequest',
            name='status',
            field=models.CharField(choices=[('Pending', 'Pending'), ('Assigned', 'Assigned'), ('Approved', 'Approved'), ('Rejected', 'Rejected'), ('Completed', 'Completed'), ('Paid', 'Paid')], default='Pending', max_length=20),
        ),

        # Create InspectionReport
        migrations.CreateModel(
            name='InspectionReport',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('inspection_date', models.DateTimeField(auto_now_add=False)),
                ('structural_evaluation', models.TextField(blank=True)),
                ('compliance_checklist', models.TextField(blank=True)),
                ('decision', models.CharField(blank=True, max_length=20, choices=[('Approved', 'Approved'), ('Rejected', 'Rejected')])),
                ('remarks', models.TextField(blank=True)),
                ('inspection_request', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='report', to='myapp.inspectionrequest')),
                ('inspector', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='reports', to='auth.user')),
            ],
        ),

        # Create Complaint
        migrations.CreateModel(
            name='Complaint',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('message', models.TextField()),
                ('admin_response', models.TextField(blank=True)),
                ('resolved', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('reporter', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='complaints_made', to='auth.user')),
                ('against_inspector', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='complaints_received', to='auth.user')),
            ],
        ),

        # Create Message
        migrations.CreateModel(
            name='Message',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('subject', models.CharField(blank=True, max_length=200)),
                ('body', models.TextField()),
                ('sent_at', models.DateTimeField(auto_now_add=True)),
                ('is_read', models.BooleanField(default=False)),
                ('recipient', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='received_messages', to='auth.user')),
                ('sender', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sent_messages', to='auth.user')),
            ],
        ),

        # Create Payment
        migrations.CreateModel(
            name='Payment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.DecimalField(max_digits=10, decimal_places=2)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('inspection_request', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='payments', to='myapp.inspectionrequest')),
                ('payer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='payments', to='auth.user')),
            ],
        ),

        # Create AdminBalance
        migrations.CreateModel(
            name='AdminBalance',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('balance', models.DecimalField(default=0, max_digits=12, decimal_places=2)),
            ],
        ),
    ]

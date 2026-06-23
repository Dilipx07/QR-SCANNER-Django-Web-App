from django.db import migrations


def seed_default_vendor(apps, schema_editor):
    vendor_master = apps.get_model("QR", "Gas_Cylinder_Vendors_Master")
    vendor_master.objects.get_or_create(
        gas_cylinder_vendor_name="Dilip",
        defaults={
            "gas_cylinder_vendor_active": True,
            "gas_cylinder_vendor_contact_person": "",
            "gas_cylinder_vendor_phone": "",
            "gas_cylinder_vendor_email": "",
            "gas_cylinder_vendor_address": "",
        },
    )


class Migration(migrations.Migration):

    dependencies = [
        ("QR", "0033_vendor_details"),
    ]

    operations = [
        migrations.RunPython(seed_default_vendor, migrations.RunPython.noop),
    ]

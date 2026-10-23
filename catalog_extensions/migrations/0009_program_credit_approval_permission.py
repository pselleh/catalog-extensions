from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [("catalog_extensions", "0008_learning_credit_plans")]
    operations = [migrations.AlterModelOptions(
        name="certificateprogramcatalogmetadata",
        options={
            "verbose_name": "CBA certificate program catalog metadata",
            "verbose_name_plural": "CBA certificate program catalog metadata",
            "permissions": [("approve_program_credit_plan", "Can approve certificate program credit plans")],
        },
    )]

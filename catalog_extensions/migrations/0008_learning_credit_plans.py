from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("catalog_extensions", "0007_catalog_contract_v2")]
    operations = [
        migrations.AddField(
            model_name="microcoursecatalogmetadata", name="credit_plan",
            field=models.JSONField(blank=True, default=dict),
        ),
        migrations.AddField(
            model_name="certificateprogramcatalogmetadata", name="credit_plan",
            field=models.JSONField(blank=True, default=dict),
        ),
    ]

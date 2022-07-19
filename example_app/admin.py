import tempfile
from itertools import chain

from django.contrib import admin
from django.contrib.admin.utils import NestedObjects
from django.core import serializers
from django.forms import forms
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.urls import path

from example_app.models import *


class ImportFileForm(forms.Form):
    file = forms.FileField()


@admin.action(description="Export Model")
def export_model(modeladmin, request, queryset):
    model_file = tempfile.TemporaryFile()
    with model_file as tmp_file:
        serialized_objects = serializers.serialize(
            "json", queryset
        )
        tmp_file.write(serialized_objects.encode("utf-8"))
        tmp_file.seek(0)
        response = HttpResponse(tmp_file.read(), content_type="application/json")
        response["Content-Disposition"] = "attachment; filename=model.json"
        return response


@admin.action(description="Export Model with related objects")
def export_model_with_related_objects(modeladmin, request, queryset):
    data_model_file = tempfile.TemporaryFile()
    with data_model_file as tmp_file:
        # Iterate over all objects, including related objects
        collector = NestedObjects(using="default")

        # Collect all objects to be exported
        collector.collect(queryset)

        objects = list(chain.from_iterable(collector.data.values()))
        serialized_objects = serializers.serialize(
            "json", objects, use_natural_foreign_keys=True, use_natural_primary_keys=True
        )
        tmp_file.write(serialized_objects.encode("utf-8"))
        tmp_file.seek(0)
        response = HttpResponse(tmp_file.read(), content_type="application/json")
        response["Content-Disposition"] = "attachment; filename=model_with_related_objects.json"
        return response


class PersonAdmin(admin.ModelAdmin):
    actions = [export_model, export_model_with_related_objects]

    # Customize the list view
    change_list_template = "admin_changelist.html"

    def get_urls(self):
        """Get urls """
        urls = super().get_urls()
        my_urls = [
            path("import-json/", self.import_from_json),
        ]
        return my_urls + urls

    def import_from_json(self, request):
        """Import data models from json file"""
        if request.method == "POST":
            file = request.FILES["file"]
            data_model_file = file.read()
            data_model_file = data_model_file.decode("utf-8")
            data_model_file = serializers.deserialize(
                "json", data_model_file, use_natural_foreign_keys=True, use_natural_primary_keys=True
            )
            for obj in data_model_file:
                obj.save()
            self.message_user(request, "Checks have been imported successfully")
            return redirect("..")
        form = ImportFileForm()
        payload = {"form": form}
        return render(request, "upload_form.html", payload)


admin.site.register(Person, PersonAdmin)
admin.site.register(Book)

from django import forms
from django.contrib import admin

from plans.models import Plan


class SettingForm(forms.ModelForm):
    class Meta:
        model = Plan
        fields = '__all__'


class SettingAdmin(admin.ModelAdmin):
    form = SettingForm


admin.site.register(Plan, SettingAdmin)

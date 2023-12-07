from django import forms

# Reordering Form and View
class PositionForm(forms.Form):
    position = forms.CharField()

class UploadFileForm(forms.Form):
    file = forms.FileField()    
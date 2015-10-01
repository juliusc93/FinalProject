from django import forms


class PlaceForm(forms.Form):
    place = forms.CharField(label="Select your place", max_length=100)

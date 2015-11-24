from django import forms


class PlaceForm(forms.Form):
    place = forms.CharField(label="Select your place", max_length=100)

class UserForm(forms.Form):
    user = forms.CharField(label="Enter a username (not their screen name):", max_length=100)
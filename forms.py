from django import forms


class JoinRoomForm(forms.Form):
    room_number = forms.CharField(label="Room number", max_length=3, empty_value='42')


class SetNameForm(forms.Form):
    user_name = forms.CharField(label="Your name", max_length=25, empty_value='NoName', required=False)

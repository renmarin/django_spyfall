from django.db import models

# Create your models here.


class Places(models.Model):
    place = models.CharField(max_length=200)

    def __str__(self):
        return f'{self.place}'


class Roles(models.Model):
    place = models.ForeignKey(Places, on_delete=models.CASCADE)
    role = models.CharField(max_length=200)
    picture = models.CharField(max_length=200)

    def __str__(self):
        return f"{self.role} in {self.place}; {self.picture} image"


class Players(models.Model):
    room_id = models.CharField(max_length=200)
    players = models.CharField(max_length=200)
    names = models.CharField(max_length=200)
    refresh_room = models.BooleanField(default=False)
    start = models.BooleanField(default=False)
    end_time = models.CharField(max_length=200)


'''
|id|place|      |place|role|picture|
'''

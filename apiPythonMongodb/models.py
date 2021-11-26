
from django.db import models


class Pais(models.Model):

    codigo = models.CharField(max_length=2,unique=True, blank=True)
    nombre = models.CharField(max_length=10, blank=True)
    region = models.CharField(max_length=10)
    poblacion = models.IntegerField()
    moneda = models.CharField(max_length=10)
    idioma = models.CharField(max_length=10)
    paisesFronterizos = models.CharField(max_length=10)
    bandera = models.CharField(max_length=10)
    ubicacion = models.CharField(max_length=10)

class Jugador(models.Model):
    rol = models.CharField(max_length=10)
    
    


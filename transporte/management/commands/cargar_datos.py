from django.core.management.base import BaseCommand
from transporte.models import *

class Command(BaseCommand):
    help = 'Carga datos iniciales para el sistema de logística'

    def handle(self, *args, **options):
        # Crear clientes
        clientes = [
            Cliente(nombre="Empresa ABC Ltda.", rut="76.123.456-7", email="contacto@empresaabc.cl", 
                   telefono="+56912345678", tipo_cliente="EMPRESA", direccion="Av. Principal 123, Santiago"),
            Cliente(nombre="María González", rut="12.345.678-9", email="maria.gonzalez@email.com", 
                   telefono="+56987654321", tipo_cliente="NATURAL", direccion="Calle Secundaria 456, Valparaíso"),
        ]
        Cliente.objects.bulk_create(clientes)

        # Crear vehículos
        vehiculos = [
            Vehiculo(patente="AB123CD", tipo_vehiculo="CAMION", marca="Volvo", modelo="FH16", 
                    capacidad_kg=20000, año=2022, activo=True),
            Vehiculo(patente="EF456GH", tipo_vehiculo="FURGON", marca="Mercedes", modelo="Sprinter", 
                    capacidad_kg=3500, año=2023, activo=True),
        ]
        Vehiculo.objects.bulk_create(vehiculos)

        # Crear aeronaves
        aeronaves = [
            Aeronave(matricula="CC-ABC", tipo_aeronave="AVION", modelo="Cessna 208", 
                    capacidad_kg=1500, horas_vuelo=500, activo=True),
            Aeronave(matricula="CC-DEF", tipo_aeronave="HELICOPTERO", modelo="Bell 206", 
                    capacidad_kg=800, horas_vuelo=300, activo=True),
        ]
        Aeronave.objects.bulk_create(aeronaves)

        # Crear conductores
        conductores = [
            Conductor(nombre="Juan Pérez", rut="11.111.111-1", licencia="A1", 
                     telefono="+56911111111", email="juan@logistica.cl", activo=True),
            Conductor(nombre="Carlos López", rut="22.222.222-2", licencia="A2", 
                     telefono="+56922222222", email="carlos@logistica.cl", activo=True),
        ]
        Conductor.objects.bulk_create(conductores)

        # Crear pilotos
        pilotos = [
            Piloto(nombre="Ana Silva", rut="33.333.333-3", certificacion="ATP", 
                  horas_vuelo=1500, telefono="+56933333333", email="ana@logistica.cl", activo=True),
            Piloto(nombre="Roberto Díaz", rut="44.444.444-4", certificacion="CPL", 
                  horas_vuelo=800, telefono="+56944444444", email="roberto@logistica.cl", activo=True),
        ]
        Piloto.objects.bulk_create(pilotos)

        # Crear rutas
        rutas = [
            Ruta(origen="Santiago", destino="Valparaíso", tipo_transporte="TERRESTRE", 
                distancia_km=120, tiempo_estimado="02:00:00", costo_base=50000, activa=True),
            Ruta(origen="Santiago", destino="Concepción", tipo_transporte="AEREO", 
                distancia_km=500, tiempo_estimado="01:15:00", costo_base=150000, activa=True),
        ]
        Ruta.objects.bulk_create(rutas)

        self.stdout.write(self.style.SUCCESS('Datos iniciales cargados exitosamente!'))
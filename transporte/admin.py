from django.contrib import admin
from .models import *

@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'rut', 'email', 'tipo_cliente', 'activo']
    list_filter = ['tipo_cliente', 'activo']
    search_fields = ['nombre', 'rut', 'email']

@admin.register(Vehiculo)
class VehiculoAdmin(admin.ModelAdmin):
    list_display = ['patente', 'tipo_vehiculo', 'marca', 'capacidad_kg', 'activo']
    list_filter = ['tipo_vehiculo', 'activo']
    search_fields = ['patente', 'marca']

@admin.register(Aeronave)
class AeronaveAdmin(admin.ModelAdmin):
    list_display = ['matricula', 'tipo_aeronave', 'modelo', 'capacidad_kg', 'activo']
    list_filter = ['tipo_aeronave', 'activo']
    search_fields = ['matricula', 'modelo']

@admin.register(Conductor)
class ConductorAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'rut', 'licencia', 'vehiculo_asignado', 'activo']
    list_filter = ['activo']
    search_fields = ['nombre', 'rut', 'licencia']

@admin.register(Piloto)
class PilotoAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'rut', 'certificacion', 'aeronave_asignada', 'activo']
    list_filter = ['activo']
    search_fields = ['nombre', 'rut', 'certificacion']

@admin.register(Ruta)
class RutaAdmin(admin.ModelAdmin):
    list_display = ['origen', 'destino', 'tipo_transporte', 'distancia_km', 'activa']
    list_filter = ['tipo_transporte', 'activa']
    search_fields = ['origen', 'destino']

@admin.register(Carga)
class CargaAdmin(admin.ModelAdmin):
    list_display = ['descripcion', 'cliente', 'tipo_carga', 'peso_kg', 'valor_declarado']
    list_filter = ['tipo_carga']
    search_fields = ['descripcion', 'cliente__nombre']

@admin.register(Despacho)
class DespachoAdmin(admin.ModelAdmin):
    list_display = ['codigo_seguimiento', 'cliente', 'estado', 'fecha_despacho', 'costo_envio']
    list_filter = ['estado', 'fecha_despacho']
    search_fields = ['codigo_seguimiento', 'cliente__nombre']

@admin.register(Cotizacion)
class CotizacionAdmin(admin.ModelAdmin):
    list_display = ['codigo_seguimiento', 'origen', 'destino', 'estado', 'costo_total']
    list_filter = ['estado']
    search_fields = ['codigo_seguimiento', 'origen', 'destino']
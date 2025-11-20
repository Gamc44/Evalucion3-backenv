from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from decimal import Decimal
from datetime import timedelta
import uuid

class Cliente(models.Model):
    TIPO_CLIENTE = [
        ('NATURAL', 'Persona Natural'),
        ('EMPRESA', 'Empresa'),
    ]
    
    nombre = models.CharField(max_length=100)
    rut = models.CharField(max_length=12, unique=True)
    email = models.EmailField()
    telefono = models.CharField(max_length=15)
    tipo_cliente = models.CharField(max_length=10, choices=TIPO_CLIENTE)
    direccion = models.TextField()
    activo = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.nombre} ({self.rut})"

class Vehiculo(models.Model):
    TIPO_VEHICULO = [
        ('CAMION', 'Camión'),
        ('FURGON', 'Furgón'),
        ('BUS', 'Bus'),
        ('VAN', 'Van'),
    ]
    
    patente = models.CharField(max_length=10, unique=True)
    tipo_vehiculo = models.CharField(max_length=10, choices=TIPO_VEHICULO)
    marca = models.CharField(max_length=50)
    modelo = models.CharField(max_length=50)
    capacidad_kg = models.IntegerField()
    año = models.IntegerField()
    activo = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.tipo_vehiculo} - {self.patente}"

class Aeronave(models.Model):
    TIPO_AERONAVE = [
        ('AVION', 'Avión'),
        ('HELICOPTERO', 'Helicóptero'),
    ]
    
    matricula = models.CharField(max_length=10, unique=True)
    tipo_aeronave = models.CharField(max_length=15, choices=TIPO_AERONAVE)
    modelo = models.CharField(max_length=50)
    capacidad_kg = models.IntegerField()
    horas_vuelo = models.IntegerField(default=0)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.tipo_aeronave} - {self.matricula}"

class Conductor(models.Model):
    nombre = models.CharField(max_length=100)
    rut = models.CharField(max_length=12, unique=True)
    licencia = models.CharField(max_length=20)
    telefono = models.CharField(max_length=15)
    email = models.EmailField()
    vehiculo_asignado = models.ForeignKey(Vehiculo, on_delete=models.SET_NULL, null=True, blank=True)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.nombre} ({self.licencia})"

class Piloto(models.Model):
    nombre = models.CharField(max_length=100)
    rut = models.CharField(max_length=12, unique=True)
    certificacion = models.CharField(max_length=50)
    horas_vuelo = models.IntegerField(default=0)
    telefono = models.CharField(max_length=15)
    email = models.EmailField()
    aeronave_asignada = models.ForeignKey(Aeronave, on_delete=models.SET_NULL, null=True, blank=True)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.nombre} ({self.certificacion})"

class Ruta(models.Model):
    TIPO_TRANSPORTE = [
        ('TERRESTRE', 'Terrestre'),
        ('AEREO', 'Aéreo'),
    ]
    
    origen = models.CharField(max_length=100)
    destino = models.CharField(max_length=100)
    tipo_transporte = models.CharField(max_length=10, choices=TIPO_TRANSPORTE)
    distancia_km = models.FloatField()
    tiempo_estimado = models.DurationField()
    costo_base = models.DecimalField(max_digits=10, decimal_places=2)
    activa = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.origen} → {self.destino} ({self.tipo_transporte})"

class Carga(models.Model):
    TIPO_CARGA = [
        ('FRAGIL', 'Frágil'),
        ('PELIGROSA', 'Peligrosa'),
        ('GENERAL', 'General'),
        ('REFRIGERADA', 'Refrigerada'),
    ]
    
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    descripcion = models.CharField(max_length=200)
    tipo_carga = models.CharField(max_length=15, choices=TIPO_CARGA)
    peso_kg = models.DecimalField(max_digits=10, decimal_places=2)
    valor_declarado = models.DecimalField(max_digits=15, decimal_places=2)
    dimensiones = models.CharField(max_length=50, help_text="Largo x Ancho x Alto en cm")
    requiere_refrigeracion = models.BooleanField(default=False)
    instrucciones_especiales = models.TextField(blank=True)

    def __str__(self):
        return f"{self.descripcion} - {self.cliente.nombre}"

class Despacho(models.Model):
    ESTADO_DESPACHO = [
        ('PENDIENTE', 'Pendiente'),
        ('ASIGNADO', 'Asignado'),
        ('EN_RUTA', 'En Ruta'),
        ('ENTREGADO', 'Entregado'),
        ('CANCELADO', 'Cancelado'),
    ]
    
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    carga = models.ForeignKey(Carga, on_delete=models.CASCADE)
    ruta = models.ForeignKey(Ruta, on_delete=models.CASCADE)
    vehiculo = models.ForeignKey(Vehiculo, on_delete=models.SET_NULL, null=True, blank=True)
    aeronave = models.ForeignKey(Aeronave, on_delete=models.SET_NULL, null=True, blank=True)
    conductor = models.ForeignKey(Conductor, on_delete=models.SET_NULL, null=True, blank=True)
    piloto = models.ForeignKey(Piloto, on_delete=models.SET_NULL, null=True, blank=True)
    
    fecha_despacho = models.DateTimeField(auto_now_add=True)
    fecha_estimada_entrega = models.DateTimeField()
    fecha_entrega_real = models.DateTimeField(null=True, blank=True)
    
    estado = models.CharField(max_length=10, choices=ESTADO_DESPACHO, default='PENDIENTE')
    costo_envio = models.DecimalField(max_digits=12, decimal_places=2)
    codigo_seguimiento = models.CharField(max_length=20, unique=True)
    
    observaciones = models.TextField(blank=True)
    creado_por = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"Despacho {self.codigo_seguimiento} - {self.estado}"

    def save(self, *args, **kwargs):
        if not self.codigo_seguimiento:
            self.codigo_seguimiento = str(uuid.uuid4())[:8].upper()
        super().save(*args, **kwargs)

class Cotizacion(models.Model):
    ESTADO_COTIZACION = [
        ('PENDIENTE', 'Pendiente'),
        ('CONFIRMADA', 'Confirmada'),
        ('RECHAZADA', 'Rechazada'),
    ]
    
    # Datos de la cotización
    origen = models.CharField(max_length=100)
    destino = models.CharField(max_length=100)
    peso_kg = models.DecimalField(max_digits=10, decimal_places=2)
    tipo_carga = models.CharField(max_length=15)
    descripcion = models.TextField(blank=True)
    distancia_km = models.FloatField(default=0)
    
    # Cálculos de cotización
    costo_por_kg = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    costo_total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    # Información del cliente
    nombre_cliente = models.CharField(max_length=100, blank=True)
    email_cliente = models.EmailField(blank=True)
    telefono_cliente = models.CharField(max_length=15, blank=True)
    
    # Estado y seguimiento
    estado = models.CharField(max_length=10, choices=ESTADO_COTIZACION, default='PENDIENTE')
    codigo_seguimiento = models.CharField(max_length=20, unique=True, blank=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_confirmacion = models.DateTimeField(null=True, blank=True)
    
    # Relación con despacho (si se confirma)
    despacho = models.OneToOneField(Despacho, on_delete=models.SET_NULL, null=True, blank=True)
    
    def __str__(self):
        return f"Cotización {self.codigo_seguimiento} - {self.estado}"
    
    def save(self, *args, **kwargs):
        if not self.codigo_seguimiento:
            self.codigo_seguimiento = f"COT-{str(uuid.uuid4())[:8].upper()}"
        super().save(*args, **kwargs)
    
    def confirmar_cotizacion(self, nombre, email, telefono):
        """Convierte una cotización en un pedido confirmado"""
        self.nombre_cliente = nombre
        self.email_cliente = email
        self.telefono_cliente = telefono
        self.estado = 'CONFIRMADA'
        self.fecha_confirmacion = timezone.now()
        self.save()
        
        # Crear el despacho automáticamente
        return self.crear_despacho()
    
    def crear_despacho(self):
        """Crea un despacho a partir de la cotización confirmada"""
        # Crear cliente si no existe
        cliente, created = Cliente.objects.get_or_create(
            email=self.email_cliente,
            defaults={
                'nombre': self.nombre_cliente,
                'rut': 'TEMP-RUT',
                'telefono': self.telefono_cliente,
                'tipo_cliente': 'NATURAL',
                'direccion': 'Por definir'
            }
        )
        
        # CORREGIDO: Usar Decimal para evitar el error
        valor_declarado = self.costo_total * Decimal('0.8')
        
        # Crear carga
        carga = Carga.objects.create(
            cliente=cliente,
            descripcion=self.descripcion or f"Carga de {self.peso_kg}kg",
            tipo_carga=self.tipo_carga,
            peso_kg=self.peso_kg,
            valor_declarado=valor_declarado,
            dimensiones="100x50x50 cm",
            requiere_refrigeracion=self.tipo_carga == 'REFRIGERADA'
        )
        
        # CORREGIDO: Usar Decimal para evitar el error
        costo_base_ruta = self.costo_total * Decimal('0.3')
        
        # Buscar ruta apropiada
        ruta, created = Ruta.objects.get_or_create(
            origen=self.origen,
            destino=self.destino,
            defaults={
                'tipo_transporte': 'TERRESTRE' if self.distancia_km < 1000 else 'AEREO',
                'distancia_km': self.distancia_km,
                'tiempo_estimado': timedelta(hours=2 if self.distancia_km < 500 else 1),
                'costo_base': costo_base_ruta,
                'activa': True
            }
        )
        
        # Crear despacho
        despacho = Despacho.objects.create(
            cliente=cliente,
            carga=carga,
            ruta=ruta,
            costo_envio=self.costo_total,
            codigo_seguimiento=f"DESP-{str(uuid.uuid4())[:8].upper()}",
            fecha_estimada_entrega=timezone.now() + timedelta(days=3),
            creado_por=User.objects.first()
        )
        
        self.despacho = despacho
        self.save()
        
        return despacho
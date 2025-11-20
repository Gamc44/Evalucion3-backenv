from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import JsonResponse
from rest_framework import viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from .serializers import *
from .models import Despacho, Cliente, Vehiculo, Aeronave, Conductor, Piloto, Ruta, Carga, Cotizacion
from django.contrib.auth.models import User
from decimal import Decimal
from django.utils import timezone

# Función para verificar si es admin
def es_admin(user):
    return user.is_authenticated and user.is_staff

def index(request):
    try:
        # Estadísticas para la página principal
        total_despachos = Despacho.objects.count()
        pendientes = Despacho.objects.filter(estado='PENDIENTE').count()
        en_ruta = Despacho.objects.filter(estado='EN_RUTA').count()
        entregados = Despacho.objects.filter(estado='ENTREGADO').count()
        
        context = {
            'total_despachos': total_despachos,
            'pendientes': pendientes,
            'en_ruta': en_ruta,
            'entregados': entregados,
        }
    except:
        # Si hay error (tablas no creadas), mostrar ceros
        context = {
            'total_despachos': 0,
            'pendientes': 0,
            'en_ruta': 0,
            'entregados': 0,
        }
    
    return render(request, 'transporte/index.html', context)

def cotizar_envio(request):
    if request.method == 'POST':
        # Lógica de cotización
        origen = request.POST.get('origen')
        destino = request.POST.get('destino')
        peso = Decimal(request.POST.get('peso', '0'))
        tipo_carga = request.POST.get('tipo_carga')
        descripcion = request.POST.get('descripcion', '')
        
        # Distancias entre ciudades (km)
        distancias = {
            'Santiago': {'Valparaíso': 120, 'Concepción': 500, 'Temuco': 675, 'Antofagasta': 1368, 'Iquique': 1785, 'Puerto Montt': 1020},
            'Valparaíso': {'Santiago': 120, 'Concepción': 560, 'Temuco': 735, 'Antofagasta': 1488, 'Iquique': 1905, 'Puerto Montt': 1140},
            'Concepción': {'Santiago': 500, 'Valparaíso': 560, 'Temuco': 305, 'Antofagasta': 1868, 'Iquique': 2285, 'Puerto Montt': 520},
            'Temuco': {'Santiago': 675, 'Valparaíso': 735, 'Concepción': 305, 'Antofagasta': 2043, 'Iquique': 2460, 'Puerto Montt': 350},
            'Antofagasta': {'Santiago': 1368, 'Valparaíso': 1488, 'Concepción': 1868, 'Temuco': 2043, 'Iquique': 417, 'Puerto Montt': 2393},
            'Iquique': {'Santiago': 1785, 'Valparaíso': 1905, 'Concepción': 2285, 'Temuco': 2460, 'Antofagasta': 417, 'Puerto Montt': 2810},
            'Puerto Montt': {'Santiago': 1020, 'Valparaíso': 1140, 'Concepción': 520, 'Temuco': 350, 'Antofagasta': 2393, 'Iquique': 2810}
        }
        
        distancia = Decimal(str(distancias.get(origen, {}).get(destino, 100)))
        
        # CORREGIDO: Usar Decimal
        costos_por_kg = {
            'GENERAL': Decimal('100'),
            'FRAGIL': Decimal('150'),
            'PELIGROSA': Decimal('200'),
            'REFRIGERADA': Decimal('180')
        }
        
        costo_por_kg = costos_por_kg.get(tipo_carga, Decimal('100'))
        
        costo_base = Decimal('2000')
        costo_distancia = distancia * Decimal('5')
        costo_peso = peso * costo_por_kg
        costo_total = costo_base + costo_distancia + costo_peso
        
        nombres_tipo_carga = {
            'GENERAL': 'General',
            'FRAGIL': 'Frágil',
            'PELIGROSA': 'Peligrosa',
            'REFRIGERADA': 'Refrigerada'
        }
        
        # Guardar la cotización en la base de datos
        cotizacion = Cotizacion.objects.create(
            origen=origen,
            destino=destino,
            peso_kg=peso,
            tipo_carga=tipo_carga,
            descripcion=descripcion,
            distancia_km=float(distancia),
            costo_por_kg=costo_por_kg,
            costo_total=costo_total
        )
        
        return render(request, 'transporte/cotizar.html', {
            'cotizacion': costo_total,
            'origen': origen,
            'destino': destino,
            'peso': peso,
            'distancia': distancia,
            'tipo_carga': nombres_tipo_carga.get(tipo_carga, tipo_carga),
            'costo_por_kg': costo_por_kg,
            'codigo_cotizacion': cotizacion.codigo_seguimiento
        })
    
    return render(request, 'transporte/cotizar.html')

def confirmar_cotizacion(request):
    if request.method == 'POST':
        codigo_cotizacion = request.POST.get('codigo_cotizacion')
        nombre = request.POST.get('nombre')
        email = request.POST.get('email')
        telefono = request.POST.get('telefono')
        
        try:
            cotizacion = Cotizacion.objects.get(codigo_seguimiento=codigo_cotizacion, estado='PENDIENTE')
            despacho = cotizacion.confirmar_cotizacion(nombre, email, telefono)
            
            return render(request, 'transporte/confirmacion_exitosa.html', {
                'cotizacion': cotizacion,
                'despacho': despacho
            })
        except Cotizacion.DoesNotExist:
            return render(request, 'transporte/error.html', {
                'mensaje': 'Cotización no encontrada o ya fue confirmada'
            })
    
    return redirect('cotizar')

@login_required
def pedidos(request):
    try:
        if request.user.is_staff:
            # Admin ve todas las cotizaciones y despachos
            cotizaciones = Cotizacion.objects.all().order_by('-fecha_creacion')
            despachos = Despacho.objects.all().order_by('-fecha_despacho')
        else:
            # Cliente ve solo sus pedidos (por email)
            email_usuario = request.user.email
            cotizaciones = Cotizacion.objects.filter(email_cliente=email_usuario).order_by('-fecha_creacion')
            despachos = Despacho.objects.filter(cliente__email=email_usuario)
        
        return render(request, 'transporte/pedidos.html', {
            'cotizaciones': cotizaciones,
            'despachos': despachos,
            'es_admin': request.user.is_staff
        })
    except:
        return render(request, 'transporte/pedidos.html', {
            'cotizaciones': [],
            'despachos': [],
            'es_admin': request.user.is_staff if request.user.is_authenticated else False
        })

@user_passes_test(es_admin)
def dashboard_admin(request):
    try:
        # Estadísticas mejoradas para admin
        total_cotizaciones = Cotizacion.objects.count()
        cotizaciones_pendientes = Cotizacion.objects.filter(estado='PENDIENTE').count()
        cotizaciones_confirmadas = Cotizacion.objects.filter(estado='CONFIRMADA').count()
        
        total_despachos = Despacho.objects.count()
        despachos_pendientes = Despacho.objects.filter(estado='PENDIENTE').count()
        despachos_ruta = Despacho.objects.filter(estado='EN_RUTA').count()
        despachos_entregados = Despacho.objects.filter(estado='ENTREGADO').count()
        
        # Estadísticas de conversión
        tasa_conversion = (cotizaciones_confirmadas / total_cotizaciones * 100) if total_cotizaciones > 0 else 0
        
        stats = {
            'total_cotizaciones': total_cotizaciones,
            'cotizaciones_pendientes': cotizaciones_pendientes,
            'cotizaciones_confirmadas': cotizaciones_confirmadas,
            'total_despachos': total_despachos,
            'despachos_pendientes': despachos_pendientes,
            'despachos_ruta': despachos_ruta,
            'despachos_entregados': despachos_entregados,
            'tasa_conversion': round(tasa_conversion, 2),
            'total_clientes': Cliente.objects.count(),
            'total_vehiculos': Vehiculo.objects.filter(activo=True).count(),
            'total_aeronaves': Aeronave.objects.filter(activo=True).count(),
            'total_empleados': Conductor.objects.filter(activo=True).count() + Piloto.objects.filter(activo=True).count(),
        }
    except Exception as e:
        stats = {
            'total_cotizaciones': 0,
            'cotizaciones_pendientes': 0,
            'cotizaciones_confirmadas': 0,
            'total_despachos': 0,
            'despachos_pendientes': 0,
            'despachos_ruta': 0,
            'despachos_entregados': 0,
            'tasa_conversion': 0,
            'total_clientes': 0,
            'total_vehiculos': 0,
            'total_aeronaves': 0,
            'total_empleados': 0,
        }
    
    return render(request, 'transporte/dashboard_admin.html', {'stats': stats})

@user_passes_test(es_admin)
def gestion_pedidos(request):
    """Vista para gestionar todos los pedidos como admin"""
    try:
        # Obtener todos los despachos con información relacionada
        despachos = Despacho.objects.all().select_related(
            'cliente', 'ruta', 'conductor', 'piloto', 'vehiculo', 'aeronave'
        ).order_by('-fecha_despacho')
        
        # Filtros
        estado_filter = request.GET.get('estado', '')
        if estado_filter:
            despachos = despachos.filter(estado=estado_filter)
        
        # Estadísticas para el panel
        stats = {
            'total': Despacho.objects.count(),
            'pendientes': Despacho.objects.filter(estado='PENDIENTE').count(),
            'asignados': Despacho.objects.filter(estado='ASIGNADO').count(),
            'en_ruta': Despacho.objects.filter(estado='EN_RUTA').count(),
            'entregados': Despacho.objects.filter(estado='ENTREGADO').count(),
            'cancelados': Despacho.objects.filter(estado='CANCELADO').count(),
        }
        
        return render(request, 'transporte/gestion_pedidos.html', {
            'despachos': despachos,
            'stats': stats,
            'estado_filter': estado_filter,
            'estados': Despacho.ESTADO_DESPACHO
        })
    except Exception as e:
        return render(request, 'transporte/gestion_pedidos.html', {
            'despachos': [],
            'stats': {},
            'error': str(e)
        })

@user_passes_test(es_admin)
def actualizar_estado(request, despacho_id):
    """Actualizar el estado de un despacho"""
    if request.method == 'POST':
        try:
            despacho = Despacho.objects.get(id=despacho_id)
            nuevo_estado = request.POST.get('estado')
            
            if nuevo_estado in dict(Despacho.ESTADO_DESPACHO):
                despacho.estado = nuevo_estado
                
                # Si se marca como entregado, registrar fecha de entrega
                if nuevo_estado == 'ENTREGADO':
                    despacho.fecha_entrega_real = timezone.now()
                
                despacho.save()
                
                return JsonResponse({
                    'success': True,
                    'mensaje': f'Estado actualizado a {nuevo_estado}',
                    'nuevo_estado': nuevo_estado
                })
            else:
                return JsonResponse({'error': 'Estado inválido'}, status=400)
                
        except Despacho.DoesNotExist:
            return JsonResponse({'error': 'Despacho no encontrado'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'Método no permitido'}, status=405)

@user_passes_test(es_admin)
def asignar_empleado(request, despacho_id):
    try:
        despacho = Despacho.objects.get(id=despacho_id)
        
        if request.method == 'POST':
            conductor_id = request.POST.get('conductor')
            piloto_id = request.POST.get('piloto')
            
            if conductor_id:
                despacho.conductor = Conductor.objects.get(id=conductor_id)
            if piloto_id:
                despacho.piloto = Piloto.objects.get(id=piloto_id)
                
            despacho.estado = 'ASIGNADO'
            despacho.save()
            return redirect('gestion_pedidos')
        
        conductores = Conductor.objects.filter(activo=True)
        pilotos = Piloto.objects.filter(activo=True)
        
        return render(request, 'transporte/asignar.html', {
            'despacho': despacho,
            'conductores': conductores,
            'pilotos': pilotos
        })
    except:
        return redirect('gestion_pedidos')

def tickets(request):
    return render(request, 'transporte/tickets.html')

def register(request):
    if request.method == 'POST':
        # Crear formulario manualmente
        username = request.POST.get('username')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        
        # Validaciones básicas
        errors = []
        
        if not username:
            errors.append("El nombre de usuario es obligatorio")
        elif len(username) < 3:
            errors.append("El usuario debe tener al menos 3 caracteres")
            
        if not password1:
            errors.append("La contraseña es obligatoria")
        elif len(password1) < 8:
            errors.append("La contraseña debe tener al menos 8 caracteres")
            
        if password1 != password2:
            errors.append("Las contraseñas no coinciden")
            
        # Verificar si el usuario ya existe
        if User.objects.filter(username=username).exists():
            errors.append("Este nombre de usuario ya existe")
        
        if not errors:
            # Crear usuario
            user = User.objects.create_user(username=username, password=password1)
            user.save()
            
            # Autenticar y loguear al usuario
            user = authenticate(username=username, password=password1)
            if user is not None:
                login(request, user)
                return redirect('index')
        
        # Si hay errores, mostrar formulario con errores
        return render(request, 'transporte/register.html', {'errors': errors})
    
    # GET request - mostrar formulario vacío
    return render(request, 'transporte/register.html')

# API Views protegidas con JWT
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_info(request):
    """Información básica de la API"""
    api_data = {
        "nombre": "Logística Global API",
        "version": "1.0",
        "endpoints": {
            "clientes": "/api/clientes/",
            "vehiculos": "/api/vehiculos/", 
            "aeronaves": "/api/aeronaves/",
            "despachos": "/api/despachos/",
            "rutas": "/api/rutas/",
            "cotizaciones": "/api/cotizaciones/"
        },
        "documentacion": "/api/docs/"
    }
    return Response(api_data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_clientes(request):
    """API simple de clientes"""
    clientes = list(Cliente.objects.values('id', 'nombre', 'rut', 'email', 'activo'))
    return Response(clientes)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_vehiculos(request):
    """API simple de vehículos"""
    vehiculos = list(Vehiculo.objects.values('id', 'patente', 'tipo_vehiculo', 'capacidad_kg', 'activo'))
    return Response(vehiculos)

# VIEWSETS PARA DRF (API REST) - Protegidos con JWT
class ClienteViewSet(viewsets.ModelViewSet):
    queryset = Cliente.objects.all()
    serializer_class = ClienteSerializer
    permission_classes = [IsAuthenticated]

class VehiculoViewSet(viewsets.ModelViewSet):
    queryset = Vehiculo.objects.all()
    serializer_class = VehiculoSerializer
    permission_classes = [IsAuthenticated]

class AeronaveViewSet(viewsets.ModelViewSet):
    queryset = Aeronave.objects.all()
    serializer_class = AeronaveSerializer
    permission_classes = [IsAuthenticated]

class ConductorViewSet(viewsets.ModelViewSet):
    queryset = Conductor.objects.all()
    serializer_class = ConductorSerializer
    permission_classes = [IsAuthenticated]

class PilotoViewSet(viewsets.ModelViewSet):
    queryset = Piloto.objects.all()
    serializer_class = PilotoSerializer
    permission_classes = [IsAuthenticated]

class RutaViewSet(viewsets.ModelViewSet):
    queryset = Ruta.objects.all()
    serializer_class = RutaSerializer
    permission_classes = [IsAuthenticated]

class CargaViewSet(viewsets.ModelViewSet):
    queryset = Carga.objects.all()
    serializer_class = CargaSerializer
    permission_classes = [IsAuthenticated]

class DespachoViewSet(viewsets.ModelViewSet):
    queryset = Despacho.objects.all()
    serializer_class = DespachoSerializer
    permission_classes = [IsAuthenticated]

class CotizacionViewSet(viewsets.ModelViewSet):
    queryset = Cotizacion.objects.all()
    serializer_class = CotizacionSerializer
    permission_classes = [IsAuthenticated]
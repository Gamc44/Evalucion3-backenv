from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from .views import *

router = DefaultRouter()
router.register(r'clientes', ClienteViewSet)
router.register(r'vehiculos', VehiculoViewSet)
router.register(r'aeronaves', AeronaveViewSet)
router.register(r'conductores', ConductorViewSet)
router.register(r'pilotos', PilotoViewSet)
router.register(r'rutas', RutaViewSet)
router.register(r'cargas', CargaViewSet)
router.register(r'despachos', DespachoViewSet)
router.register(r'cotizaciones', CotizacionViewSet)

urlpatterns = [
    path('', views.index, name='index'),
    path('cotizar/', views.cotizar_envio, name='cotizar'),
    path('confirmar-cotizacion/', views.confirmar_cotizacion, name='confirmar_cotizacion'),
    path('pedidos/', views.pedidos, name='pedidos'),
    path('tickets/', views.tickets, name='tickets'),
    path('register/', views.register, name='register'),
    path('dashboard/', views.dashboard_admin, name='dashboard_admin'),
    path('gestion-pedidos/', views.gestion_pedidos, name='gestion_pedidos'),
    path('actualizar-estado/<int:despacho_id>/', views.actualizar_estado, name='actualizar_estado'),
    path('asignar/<int:despacho_id>/', views.asignar_empleado, name='asignar_empleado'),
    
    # API URLs protegidas
    path('api/', views.api_info, name='api_info'),
    path('api/clientes/', views.api_clientes, name='api_clientes'),
    path('api/vehiculos/', views.api_vehiculos, name='api_vehiculos'),
    
    # DRF API Routes
    path('api/', include(router.urls)),
]
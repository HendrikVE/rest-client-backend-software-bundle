from django.urls import path

from . import views

urlpatterns = [
    path('fixed-payload-length/', views.fixed_payload_length),
    path('update-sensor-data/', views.update_sensor_data),
    path('scale-kubernetes/', views.scale_kubernetes),
]

from django.http import JsonResponse
from rest_framework import permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

import random

from kubernetes import client, config

lorem_ipsum = (
"Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et dolore " 
"magna aliquyam erat, sed diam voluptua. At vero eos et accusam et justo duo dolores et ea rebum. Stet clita kasd "
"gubergren, no sea takimata sanctus est Lorem ipsum dolor sit amet. Lorem ipsum dolor sit amet, consetetur sadipscing " 
"elitr, sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua. At vero eos"
"et accusam et justo duo dolores et ea rebum. Stet clita kasd gubergren, no sea takimata sanctus est Lorem ipsum dolor "
"sit amet. Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore " 
"et dolore magna aliquyam erat, sed diam voluptua. At vero eos et accusam et justo duo dolores et ea rebum. Stet clita " 
"kasd gubergren, no sea takimata sanctus est Lorem ipsum dolor sit amet. Duis autem vel eum iriure dolor in hendrerit "
"in vulputate velit esse molestie consequat, vel illum dolore eu feugiat nulla facilisis at vero eros et accumsan et " 
"iusto odio dignissim qui blandit praesent luptatum zzril delenit augue duis dolore te feugait nulla facilisi. Lorem "
"ipsum dolor sit amet,"
)


@api_view(['GET', 'POST'])
@permission_classes([permissions.AllowAny])
def fixed_payload_length(request):
    # quotation marks are also send, so 2 characters are added to the output
    # MQTT-SN on RIOT is not able to receive more than a payload of 531 due to a bug
    return Response(lorem_ipsum[:529], content_type='text/plain')


@api_view(['POST'])
# TODO: Due to an open issue in the MQTT-SN implementation, the message gets too large and won't be sent when the auth
#       token is included. It works for CoAP and MQTT, but to keep comparability disable it for all of them for now)
@permission_classes([permissions.AllowAny])
def update_sensor_data(request):

    print(request.data)

    replicas = random.randint(1, 42)

    # Configs can be set in Configuration class directly or using helper utility
    config.load_kube_config()

    api_instance = client.AppsV1Api()

    api_response = api_instance.patch_namespaced_deployment_scale(
        'kubernetes-bootcamp', 'default', {'spec': {'replicas': replicas}})
    print(api_response)

    return JsonResponse({'status': 'ok'})


@api_view(['POST'])
def scale_kubernetes(request):

    # Call this request with the following payload: {"scale_factor": "34"}

    replicas = int(request.data['scale_factor'])

    # Configs can be set in Configuration class directly or using helper utility
    config.load_kube_config()

    api_instance = client.AppsV1Api()

    api_response = api_instance.patch_namespaced_deployment_scale(
        'kubernetes-bootcamp', 'default', {'spec': {'replicas': replicas}})
    print(api_response)

    return JsonResponse({'status': 'ok'})


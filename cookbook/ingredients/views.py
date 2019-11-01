from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse,JsonResponse
from django.views.decorators.http import require_POST

from django.views.decorators.csrf import csrf_protect


@require_POST
def hello(request):
	data = dict()
	if request.method == 'POST':
		data.update({'hey':'keu'})
	return JsonResponse(data)
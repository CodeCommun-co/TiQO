from django.shortcuts import render, redirect
from django.views import View
from qonto_parser.models import Configuration, Label
import requests
from qonto_parser.qonto_api import QontoApi

from qonto_parser.serializers import LabelsSerializer


# Create your views here.



def button_action(action):
    ACTIONS_POSSIBLE = [
        "get_labels",
    ]
    if action in ACTIONS_POSSIBLE:
        qontoApi = QontoApi()
        return getattr(qontoApi, action)()

class index(View):

    def get(self, request):
        labels = LabelsSerializer(Label.objects.all())

        context = {
            "labels" : labels,
            "message": "Hello, world. View",
        }
        return render(request, 'index.html', context=context)

    def post(self, request):
        data = request.POST
        for input, value in data.items():
            if input == "button_action":
                result = button_action(value)
                print(f'result {result}')


        return redirect('index')
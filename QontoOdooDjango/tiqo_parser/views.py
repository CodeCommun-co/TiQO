from django.shortcuts import render, redirect
from django.views import View
from tiqo_parser.models import Configuration, Label
import requests
from tiqo_parser.qonto_api import QontoApi

from tiqo_parser.serializers import LabelsSerializer


# Technique de sioux qui me permet de ne pas faire une class par bouton ...
# En gros, si le formulaire renvoie un inpoute avec name="button_action" value="get_labels"
# alors je lance la fonction get_labels() de la class QontoApi
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
            "message": "Hello, world.",
        }
        return render(request, 'index.html', context=context)

    def post(self, request):
        data = request.POST
        for input, value in data.items():
            if input == "button_action":
                result = button_action(value)
                print(f'result {result}')

        return redirect('index')
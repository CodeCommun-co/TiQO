from django.contrib.sites import requests
import requests
from tiqo_parser.models import Configuration, Label
from tiqo_parser.serializers import LabelsSerializer


class QontoApi():
    def __init__(self):
        config = Configuration.get_solo()
        self.login = config.qonto_login
        self.api_key = config.qonto_apikey

        if not any([self.login, self.api_key]):
            raise Exception("No Qonto credentials. Set its in the admin panel.")

    def _get_request_api(self, url):
        url = f"https://thirdparty.qonto.com/v2/{url}"

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"{self.login}:{self.api_key}"
        }

        response = requests.request("GET", url, headers=headers)
        if response.status_code == 200:
            return response.json()

        print(response.text)
        raise Exception(response.text)

    def get_labels(self):

        labels_qonto = self._get_request_api("labels")
        labels = labels_qonto.get('labels')

        # On crée les labels qui n'ont pas de parent en premier
        parents = [label for label in labels if not label.get('parent_id')]
        for label in parents:
            labeldb, created = Label.objects.get_or_create(
                uuid=label.get('id'),
                name=label.get('name'),
            )

        # On crée les labels qui ont un parent
        childs = [label for label in labels if label.get('parent_id')]
        for label in childs:
            labeldb, created = Label.objects.get_or_create(
                uuid=label.get('id'),
                name=label.get('name'),
            )

            label_parent = Label.objects.get(uuid=label.get('parent_id'))
            labeldb.parent = label_parent
            labeldb.save()

        return LabelsSerializer(Label.objects.all())

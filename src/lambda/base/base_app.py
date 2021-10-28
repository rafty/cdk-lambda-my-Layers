import json
from pynamodb.models import Model
from pynamodb.attributes import UnicodeAttribute, NumberAttribute
import requests

class UserModel(Model):
    class Meta:
        table_name = "Devio-user"
    last_name = UnicodeAttribute(hash_key=True)
    email = UnicodeAttribute(range_key=True)
    age = NumberAttribute(null=True)


def handler(event, context):
    print('request: {}'.format(json.dumps(event)))

    return {}

from .menu import Menu
from .urls import INFO_URL, MENU_URL
from .utils import request_json


class Store(object):
    def __init__(self, data={}):
        self.id = int(data.get('StoreID', -1))
        self.data = data

    def get_details(self):
        details = request_json(INFO_URL, store_id=self.id)
        return details

    def get_menu(self, lang='en'):
        response = request_json(MENU_URL, store_id=self.id, lang=lang)
        menu = Menu(response)
        return menu

    def print_info(self):
        details = self.get_details()
        print(details['StoreID'],
              details['Phone'],
              details['AddressDescription'],
              details['EstimatedWaitMinutes'])

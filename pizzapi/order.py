import requests

from .menu import Menu
from .urls import PRICE_URL, PLACE_URL, VALIDATE_URL


# TODO: Add add_coupon and remove_coupon methods
class Order(object):
    def __init__(self, store, customer):
        self.store = store
        self.menu = Menu.from_store(store_id=store.id)
        self.customer = customer
        self.data = {
            'Coupons': [], 'CustomerID': '', 'Extension': '',
            'OrderChannel': 'OLO', 'OrderID': '', 'NoCombine': True,
            'OrderMethod': 'Web', 'OrderTaker': None, 'Payments': [],
            'Products': [], 'Market': '', 'Currency': '',
            'ServiceMethod': 'Delivery', 'Tags': {}, 'Version': '1.0',
            'SourceOrganizationURI': 'order.dominos.com', 'LanguageCode': 'en',
            'Partners': {}, 'NewUser': True, 'metaData': {}, 'Amounts': {},
            'BusinessDate': '', 'EstimatedWaitMinutes': '',
            'PriceOrderTime': '', 'AmountsBreakdown': {}
        }

    # TODO: Implement item options
    def add_item(self, code, qty=1, options=[]):
        try:
            item = self.menu.variants[code]
            item.update(ID=1, isNew=True, Qty=qty, AutoRemove=False)
            self.data['Products'].append(item)
            return True
        except KeyError:
            return False

    # TODO: Raise Exception when index isn't found
    def remove_item(self, code):
        codes = [x['Code'] for x in self.data['Products']]
        return self.data['Products'].pop(codes.index(code))

    def _send(self, url, merge):
        self.data.update(
            StoreID=self.store.id,
            Email=self.customer.email,
            FirstName=self.customer.first_name,
            LastName=self.customer.last_name,
            Phone=self.customer.phone,
            Address=self.customer.address.data
        )

        for key in ('Products', 'StoreID', 'Address'):
            if key not in self.data or not self.data[key]:
                raise Exception('order has invalid value for key "%s"' % key)

        headers = {
            'Referer': 'https://order.dominos.com/en/pages/order/',
            'Content-Type': 'application/json'
        }
        r = requests.post(url=url, headers=headers, json={'Order': self.data})
        r.raise_for_status()
        json_data = r.json()
        if merge:
            for key, value in iter(json_data['Order'].items()):
                if value or not isinstance(value, list):
                    self.data[key] = value

        return json_data

    # TODO: Figure out if this validates anything that PRICE_URL does not
    def validate(self):
        response = self._send(VALIDATE_URL, True)
        return response['Status'] != -1

    # TODO: Actually test this
    def place(self, card):
        self.pay_with(card)
        response = self._send(PLACE_URL, False)
        return response

    # TODO: Add self.price() and update whenever called and items were changed
    def pay_with(self, card):
        """Use this instead of self.place when testing"""
        # get the price to check that everything worked okay
        response = self._send(PRICE_URL, True)
        if response['Status'] == -1:
            raise Exception('get price failed: %r' % response)

        self.data['Payments'] = [
            {
                'Type': 'CreditCard',
                'Expiration': card.expiration,
                'Amount': self.data['Amounts'].get('Customer', 0),
                'CardType': card.card_type,
                'Number': card.number,
                'SecurityCode': card.cvv,
                'PostalCode': card.zip
            }
        ]

"""This is a script for ordering pizza from Dominos in the command line."""

import pickle
import os.path
import click
from tabulate import tabulate
import pizzapi

CUSTOMER_DATA_FILE = 'customer_data.pkl'

def order_pizza():
    '''Main pizza-ordering function'''
    customers = []

    if os.path.isfile(CUSTOMER_DATA_FILE):
        with open(CUSTOMER_DATA_FILE, 'rb') as customer_file:
            customers = pickle.load(customer_file)
        print_customers(customers)

    customer = customer_menu(customers)
    store = store_menu(customer)
    if not store:
        return
    order = build_order(store, customer)

    while True:
        card = pizzapi.PaymentObject(click.prompt('Card Number'),
                                     click.prompt('Expiration date'),
                                     click.prompt('CVV'),
                                     click.prompt('Zip code'))
        if card.validate():
            order.pay_with(card)
            break
        click.echo('Invalid card.  Please re-enter information.')

def customer_menu(customers):
    '''Menu for adding and removing customer data'''
    while True:
        action = click.prompt('(A)dd customer, (r)emove customer, (o)rder', type=str).lower()

        if action in ['a', 'add']:
            customer = pizzapi.Customer()
            get_customer_data(customer)
            customers.append(customer)
            with open(CUSTOMER_DATA_FILE, 'wb') as customer_file:
                pickle.dump(customers, customer_file, -1)

        elif action in ['r', 'remove']:
            cust_index = click.prompt('Customer ID to remove', type=int)
            try:
                customers.remove(customers[cust_index])
                with open(CUSTOMER_DATA_FILE, 'wb') as customer_file:
                    pickle.dump(customers, customer_file, -1)
            except IndexError:
                click.echo('Customer does not exist.')

        else:
            break

    customer_index = click.prompt('Choose a customer', type=int)
    customer = customers[customer_index - 1]
    return customer

def store_menu(customer):
    try:
        stores = customer.address.nearby_open_stores()
    except:
        click.echo('Neaby stores are not available.  Please try again later.')
        return
        
    for store in stores:
        try:
            store_details = store.get_details()
            use_store = \
            click.prompt(
                'The closest open store is at {}. Expected wait time: {}  Use this store?'
                .format(store_details['StreetName'], store_details['EstimatedWaitMinutes']))\
                .lower()
            if use_store in ['y', 'yes']:
                return store
        except:
            click.echo('Neaby stores are not available.  Please try again later.')
            return

def print_customers(customers):
    print(
        tabulate(
            map(lambda c: [c.first_name, c.last_name, c.email, c.phone, c.address]
                , customers),
            ['ID', 'First', 'Last', 'Phone', 'Email', 'Address'],
            showindex="always")
    )


def get_customer_data(customer):
    '''Prompts the user for customer data'''
    customer.first_name = click.prompt('First name')
    customer.last_name = click.prompt('Last name')
    customer.email = click.prompt('Email')
    customer.phone = click.prompt('Phone')
    street = click.prompt('Street Address')
    city = click.prompt('City')
    region = click.prompt('Region')
    zipcode = click.prompt('Zip Code')
    customer.address = pizzapi.Address(street, city, region, zipcode)

def build_order(store, customer):
    '''Prompts user to build order'''
    order = pizzapi.Order(store, customer)
    while True:
        action = click.prompt('View (m)enu, (a)dd item, (r)emove item, (p)lace order',
                              type=str).lower()
        if action in ['view', 'v', 'm', 'menu']:
            store.get_menu().display()
        elif action in ['add', 'a']:
            add_menu_item(order)
        elif action in ['remove', 'r']:
            remove_menu_item(order)
        elif action in ['place', 'p']:
            print('Your order:', [x['Code'] for x in order.data['Products']])
            return order

        print('Your order:', [x['Code'] for x in order.data['Products']])

def add_menu_item(order):
    item = click.prompt('Enter item code', type=str)
    if not order.add_item(item):
        click.echo('Item code is invalid.')

def remove_menu_item(order):
    item = click.prompt('Enter item code', type=str)
    try:
        item = order.remove_item(item)
        click.echo('{} was removed.'.format(item['Code']))
    except ValueError:
        click.echo('Item was not in order.')

order_pizza()

from setuptools import setup

setup(
    name='pizzacli',
    version='0.1',
    description='Order pizza from the command line',
    author='Matthew Richardson',
    author_email='matthewmadhavrichardson@gmail.com',
    url='',
    download_url='',
    keywords='pizza',
    py_modules=['pizzacli'],
    install_requires=[
        'Click',
        'requests',
        'tabulate',
        'xmltodict'
    ],
    entry_points='''
        [console_scripts]
        pizza=pizzacli:order_pizza
    '''
)
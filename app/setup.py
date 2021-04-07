from setuptools import setup, find_packages

config = {
    'description': '',
    'author': 'Tomer Raz',
    'author_email': 'qtomerr@gmail.com',
    'version': '1.0',
    'install_requires': [
        'nose==1.3.7',
        'bottle==0.12.19',
        'configparser==3.5.0',
        'six==1.10.0'
    ],
    'packages': find_packages('app'),
    'scripts': [],
    'name': 'scraper-collector',
    'package_dir': {'': 'app'},
    'entry_points': {
        'console_scripts': {
            'scraper-collector = appapi.__init__:main'
        }
    }
}

setup(**config)

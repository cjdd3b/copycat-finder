import sunlight
from sunlight import openstates

sunlight.config.API_KEY = 'd7b45f3b788240acb4ab8c8aa56d7446'


vt_agro_bills = openstates.bills(
    state='ca',
    chamber='lower',
)

for bill in vt_agro_bills:
    a = openstates.bill(bill['id'])
    print a['versions']
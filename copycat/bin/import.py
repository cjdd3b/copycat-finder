import csv, datetime
from apps.bills.models import *


########## HELPER FUNCTIONS ##########

def create_records(records):
    '''
    Helper function to bulk create records.
    '''
    Bill.objects.bulk_create(records)
    return

if __name__ == '__main__':
    raw_data = csv.DictReader(open('../../data/nv_bills.csv', 'rU'), delimiter=',', quotechar='"')
    for row in raw_data:
        state, created = State.objects.get_or_create(name=row['state'])
        if created: state.save()

        session, created = Session.objects.get_or_create(name=row['state'])
        if created: session.save()

        bill, created = Bill.objects.get_or_create(state=state, session=session, bill_id=row['bill_id'], title=row['title'])

        for t in row['type'].split('|'):
            type, created = Type.objects.get_or_create(name=t)
            bill.type.add(type)

        for s in row['subjects'].split('|'):
            subject, created = Subject.objects.get_or_create(name=t)
            bill.subjects.add(subject)

        bill.save()

        
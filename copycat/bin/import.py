import csv, datetime, urllib, urllib2, zipfile
from StringIO import StringIO
from BeautifulSoup import BeautifulSoup
from apps.bills.models import *


########## HELPER FUNCTIONS ##########

def unzip(url):
    '''
    Function to unzip incoming zip files in memory rather than
    processing them on the disk. Helps beacuse the incoming bill
    files are stored as zips.
    '''
    zipdata = StringIO()
    zipdata.write(urllib2.urlopen(url).read())
    myzipfile = zipfile.ZipFile(zipdata)
    for f in myzipfile.filelist:
        if f.filename.find('bills') > -1:
            foofile = myzipfile.open(f.filename)
    return foofile.readlines()


def get_csvs():
    '''
    Gets all the links of state-level bill CSVs from the OpenStates site.
    '''
    html = urllib2.urlopen('http://openstates.org/downloads/').read()
    soup = BeautifulSoup(html)

    download_table = soup.find(id='download_list')
    for td in download_table.findAll('td'):
        if td.find('a'):
            link = td.find('a')['href']
            if link.find('csv') > -1:
                yield link


########## MAIN ##########

if __name__ == '__main__':
    # Go through all the states
    for url in get_csvs():
        print url

        bills = []
        # Create the corresponding bill object in the database
        raw_data = csv.DictReader(unzip(url), delimiter=',', quotechar='"')
        for row in raw_data:
            state, created = State.objects.get_or_create(name=row['state'])
            if created: state.save()

            session, created = Session.objects.get_or_create(name=row['session'])
            if created: session.save()

            # Still need to fill in things like created date and updated date here.
            bill = Bill(state=state, session=session, bill_id=row['bill_id'], title=row['title'])
            bills.append(bill)

        # Bulk create to save time on transactions
        Bill.objects.bulk_create(bills)
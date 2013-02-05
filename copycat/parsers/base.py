import urllib2, re, string
from readability.readability import Document

from HTMLParser import HTMLParser

class MLStripper(HTMLParser):

    def __init__(self):
        self.reset()
        self.fed = []
    
    def handle_data(self, d):
        self.fed.append(d)
    
    def get_data(self):
        return ''.join(self.fed)

def strip_tags(html):
    s = MLStripper()
    s.feed(html)
    return s.get_data()


class BaseBillParser(object):

    def __init__(self, url):
        self.url = url
        self.filetype = self._get_filetype(url)

    def _get_filetype(self, url):
        '''
        Using HTTP HEAD to figure out the filetype on the other end. We'll ultimately
        use this to select the proper parser.
        '''
        request = urllib2.Request(url)
        request.get_method = lambda: 'HEAD'
        response = urllib2.urlopen(request)
        return response.headers['Content-Type']

    def _clean_text(self, text):
        regex = re.compile('[%s]' % re.escape(string.punctuation))
        return ' '.join(regex.sub('', text).split())

    def _parse_pdf(self):
        raise NotImplementedError

    def _parse_html(self, striptags=True):
        html = urllib2.urlopen(self.url).read()
        clean_doc = Document(html).summary()
        s = MLStripper()
        s.feed(clean_doc)
        return self._clean_text(s.get_data())

    def _parse_word(self):
        raise NotImplementedError

    def _get_parser(self):
        if self.filetype.find('html') > -1:
            return self._parse_html()
        return None

    def get_clean_text(self):
        return self._get_parser()


a = BaseBillParser('http://www.malegislature.gov/Bills/BillHtml/119414?generalCourtId=1')
print a.get_clean_text()
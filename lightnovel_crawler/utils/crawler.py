#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Crawler application
"""
import re
from concurrent import futures
from . import cfscrape


class Crawler:
    '''Blueprint for creating new crawlers'''

    home_url = ''
    novel_url = ''
    scrapper = cfscrape.create_scraper()
    executor = futures.ThreadPoolExecutor(max_workers=5)

    '''Must resolve these fields inside `read_novel_info`'''
    novel_title = 'N/A'
    novel_author = 'N/A'
    novel_cover = None

    '''
    Each item must contain these keys:
    `title` - the title of the volume
    '''
    volumes = []

    '''
    Each item must contain these keys:
    `id` - the index of the chapter
    `title` - the title name
    `volume` - the volume id of this chapter
    `url` - the link where to download the chapter
    `name` - the chapter name, e.g: 'Chapter 3' or 'Chapter 12 (Special)'
    '''
    chapters = []

    def __init__(self):
        self.scrapper.verify = False
    # end def

    # ------------------------------------------------------------------------- #
    # Implement these methods
    # ------------------------------------------------------------------------- #

    def initialize(self):
        pass
    # end def

    def dispose(self):
        pass
    # end def

    @property
    def supports_login(self):
        '''Whether the crawler supports login() and logout method'''
        return False
    # end def

    def login(self, email, password):
        pass
    # end def

    def logout(self):
        pass
    # end def

    def read_novel_info(self, url):
        '''Get novel title, autor, cover etc'''
        pass
    # end def

    def download_chapter_list(self):
        '''Download list of chapters and volumes.'''
        pass
    # end def

    def download_chapter_body(self, chapter):
        '''Download body of a single chapter and return as clean html format.'''
        pass
    # end def

    def get_chapter_index_of(self, url):
        '''Return the index of chapter by given url or -1'''
        url = (url or '').strip().strip('/')
        for i, chapter in enumerate(self.chapters):
            if chapter['url'] == url:
                return i
            # end if
        # end for
        return -1
    # end def

    # ------------------------------------------------------------------------- #
    # Helper methods to be used
    # ------------------------------------------------------------------------- #
    @property
    def headers(self):
        return self.scrapper.headers.copy()
    # end def

    @property
    def cookies(self):
        return {x.name: x.value for x in self.scrapper.cookies}
    # end def

    def absolute_url(self, url):
        if not url or len(url) == 0:
            return None
        elif url.startswith('//'):
            return 'http:' + url
        elif url.find('//') >= 0:
            return url
        else:
            return self.home_url + url
        # end if
    # end def

    def get_response(self, url, incognito=False):
        response = self.scrapper.get(url)
        response.encoding = 'utf-8'
        self.cookies.update({
            x.name: x.value
            for x in response.cookies
        })
        return response
    # end def

    def submit_form(self, url, multipart=False, headers={}, **data):
        '''Submit a form using post request'''
        headers = {
            'content-type': 'multipart/form-data' if multipart
            else 'application/x-www-form-urlencoded'
        }
        response = self.scrapper.post(url, data=data, headers=headers)
        self.cookies.update({
            x.name: x.value
            for x in response.cookies
        })
        return response
    # end def

    def download_cover(self, output_file):
        response = self.get_response(self.novel_cover)
        with open(output_file, 'wb') as f:
            f.write(response.content)
        # end with
    # end def

    def extract_contents(self, contents, level=0):
        body = [] 
        for elem in contents:
            if ['script', 'iframe', 'form', 'a', 'br'].count(elem.name):
                pass
            elif ['h3', 'div', 'p'].count(elem.name):
                body += self.extract_contents(elem.contents, level + 1)
            elif not elem.name:
                body.append(str(elem).strip())
            elif ['img'].count(elem.name):
                body.append(str(elem))
            elif elem.text.strip() != '':
                tag = elem.name
                text = '<%s>%s</%s>' % (tag, elem.text, tag)
                body.append(text)
            # end if
        # end for
        if level == 0:
            return [x for x in body if len(x) and self.not_blacklisted(x)]
        else:
            return body
        # end if
    # end def

    blacklist_patterns = [
        r'^(volume|chapter) .?\d+$',
    ]

    def not_blacklisted(self, text):
        for pattern in self.blacklist_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return False
            # end if
        # end for
        return True
    # end def
# end class
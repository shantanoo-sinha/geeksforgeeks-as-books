import glob
from subprocess import call

#!/usr/bin/env python
import sys
import logging
import codecs
import os

from optparse import OptionParser
import HTMLParser
import requests
import lxml.html as html
import lxml.etree
from boilerpipy import (Extractor, isvalidhtml)


def insert_content(doc, html_doc, insert_string, insert_type):
    to_insert = html_doc.find('.//'+insert_type)
    doc.append(to_insert)
    return doc

def clean(file_name, debug=False, directory="."):

    loglevel = logging.INFO
    if debug:
        loglevel = logging.DEBUG
    content = codecs.open(file_name, "r", "utf-8").read()
    article = Extractor(content, loglevel=loglevel).extracted()
    if article is None:
        print "Error processing html file"
        sys.exit(1)
    html_parser = html.HTMLParser(encoding="utf-8")
    html_doc = html.fromstring(content, parser=html_parser)
    head_doc = html_doc.find('head')
    source_url = head_doc.cssselect('meta[property="og:url"]')[0].get('content')

    """
    style_string = "<link rel='stylesheet' type='text/css' href='buttondown.css'>"
    publish_date = head_doc.cssselect('meta[property="article:published_time"]')[0].get('content')[:10]
    publish_date_string = "<meta name='date' " + "content=" + publish_date + " scheme='YYYY-MM-DD'>"
    author_string = "<meta name='author' content='Geeksforgeeks'>"
    head_doc = insert_content(head_doc, author_string, 'meta')
    head_doc = insert_content(head_doc, publish_date_string, 'meta')
    head_doc = insert_content(head_doc, style_string, 'link')
    title_doc = head_doc.find(".//title")
    """
    reconstructed_body = "<html><body>" + article.encode('utf-8') + "</body></html>"
    source_header_string = "<h3>Source:</h3>"
    source_link = "<p><a href='" + source_url +"' rel='tag'>" + source_url + "</a></p>"
    # further remove useless stuff
    body_doc = html.fromstring(reconstructed_body).find('body')
    for bad in body_doc.xpath("//div[@class='comments-main']"):
        bad.getparent().remove(bad)
    for ad_by_google in body_doc.xpath("//ins[@class='adsbygoogle']"):
        ad_by_google.getparent().remove(ad_by_google)
    for bad_h3 in body_doc.xpath("//h3"):
        bad_h3.getparent().remove(bad_h3)

    post_content_doc = body_doc.xpath("//div[@class='post-content']")[0]
    post_content_doc.append(lxml.etree.XML(source_header_string))
    post_content_doc.append(lxml.etree.XML(source_link))
    basename = os.path.basename(file_name)
    cleaned_file = os.path.splitext(basename)[0] + "_cleaned.html"
    #out = html.tostring(head_doc) + html.tostring(body_doc)
    result = html.tostring(body_doc)
    with codecs.open(cleaned_file, 'w', 'utf-8') as cleaned_file_handle:
        cleaned_file_handle.write(result)

def clean_html_files():
    for html_file in glob.glob('*.html'):
        if 'clean' not in html_file:
            clean(html_file)

if __name__ == "__main__":
    clean_html_files()

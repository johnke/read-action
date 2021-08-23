#!/usr/bin/env python3

import os
import requests
import json
import sys
import datetime
from lxml import html
from slugify import slugify
from bs4 import BeautifulSoup


scriptdir = os.path.dirname(__file__)


def get_parsed_page(url):
  """
  Return the content of the website on the given url in
  a parsed lxml format that is easy to query.
  """
  response = requests.get(url, headers={"User-Agent": "Only slightly defined"})
  parsed_page = BeautifulSoup(response.text, 'html.parser')
  return parsed_page


def parse_parsed_page(parsed_page, url, book_date, book_rating):
  book = {}
  book['url'] = url
  book['title'] = parsed_page.find(id="productTitle").text.strip()
  book['author'] = parsed_page.find(class_="author notFaded").span.text.split("\n")[0]
  if book['author'] == "":
    book['author'] = parsed_page.find(class_="author notFaded").a.text

  images = json.loads(parsed_page.find(
    "img", class_="frontImage")['data-a-dynamic-image'])
  book['image'] = list(images.keys())[0]
  book['date'] = book_date
  if book_rating:
    book['rating_string'] = "  rating: \"{}\"".format("★" * book_rating)
  else:
    book['rating_string'] = ""
  return book


def format_book(book, body=None):
  if body is None:
    book['body'] = ""
  else:
    book['body'] = body
  formatted_book = """---
date: "{date}"
title: "{title}"
extra:
  author: "{author}"
  image: "{image}"
  link: "{url}"
{rating_string}

---

{body}
""".format_map(book)
  return formatted_book


def write_file(book):
  formatted_book = format_book(book)
  slugified_title = slugify(book['title'])
  slugified_author = slugify(book['author'])
  book_filename = os.path.join(scriptdir, "test-{}-{}.md".format(slugified_title, slugified_author))

  f = open(book_filename, 'w')
  f.write(formatted_book)
  f.close()


if __name__ == "__main__":
  if "GITHUB_ACTIONS" in os.environ:
    if "AMAZON_LOOKUP_ISSUE_TITLE" in os.environ:
      title_split = os.environ.get("AMAZON_LOOKUP_ISSUE_TITLE").split()
      url = title_split[0]
      if len(title_split) >= 2:
        book_rating = int(title_split[1])
      if len(title_split) == 3:
        book_date = title_split[2]
      else:
        book_date = str(datetime.date.today())

    if "AMAZON_LOOKUP_ISSUE_BODY" in os.environ:
      book_body = os.environ.get("AMAZON_LOOKUP_ISSUE_BODY")

  else:
    book_body = None
    if len(sys.argv) == 1:
      print("You need to give me a URL to parse")
      sys.exit(1)
    else:
      url = sys.argv[1]

    book_rating = None
    if len(sys.argv) == 3:
      book_rating = int(sys.argv[2])

    if len(sys.argv) == 4:
      book_date = sys.argv[3]
    else:
      book_date = str(datetime.date.today())

  parsed_page = get_parsed_page(url)
  book = parse_parsed_page(parsed_page, url, book_date, book_rating)
  write_file(book, book_body)
  print("::set-output name=book_title::{}".format(book['title']))
  print("::set-output name=book_date::{}".format(book['date']))

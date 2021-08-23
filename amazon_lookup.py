#!/usr/bin/env python3

import os
import requests
import json
import sys
import datetime
from slugify import slugify
import isbnlib


scriptdir = os.path.dirname(__file__)


def lookup_isbn(isbn, rating_string, date, body):
  book_info = isbnlib.meta(isbn, service="goob")
  book_info['url'] = "https://www.amazon.co.uk/dp/" + isbn
  book_info['image'] = isbnlib.cover(isbn)['thumbnail']
  book_info['rating_string'] = rating_string
  book_info['authors'] = ", ".join(book_info['Authors'])
  book_info['date'] = date
  if body is None:
    book_info['body'] = ''
  else:
    book_info['body'] = body
  return book_info


def format_book(book):
  formatted_book = """---
date: "{date}"
title: "{Title}"
extra:
  author: "{authors}"
  image: "{image}"
  link: "{url}"
{rating_string}

---

{body}
""".format_map(book)
  return formatted_book


def write_file(book):
  formatted_book = format_book(book)
  slugified_title = slugify(book['Title'])
  slugified_author = slugify(book['authors'])
  # book_filename = os.path.join(scriptdir, "test-{}-{}.md".format(slugified_title, slugified_author))
  book_filename = os.path.join(
      "/github/workspace/content/reading", "test-{}-{}.md".format(slugified_title, slugified_author))

  f = open(book_filename, 'w')
  f.write(formatted_book)
  f.close()


if __name__ == "__main__":
  if "GITHUB_ACTIONS" in os.environ:
    title_split = sys.argv[1].split()
    isbn = title_split[0]

    if len(title_split) >= 2:
      rating_string = "  rating: \"{}\"".format("★" * int(title_split[1]))
    else:
      rating_string = ""
    if len(title_split) == 3:
      book_date = title_split[2]
    else:
      book_date = str(datetime.date.today())

    if len(sys.argv) == 3:
      book_body = sys.argv[2]

  else:
    book_body = None
    if len(sys.argv) == 1:
      print("You need to give me an ISBN to parse")
      sys.exit(1)
    else:
      isbn = sys.argv[1]

    book_rating = None
    if len(sys.argv) == 3:
      book_rating = int(sys.argv[2])

    if len(sys.argv) == 4:
      book_date = sys.argv[3]
    else:
      book_date = str(datetime.date.today())

  book_info = lookup_isbn(isbn, rating_string, book_date, book_body)
  write_file(book_info)
  print("::set-output name=book_title::{}".format(book['title']))
  print("::set-output name=book_date::{}".format(book['date']))

import unittest
import os
from httmock import all_requests, HTTMock
import requests
import amazon_lookup


@all_requests
def response_content(url, request):
  current_dir = os.path.abspath(os.path.dirname(__file__))
  mock_filename = os.path.join(current_dir, 'mock_response.html')
  with open(mock_filename, "rb") as f:
    content = f.read().decode("utf-8")
  return {'status_code': 200, 'content': content}


class MockTest(unittest.TestCase):

  with HTTMock(response_content):
    test_url = "http://foo_bar"
    bs_mock = amazon_lookup.get_parsed_page(test_url)
    parsed_mock = amazon_lookup.parse_parsed_page(bs_mock, test_url, "2021-08-23", 5)
    output_format = amazon_lookup.format_book(parsed_mock, "test body")
    output_format_empty_body = amazon_lookup.format_book(parsed_mock, None)

  def test_200_response(self):
    with HTTMock(response_content):
      r = requests.get('https://foo_bar')
    self.assertEqual(r.status_code, 200)

  def test_text_response(self):
    self.assertIn("Neil Gaiman", str(self.bs_mock))

  def test_parsed_page(self):
    self.assertEqual(self.parsed_mock, {'url': 'http://foo_bar', 'body': '', 'title': 'The Sandman Volume 1: 30th Anniversary Edition: Preludes and Nocturnes', 'author': 'Neil Gaiman', 'image': 'https://images-na.ssl-images-amazon.com/images/I/51bpOmzgv5L._SX321_BO1,204,203,200_.jpg', 'date': '2021-08-23', 'rating_string': '  rating: "★★★★★"'})

  def test_output_format(self):
    f = """---
date: "2021-08-23"
title: "The Sandman Volume 1: 30th Anniversary Edition: Preludes and Nocturnes"
extra:
  author: "Neil Gaiman"
  image: "https://images-na.ssl-images-amazon.com/images/I/51bpOmzgv5L._SX321_BO1,204,203,200_.jpg"
  link: "http://foo_bar"
  rating: "★★★★★"

---

test body
"""
    self.assertEqual(self.output_format, f)

  def test_output_format_empty_body(self):
    f = """---
date: "2021-08-23"
title: "The Sandman Volume 1: 30th Anniversary Edition: Preludes and Nocturnes"
extra:
  author: "Neil Gaiman"
  image: "https://images-na.ssl-images-amazon.com/images/I/51bpOmzgv5L._SX321_BO1,204,203,200_.jpg"
  link: "http://foo_bar"
  rating: "★★★★★"

---


"""
    self.assertEqual(self.output_format_empty_body, f)

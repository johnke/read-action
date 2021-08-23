FROM alpine:3.14
RUN apk update && apk upgrade && \
  apk add --no-cache python3-dev py3-pip && \
  pip install --upgrade pip python-slugify httmock isbnlib

COPY amazon_lookup.py /
COPY tests/ tests/

RUN python3 -m unittest

# ENTRYPOINT [ "/bin/bash", "-c"]
# CMD ["/bin/bash"]
ENTRYPOINT ["/amazon_lookup.py"]

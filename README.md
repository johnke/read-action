# read-action

This GitHub action tracks the books that you've read by creating a `.md` file in your repository. This is heavily based on [Katy Decorah's read-action](https://github.com/katydecorah/read-action)

Create an issue with the book's amazon link. The action fetches the product's data and adds a `.md` file under `content/reading` (I'm using Hugo to track this!) under your repository.

## Setup

Create .github/workflows/read.yml file using the following template:

on:
  issues:
    types: opened

jobs:
  update_library:
    runs-on: macOS-latest
    name: Read
    # only continue if issue has "read" label
    if: contains( github.event.issue.labels.*.name, 'read')
    steps:
      - name: Checkout
        uses: actions/checkout@v2
      - name: Read
        uses: johnke/read-action@1.0.0
      - name: Commit files
        run: |
          git config --local user.email "action@github.com"
          git config --local user.name "GitHub Action"
          git add -A && git commit -m "Updated _data/read.yml"
          git push "https://${GITHUB_ACTOR}:${{secrets.GITHUB_TOKEN}}@github.com/${GITHUB_REPOSITORY}.git" HEAD:${GITHUB_REF}
      - name: Close issue
        uses: peter-evans/close-issue@v1
        with:
          issue-number: "${{ env.IssueNumber }}"
          comment: "📚 You read ${{ env.BookTitle }} on ${{env.DateRead}}."

## Options

    readFileName: The file where you want to save your books. Default: _data/read.yml.
    providers: Specify the ISBN providers that you want to use, in the order you need them to be invoked. If setting more than one provider, separate each with a comma.


# Creating an issue

The title of your issue must start with the Amazon URL of the book, followed by a numerical score from 1-5:

https://www.amazon.co.uk/Sandman-30th-Anniversary-Preludes-Nocturnes/dp/1401284779/ 4

The action will automatically set the date that you finished the book (dateFinished) to today. To specify a different date that you finished the book, add the date after the score in YYYYMMDD format.

https://www.amazon.co.uk/Sandman-30th-Anniversary-Preludes-Nocturnes/dp/1401284779/ 4 20210823

If you add content to the body of the comment, the action will add it as the body of the markdown.

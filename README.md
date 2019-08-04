# QuizBot
Answer Bot for games like HQ Trivia &amp; Loco (old project)

#### This script may not work now. I developed this for educational purposes in Jan 2018.

## Highlights
- Utilized OCR Technology to read questions and options from the Game screen.
- Removed common irrelevant words from the question and made a google search for the keywords using requests module and extracted the search results using BeautifulSoup.
- The results were matched with all the 3 options and the most matched option was shown as the answer.
- Later, improved the question fetching process, by using Socket Programming and getting questions directly from the host.
- The complete code was written in Python.

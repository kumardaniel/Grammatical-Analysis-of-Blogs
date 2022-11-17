import requests
from bs4 import BeautifulSoup
import pandas as pd
import re

class TextExtractorObject():
    def __init__(self):
        self.headers = {
            'User-Agent': 'Chrome/42.0.2311.135 Safari/537.36 Edge/12.246',
        }
    def get_text(self, url_:str):
        html_text = requests.get(url= url_, headers = self.headers).text
        soup = BeautifulSoup(html_text, 'lxml')
        TITLE = soup.find('title').text + '\n'
        TITLE = re.sub(' - Blackcoffer Insights', "", TITLE)
        paragraphs = (soup.find('div', class_ = 'td-post-content')).find_all('p')
        CONTENT = ""
        for para in paragraphs:
            if(para.find('strong') is not None):
                CONTENT += "<head>"
                CONTENT += para.text
                CONTENT += "<\head>\n"
                continue
            CONTENT += para.text
            CONTENT += ' <para_end>\n'
        return {
            'Title': TITLE,
            'Content': CONTENT
        }
    def write_to_file(self, url, urlId):
        try:
            extracted_text = self.get_text(url)
            success_ = True
            with open(f"./Extracted Text/{urlId}.txt", "w") as f:
                f.write(extracted_text['Title'])
                f.write(extracted_text['Content'])
                f.close()
        except:
            print(f"Could Not retrieve text for URL_ID-{urlId}, URL- {url}\n")
            success_ = False
        return success_

# def main():
#     urls = pd.read_excel(r'.\Input Data\Input.xlsx', dtype={'URL': str, 'URL_ID': int})
#     urls.set_index('URL_ID', inplace = True)

#     extractor = TextExtractorObject()

#     retrieved = []
#     failed = []
#     for url_id in urls.index:
#         print(url_id, "----", urls.loc[url_id][0])
#         _ = extractor.write_to_file(urls.loc[url_id][0], url_id)
#         if _:
#             retrieved.append(url_id)
#         else:
#             failed.append(url_id)
#     print(retrieved, failed, sep = "\n")

# if __name__ == "__main__":
#     main()

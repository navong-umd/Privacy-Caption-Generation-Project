#Install dependencies
#pip install beautifulsoup4 requests

#import library of BeautifulSoup Retreive Official API Description
import requests
from bs4 import BeautifulSoup
from urllib.parse import quote
import re
from tabulate import tabulate

def get_android_doc_description(class_name, method_name):
    class_path = class_name.split('$')[0].replace('.', '/')
    base_url = f'https://developer.android.com/reference/{quote(class_path)}'
    #print("base_url:", base_url)

    try:
        res = requests.get(base_url, timeout=10)
        if res.status_code != 200:
            return "Documentation not found."

        soup = BeautifulSoup(res.text, 'html.parser')

        # First try: find an <a> whose id is the method name with "()" appended.
        anchor_id = f"{method_name}()"
        method_anchor = soup.find('a', id=anchor_id)
        if method_anchor:
            method_header = method_anchor.find_parent(lambda tag: tag.name in ['h2', 'h3', 'h4'])
        else:
            # Fallback: search for a header containing the method name text
            headers = soup.find_all(['h2','h3','h4'])
            method_header = None
            for h in headers:
                if method_name.lower() in h.get_text(strip=True).lower():
                    method_header = h
                    break

        if not method_header:
            return "Method description not found."

        # Gather all paragraphs that follow the header and occur before the next header.
        paragraphs = []
        for p in method_header.find_all_next('p'):
            # Check if the previous header (h2/h3/h4) of this paragraph is the same as method_header.
            prev_header = p.find_previous(lambda tag: tag.name in ['h2','h3','h4'])
            if prev_header and prev_header == method_header:
                paragraphs.append(p)
            else:
                break  # We've left the current method section

        def extract_first_sentence(text):
            # Try to capture a sentence ending with . ! or ?
            match = re.search(r'([A-Z][^.!?]*[.!?])', text)
            if match:
                return match.group(1).strip()
            return text.strip()

        def classify_paragraph(p):
            if not p or p.name != 'p':
                return 'skip'
            text = p.get_text(strip=True)
            lower_text = text.lower()
            # Skip paragraphs that start with "Note:" or "Note" or contain a caution indicator
            if p.get('class') and 'caution' in p.get('class'):
                return 'skip'
            if lower_text.startswith('note:') or lower_text.startswith('note'):
                return 'skip'
            # If the paragraph begins with a deprecation message, mark it as "deprecated"
            if lower_text.startswith('this method was deprecated') or lower_text.startswith('deprecated'):
                return 'deprecated'
            if not text:
                return 'skip'
            return 'valid'

        valid_para = None
        deprecated_para = None

        # Look over all paragraphs in this section.
        for p in paragraphs:
            cls = classify_paragraph(p)
            if cls == 'valid' and valid_para is None:
                valid_para = p
            elif cls == 'deprecated' and deprecated_para is None:
                deprecated_para = p

        if valid_para:
            return extract_first_sentence(valid_para.get_text(strip=True))
        elif deprecated_para:
            return extract_first_sentence(deprecated_para.get_text(strip=True))
        else:
            return "Method description not found."

    except Exception as e:
        return f"Error: {str(e)}"


import requests
import json
from bs4 import BeautifulSoup
import re
import pandas as pd
import os
import downloader

class analyzer:
    def __init__(self, key, model, ticker):
        self.key = key
        self.url = "https://api.awanllm.com/v1/chat/completions"
        self.model = model
        self.ticker = ticker
        downloader.download_10K(ticker)
        years = self.get_available_years()
        self.df = {}
        for year in years:
            df = self.extract_sections(year)
            self.df[year] = df

    def get_available_years(self):
        base_path = "sec-edgar-filings"
        ticker_path = os.path.join(base_path, self.ticker, "10-K")
        years = []
        for folder_name in os.listdir(ticker_path):
            parts = folder_name.split("-")
            if len(parts) >= 2 and parts[1].isdigit():
                year = int(parts[1])
                if year < 50:
                    year += 2000
                else:
                    year += 1900
                years.append(year)
        return sorted(years)
    
    # get the disiring information
    def get_message(self, prompt):
        payload = json.dumps({
            "model": self.model,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        })
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f"Bearer {self.key}"
        }
        response = requests.request("POST", self.url, headers=headers, data=payload)
        result = response.json()
        if 'choices' in result and len(result['choices']) > 0:
            message = result['choices'][0]['message']
            return message.get('content', 'No response')
        else:
            print('No response')
            return "No response"
    
    def extract_sections(self, year):
        with open(self.find_10k_path(year), "r", encoding="utf-8") as file:
            content = file.read()
        regex = re.compile(r'(>Item(\s|&#160;|&nbsp;)(1A|1B|7A|7|8|9)\.{0,1})|(ITEM\s(1A|1B|7A|7|8|9))')
        matches = list(regex.finditer(content))
        sections = [(match.group(), match.start()) for match in matches]

        df = pd.DataFrame(sections, columns=["Item", "Start"])
        df["End"] = df["Start"].shift(-1, fill_value=len(content))
        df["Item"] = df["Item"].apply(lambda x: re.sub(r'(>|&nbsp;|\s|&#160;|\.|ITEM)', '', x).upper())
        df["Item"] = df["Item"].apply(lambda x: x)

        unique_items = df["Item"].unique()
        final_sections = []
        for item in unique_items:
            latest_match = df[df["Item"] == item].iloc[-1]
            final_sections.append(latest_match)

        result_df = pd.DataFrame(final_sections)
        return result_df.reset_index(drop=True)
    
    def get_item_text(self, section, year):
        df = self.df[year]
        if df.empty:
            return
        with open(self.find_10k_path(year), "r", encoding="utf-8") as file:
            content = file.read()
        content = content[df[df['Item'] == 'ITEM1A']['Start'].iloc[0]:df[df['Item'] == 'ITEM1A']['End'].iloc[0]]
        content = BeautifulSoup(content, features="html.parser")
        content = content.get_text("\n\n")
        content = re.sub(r'\s+', ' ', content).strip()
        # Clean up the text using split and join
        content = ' '.join(content.split())
        return content
    
    def analyze_1(self):
        # given the dataframe of text, return the analysis of first part
        max_token_length = 30000
        text = self.get_item_text('ITEM1A.', 2022)
        chunks = [text[i:i + max_token_length] for i in range(0, len(text), max_token_length)]
        summary_placeholder = "give a brief summary of that company {self.ticker}'s main business, and its current risk, challenges, write unknown if u can't infer from text."
        summarization = ""
        # Feed chunks to the model
        for chunk in chunks:
            prompt = f"Here is portion of the text:\n\n{chunk}\n\n{summary_placeholder}"
            summarization += self.get_message(prompt)
        
        # Final prompt for summary
        final_prompt = f"Now you finished reading each portion of text, and that's your partial answers {summarization}, please give a brief summary of that company's main business, and its current risk, challenges"
        return self.get_message(final_prompt)

    
    def analyze_7(self, df):
        
        return
    
    def find_10k_path(self, year):
        base_path = "sec-edgar-filings"
        ticker_path = os.path.join(base_path, self.ticker, "10-K")
        pattern = re.compile(r"(\d+)-(\d{2})-\d+")
        for folder_name in os.listdir(ticker_path):
            match = pattern.match(folder_name)
            if match and int(match.group(2)) == year % 100: 
                return os.path.join(ticker_path, folder_name, "full-submission.txt")
        return None


def main():
    a = analyzer("d9afe4b3-bb3f-46b0-b37b-373cae94aba8", "Meta-Llama-3-8B-Instruct", "MSFT")
    print(a.analyze_1())

    

if __name__ == '__main__':
    main()
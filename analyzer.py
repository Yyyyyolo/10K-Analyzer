import requests
import json
from bs4 import BeautifulSoup
import re
import pandas as pd
import os
import downloader
import time

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

        regex = re.compile(r'(>Item(\s|&#160;|&nbsp;)(1A|1B|7A|7|8)\.{0,1})|(ITEM\s(1A|1B|7A|7|8))')
        matches = list(regex.finditer(content))
        sections = [(match.group(), match.start()) for match in matches]

        df = pd.DataFrame(sections, columns=["Item", "Start"])
        df["Item"] = df["Item"].apply(lambda x: re.sub(r'(>|&nbsp;|\s|&#160;|\.|ITEM)', '', x).upper())

        # Remove "ITEM" and normalize
        df["Item"] = df["Item"].str.replace("ITEM", "")

        final_sections = []
        unique_items = df["Item"].unique()

        for item in unique_items:
            item_df = df[df["Item"] == item]
            if len(item_df) > 1:
                # Step 1: Remove the first occurrence
                item_df = item_df.iloc[1:]
                # Step 2: Keep the first occurrence of the remaining items
                final_sections.append(item_df.iloc[0])
            else:
                final_sections.append(item_df.iloc[0])

        result_df = pd.DataFrame(final_sections, columns=["Item", "Start"])
        result_df["End"] = result_df["Start"].shift(-1, fill_value=len(content))
        
        return result_df
    
    def get_item_text(self, section, year):
        df = self.df[year]
        if df.empty:
            return
        with open(self.find_10k_path(year), "r", encoding="utf-8") as file:
            content = file.read()
        content = content[df[df['Item'] == section]['Start'].iloc[0]:df[df['Item'] == section]['End'].iloc[0]]
        content = BeautifulSoup(content, features="html.parser")
        content = content.get_text("\n\n")
        content = re.sub(r'\s+', ' ', content).strip()
        # Clean up the text using split and join
        content = ' '.join(content.split())
        return content
    
    def analyze_1(self):
        # given the dataframe of text, return the analysis of first part
        max_token_length = 30000
        text = self.get_item_text('1A', 2022)
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

    
    def analyze_GI(self):
        recent_years = sorted(self.df.keys(), reverse=True)[:5]
        free_cash_flows = []
        max_token_length = 30000
        count = 0
        for _, year in enumerate(recent_years):
            df = self.df[year]
            if df.empty:
                free_cash_flows.append(0)
                continue

            text = self.get_item_text('7', year)
            if not text:
                free_cash_flows.append(0)
                continue
            chunks = [text[i:i + max_token_length] for i in range(0, len(text), max_token_length)]
            summarization = ""

            for chunk in chunks:
                prompt = f"Here is portion of the text:\n\n{chunk}\n\nPlease extract the EBIT for the year {year}, if u can't infer from the text, just say nothing."
                summarization += self.get_message(prompt)
                count += 1
                if count % 10 == 9:  # After 10 requests, take a rest for a minute
                    time.sleep(60)
            
            final_prompt = f"Now you finished reading each portion of text, and that's your partial answers {summarization}, please give me the EBIT of that company at that year, I want u to give a single pure int, no more words, no unit, and return 0 if u don't know, DONT SAY ANYTHING"
            print(final_prompt)
            free_cash_flows.append(int(self.get_message(final_prompt)))

        return free_cash_flows
    
    def analyze_income(self):
        # given the dataframe of text, return the analysis of first part
        max_token_length = 30000
        text = self.get_item_text('7', 2022)
        chunks = [text[i:i + max_token_length] for i in range(0, len(text), max_token_length)]
        summary_placeholder = "find {self.ticker}'s products, and return a dictionary that key is the product, and value is the net sale of that product, also include a total earning/sale in the dict with key named total(you should always make sure that sum of all earning/sales equals to total, no negative numbers), and no more words, don't return if u don't found"
        summarization = ""
        # Feed chunks to the model
        for chunk in chunks:
            prompt = f"Here is portion of the text:\n\n{chunk}\n\n{summary_placeholder}"
            summarization += self.get_message(prompt)
        
        # Final prompt for summary
        final_prompt = f"Now you finished reading each portion of text, and that's your partial answers {summarization}, please give a final dictionary that key is the product, and value is the net sale/earning from that source, also include a total earning/sale in the dict with key named total(you should make sure that sum of all earning/sales equals to total sale, no negative numbers). Just return those and no more explanation."
        return self.get_message(final_prompt)

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
    a = analyzer("d9afe4b3-bb3f-46b0-b37b-373cae94aba8", "Meta-Llama-3-8B-Instruct", "TSLA")
    print(a.analyze_GI())


    

if __name__ == '__main__':
    main()
# 10K Analyzer Overview
For this project, I used LLMA from Awan LLM to analyze the 10-K files for a given ticker and generate some insights and graphs. 
## Run
install neccessary libaries and cd to directory and enter "py gui.py", or enter the dist folder, click the gui.exe file.
# Tech Stack
I use a tech stack which python as the backend, python tkinter for UI design, not that complicated. It could run locally after installing neccessary libraries, but not able to run remotely. Reasons using this: mainly because I'm familiar with them and don't require much self-learning, and it only use one single programming language which make it much easier to write.<br>
I konw probably deploy on platform like heroku, google cloud, which make it a web app, should be better, but I really don't got much time for this in these days.
# Insight choice
Before digging into why we looking for specific insights, we should first know what we are looking for, and what task are we doing. In a research setting, I would assume that we want look for some correlation of certain stats and stock price. In a work setting, I would assume we are looking for some important information of a company that help our decision on buying, selling stock, etc.<br>
PS: It's worth noting that since most LLM are paid service, I found a free one but with limited access(10 requests per min, and maximum 30k token per request), that would stop me from digging a lots complicated insights, since most would require it to read large amount of text in short time. Thus, I mainly looking for some simple and naive insight.
## Item 1A
I think Item 1A is the first part that would be considered important, as it includes some basic information of that company, along with some potential risks and challenges. Thus, I use LLM to read that part of recent 10-K files, and give a brief summary. It would be a good start for a person who don't really know it, and start getting familiar with that company through this introduction.
## Item 7
Item 7 includes large amount of financial data, which is important in both work setting and research setting. In particular, I want look at two specific points:
### trend
we want to see whether it's going worse, or going better. Specifically, we want look at its free cash flow trend in recent years using a bar chart, which could reflect a lot about it's current trend.
### Income composition
We also want to know what it profits from. Like for the APPL, is it mainly earn from Iphone or Macbook, we would want a pie chart to see this closely.
### PE ratio compared to others
# Demo
I dont got the time to finish all, and the LLM used is too bad, so demo for some basic function: [Link to Demo](https://youtu.be/UVpf-Za8BAY).



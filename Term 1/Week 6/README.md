# Term 1 - Week 6: Language Models

---

## 1. Homework & workshop assignments -> [`homework/`](homework/)

**What was the assignment?**

**What did I hand in?**
_List the files, or link to them. Notebook exports, screenshots, scripts._

**What did I find difficult, and how did I solve it?**

### Checklist
- [ ] My workshop / homework files are in `homework/`
- [ ] Everything runs without errors, or I explained what does not and why

---


## 2. Hackathon prototype -> [`hackathon/`](hackathon/)

> Your tool and your SDG for this hackathon are announced at the **start of Friday's class**.
> Write them down here once you know them.

**Project title:**
SolarMood: Solar Energy News Sentiment Dashboard

**My pair partner:**
Milou van Leuven

**Tool we had to use:**


**SDG we had to address:**
9: Industry, Innovation and Infrastructure

**What problem does it solve, and for whom?**
_The solar energy industry is growing rapidly, making it increasingly important for companies to monitor technological developments, government policies, investments and market changes. According to IRENA (2025), global solar energy capacity grew by 32.2% in 2024, adding approximately 452 GW. Furthermore, the International Energy Agency (2026) reported that solar PV accounted for more than 75% of global renewable capacity additions in 2025.

Our specific target user is a market intelligence analyst working at a solar panel manufacturing company. This professional needs to monitor industry news to identify emerging technologies, policy changes, investment developments and potential market risks.

The problem is that relevant information is spread across many news sources, making it time-consuming to monitor developments and identify changes in news sentiment. Manually reading hundreds of headlines is inefficient and makes it harder to notice patterns over time.

SolarMood addresses this problem by automatically collecting solar energy news every 30 minutes and analysing headlines with a pretrained Hugging Face sentiment model. The results are displayed in an interactive Streamlit dashboard, allowing the analyst to monitor sentiment trends, filter articles and investigate unusual changes.

Our prototype has already collected more than 773 news articles, demonstrating the amount of information that can be gathered and organised automatically.

SolarMood supports SDG 9 by applying AI-driven innovation to information monitoring within the renewable energy industry. However, it measures the tone of news headlines rather than the actual economic or environmental impact of developments.

Sources:

IRENA (2025). Renewables in 2024: 5 Key Facts Behind a Record-Breaking Year. https://www.irena.org/News/articles/2025/Apr/Renewables-in-2024-5-Key-Facts-Behind-a-Record-Breaking-Year

IEA (2026). Global Energy Review 2026 – Solar PV and Wind. https://www.iea.org/reports/global-energy-review-2026/technology-solar-pv-and-wind_

**What did you build?**
_We built SolarMood, an AI-powered news monitoring application.

The project consists of several parts:

1. Collecting news articles

We created a Python script called collector.py that collects solar energy news headlines from Google News RSS feeds.

The script searches for articles using keywords related to solar energy and retrieves information such as the title, publication date and article link.

It also checks for duplicates to avoid collecting the same headlines multiple times.

2. Analysing the headlines with AI

We used a pretrained Hugging Face RoBERTa model to analyse the sentiment of each headline.

The model predicts three possible categories:

Positive

Neutral

Negative

It also provides a confidence score for each prediction.

We did not train the model ourselves. Instead, we used an existing model and connected it to our Python code.

3. Saving the results

The collected articles and AI predictions are stored in solarmood.csv.

This file contains the data used for the dashboard and further analysis.

4. Automatic data collection

At first, we had to run the collector manually.

I worked on automating this process by creating auto_collect.py, which uses a loop to run collector.py every 30 minutes.

I left my MacBook running overnight so the program could continue collecting new articles automatically.

We also experimented with GitHub Actions to automate the process through GitHub, although we initially experienced problems getting it to work.

5. Creating the dashboard

We used Streamlit to create a dashboard that visualises the results.
The dashboard allows users to:

See the total number of collected articles.

View the distribution of positive, neutral and negative headlines.

Explore how sentiment changes over time.

Filter and inspect individual articles.

6. Evaluating the AI models

To investigate how reliable the sentiment predictions were, we manually labelled 50 news headlines.

Milou compared these human labels with two different sentiment analysis methods:

Method

Matching labels

Agreement

RoBERTa

21/50

42%

VADER

19/50

38%

RoBERTa had slightly higher agreement with our human labels than VADER.

However, we discovered that our human evaluations sometimes considered whether a development was good or bad for the solar energy industry, while the AI models mainly analysed the sentiment of the words in the headline.

For example, a headline about a new solar power plant could be considered positive by us, while the AI classifies it as neutral because the wording is factual.

This showed us that the models and our human evaluations were not always measuring exactly the same thing.
_

**Link to the live thing (if any):**
_https://solarmood-milou-jkelt2tjctww4cb8fjsbri.streamlit.app/_

**How do I run it?**
_The easiest way to view SolarMood is through the live Streamlit dashboard linked above.

To run the project locally:

Download or clone the SolarMood project from GitHub.

Open the project folder in VS Code.

Make sure Python is installed.

Open the terminal in VS Code.

Install the required libraries:

python -m pip install -r requirements.txt

Start the Streamlit dashboard:

python -m streamlit run dashboard.py

Open the local URL shown in the terminal.

To collect and analyse new articles manually, run:

python collector.py

To start the automatic collection every 30 minutes, run:

python auto_collect.py

The automatic collection continues while the script is running and the computer stays awake.

The first time the collector runs, it may take longer because the pretrained Hugging Face model needs to be downloaded._

**Who did what?**
_My contribution: Meggie

I mainly focused on getting the automatic news collection working, collecting the larger dataset and making the results available through GitHub and Streamlit.

At first, we collected articles manually. I wanted the program to continue collecting data without having to start it every time.

I worked on auto_collect.py, a Python script that automatically runs our collector every 30 minutes. I tested the script in VS Code and kept my MacBook running overnight to collect more data.

This allowed us to collect 815 news articles, which was more than the required minimum of 300.

I also worked on uploading the code and dataset to GitHub. This was challenging because I experienced problems with Git commands and merging the local project with the existing GitHub repository.

After solving these issues, I successfully uploaded the collected data and made it available for our Streamlit dashboard.

I also worked on making the dashboard accessible online and documenting how the different parts of our code work together.

Milou's contribution:

Milou mainly focused on evaluating the AI predictions and comparing different sentiment analysis methods.

She created Python scripts to compare our 50 manually labelled headlines with the RoBERTa model and the VADER method.

She calculated the agreement percentages, created confusion matrices and investigated examples where the AI predictions differed from our human labels.

She also tested the Python environment, worked on the Streamlit dashboard and helped document the project.

We both contributed to developing and improving SolarMood, but focused on different parts of the project._

**Ethical reflection - what are the risks of your tool? Who could it harm?**
_Although SolarMood provides a useful overview of solar energy news, it has several important limitations.

Risk 1 – Incorrect classifications
Our evaluation showed that RoBERTa agreed with the human labels in only 42% of the evaluated headlines.
This does not necessarily mean the model is incorrect in all other cases, because the human labels partly measured sector impact rather than linguistic sentiment.
However, it shows that the results need careful interpretation.
Who could be harmed? Market analysts and companies could make poor decisions if they mistake automated sentiment classifications for reliable assessments of industry developments.
Mitigation: We should clearly explain what the model measures, provide access to the underlying headlines and encourage human review before important decisions are made.

Risk 2 – Data and geographical bias
Our Google News searches use English-language settings and may overrepresent certain countries, publishers and topics.
As a result, the collected news may not represent the global solar energy industry equally.
Who could be harmed? Companies operating in underrepresented regions could receive an incomplete picture of developments relevant to their markets.
Mitigation: We should disclose the data source and language settings, allow users to inspect the articles and consider adding regional or multilingual sources in future versions.

Risk 3 – Model-domain mismatch

The RoBERTa model was trained on Twitter data rather than specifically on solar energy industry news.
Technical announcements, investments and policy changes may therefore be classified differently from how an industry specialist would interpret them.
Who could be harmed? Analysts could overlook relevant developments because neutral wording hides important sector implications.
Mitigation: We should evaluate the model on a larger solar-specific dataset and develop separate labels for linguistic sentiment and sector impact.

Risk 4 – Overconfidence and misleading visualisations
Charts can make AI predictions appear more objective than they actually are.
A sudden increase in negative classifications does not necessarily mean that the solar energy industry is performing worse.
Who could be harmed? Users who rely on the dashboard without checking the underlying news may draw misleading conclusions.
Mitigation: The dashboard should include a clear disclaimer that it measures news-headline sentiment, not public opinion, environmental impact or financial performance. The results should be used to identify articles for further investigation rather than to make automatic decisions.

Overall, SolarMood should be considered a decision-support tool, not a replacement for professional judgement._

### Checklist
- [ ] Prototype code (or export / workflow file) is in `hackathon/`
- [ ] This week's slides are in `hackathon/`
- [x] The prototype actually runs, and I wrote down how to run it
- [x] Ethical reflection written above

---

## 3. Presentation -> [`presentation/`](presentation/)

*Only fill this in for the week your group was selected to present. You need at least **one** of these across the whole term.*

- [ ] My group presented in this week
- [ ] Slides are in `presentation/`
- [ ] Proof of the live demo is in `presentation/` (recording, screenshots, or link)

**How did it go? What would I do differently next time?**

---

## 4. Reflection

**What is the most important thing I learned this week?**
The most important thing I learned during this hackathon was how to connect different Python scripts and tools to create a working AI application.

Before this project, I had little experience with automatically collecting data from the internet or using a pretrained AI model to analyse text.

I learned that we could use an existing Hugging Face model instead of training our own AI. We connected this model to a Python script that collects news headlines and saves the results in a CSV file.

I also learned how to automate a process using a loop in Python. By creating auto_collect.py, I was able to make the collector run every 30 minutes without having to start it manually.

One of the biggest challenges was working with GitHub. I had difficulties uploading the latest data because the local project and the online repository had different versions. I learned how to solve these problems and successfully upload our files.

Another important lesson came from evaluating the AI models. Our results showed that RoBERTa and VADER did not always agree with our human labels.

This helped me understand that AI predictions are not automatically correct and that it is important to know exactly what a model is measuring.

Overall, I learned how data collection, AI analysis, automation and data visualisation can work together in one project.

**Where does this connect to "AI for Good"?**
_SolarMood connects to SDG 9: Industry, Innovation and Infrastructure.

The solar energy industry is important for the transition to renewable energy. New technologies, investments and government policies can influence how the industry develops.

With SolarMood, we use AI to make information about these developments easier to explore.

Instead of manually reading hundreds of headlines, users can view patterns in news sentiment through a dashboard.

This shows how AI can help people process large amounts of information and potentially support research and decision-making.

However, this project also showed us that AI has limitations.

Our evaluation demonstrated that AI models may interpret headlines differently from humans. If users trust the results without understanding these limitations, they could draw incorrect conclusions.

For me, the most important connection to AI for Good is that AI should not only make tasks easier, but should also be used responsibly.

It is important to be transparent about how the AI works, where the data comes from and what the results actually mean._

Sources:

International Renewable Energy Agency (IRENA). (2025). Renewables in 2024: 5 Key Facts Behind a Record-Breaking Year. https://www.irena.org/News/articles/2025/Apr/Renewables-in-2024-5-Key-Facts-Behind-a-Record-Breaking-Year
International Energy Agency (IEA). (2026). Global Energy Review 2026: Technology – Solar PV and Wind. https://www.iea.org/reports/global-energy-review-2026/technology-solar-pv-and-wind
Cardiff NLP. Twitter RoBERTa Base Sentiment Latest. https://huggingface.co/cardiffnlp/twitter-roberta-base-sentiment-latest
Hutto, C. J., & Gilbert, E. (2014). VADER: A Parsimonious Rule-based Model for Sentiment Analysis of Social Media Text. Proceedings of the International AAAI Conference on Web and Social Media.

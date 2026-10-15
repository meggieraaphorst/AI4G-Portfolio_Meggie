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
A pretrained sentiment analysis model from Hugging Face, using the Python transformers library.

We used the RoBERTa model (cardiffnlp/twitter-roberta-base-sentiment-latest) to classify solar energy news headlines as positive, neutral or negative.

We also used Python for data collection, Streamlit to visualise the results and VADER as a second sentiment analysis method for comparison.

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

### What did you build?

We built **SolarMood**, an AI-powered news monitoring application that automatically collects solar energy news, analyses the headlines and visualises the results in a Streamlit dashboard.

Our project consists of six main parts.

#### 1. Collecting news articles

We created a Python script called `collector.py` that collects solar energy news headlines from Google News RSS feeds.

The script:
- Searches for articles using solar energy-related keywords.
- Collects the headline, publication date and article link.
- Checks for duplicates to avoid saving the same article multiple times.

#### 2. Analysing headlines with AI

We used a pretrained **Hugging Face RoBERTa model** to analyse the sentiment of each headline.

The model classifies headlines into three categories:

- **Positive:** Headlines containing positive sentiment.
- **Neutral:** Headlines written in a neutral or factual way.
- **Negative:** Headlines containing negative sentiment.

The model also provides a confidence score for each prediction.

We did not train the AI model ourselves. Instead, we integrated an existing model into our Python project.

#### 3. Saving the results

The collected articles and AI predictions are saved in `solarmood.csv`.

This dataset contains the information needed for the dashboard and further analysis, including the headlines, dates, sentiment labels and confidence scores.

During our hackathon, we collected **815 news articles**.

#### 4. Automatic data collection

Initially, we had to run `collector.py` manually to collect new articles.

To automate this process, I worked on `auto_collect.py`, a Python script that:

1. Runs `collector.py`.
2. Waits 30 minutes.
3. Automatically starts the collector again.

I left my MacBook running overnight so SolarMood could continue collecting articles without manual input.

We also experimented with GitHub Actions to automate collection through GitHub, but initially experienced difficulties getting it to work.

#### 5. Creating the Streamlit dashboard

We used **Streamlit** to create an interactive dashboard that visualises the collected data.

The dashboard allows users to:

- View the total number of collected articles.
- See the distribution of positive, neutral and negative headlines.
- Explore changes in sentiment over time.
- Filter and inspect individual articles.

This makes it easier to understand patterns in the news instead of manually reading hundreds of headlines.

#### 6. Evaluating the AI models

To evaluate the sentiment predictions, we manually labelled **50 news headlines** and compared our labels with two sentiment analysis methods.

Milou worked on the comparison between RoBERTa and VADER.

| Method | Matching human labels | Agreement |
|---|---|---|
| **RoBERTa** | 21/50 | 42% |
| **VADER** | 19/50 | 38% |

RoBERTa showed slightly higher agreement with our human evaluations than VADER.

**What did we discover?**

Our manual evaluations sometimes focused on whether a development was beneficial or harmful to the solar energy industry, while the AI models mainly analysed the sentiment of the words in the headline.

For example, a headline about a new solar power plant might be considered positive by us because it represents progress in renewable energy. However, the AI could classify it as neutral because the headline is written factually.

**Our conclusion:** The AI models and our human evaluations did not always measure the same thing. This explains some of the disagreements and shows why clear evaluation guidelines are important.
_

**Link to the live thing (if any):**
_https://solarmood-milou-jkelt2tjctww4cb8fjsbri.streamlit.app/_

**How do I run it?**
_The easiest way to view SolarMood is through the live Streamlit dashboard linked above.

### How do I run it?

SolarMood can be accessed directly through our [live Streamlit dashboard](https://solarmood-milou-jkelt2tjctww4cb8fjsbri.streamlit.app/).

To run the project locally, follow the steps below.

#### 1. Set up the project

1. Download or clone the SolarMood repository from GitHub.
2. Open the project folder in VS Code.
3. Make sure Python is installed.
4. Open the terminal and install the required libraries:

   `python -m pip install -r requirements.txt`

The first time you run the sentiment analysis, the pretrained Hugging Face model may take some time to download.

#### 2. Run the Streamlit dashboard

Start the dashboard by entering this command in the terminal:

`python -m streamlit run dashboard.py`

Streamlit will provide a local URL, which you can open in your browser to view the dashboard.

#### 3. Collect new articles

To manually collect and analyse new solar energy news articles, run:

`python collector.py`

The script retrieves new headlines, analyses their sentiment and saves the results in `solarmood.csv`.

#### 4. Run automatic data collection

To automatically collect articles every 30 minutes, run:

`python auto_collect.py`

This script repeatedly runs the collector with a 30-minute interval.

**Important:** Automatic collection through this script only works while the computer is awake and the Python program is running.

#### Project files overview

| File | Purpose |
|---|---|
| `collector.py` | Collects news articles and analyses their sentiment using AI |
| `auto_collect.py` | Automatically runs the collector every 30 minutes |
| `dashboard.py` | Displays the collected data in Streamlit |
| `solarmood.csv` | Stores the collected articles and AI predictions |
| `requirements.txt` | Lists the Python libraries needed to run the project |
**Who did what?**
_### Who did what?

We worked together on SolarMood, but each focused on different parts of the project.

#### My contribution – Meggie

I mainly focused on **automatic data collection, GitHub and making the results available online**.

**Automatic news collection**
- Worked on `auto_collect.py` to automatically run the news collector every 30 minutes.
- Tested the Python scripts in VS Code and solved problems during the collection process.
- Kept my MacBook running overnight to collect news articles automatically.
- Collected a total of **815 news articles**, exceeding the minimum requirement of 300.

**GitHub and Streamlit**
- Uploaded the Python code and collected dataset to GitHub.
- Solved GitHub issues, including problems with merging local and online files.
- Made the collected data available through our Streamlit dashboard.
- Documented the Python files and explained how the different parts of the project work together.

#### Milou's contribution

Milou mainly focused on **model evaluation, comparing sentiment analysis methods and improving the dashboard**.

**Evaluating the AI models**
- Compared 50 manually labelled headlines with the predictions from RoBERTa.
- Used VADER as a second sentiment analysis method.
- Created Python scripts to calculate agreement percentages and confusion matrices.
- Investigated headlines where the AI predictions differed from our human evaluations.

**Testing and documentation**
- Set up and tested the Python environment.
- Worked on improving and testing the Streamlit dashboard.
- Tested the news collector and explored an alternative automatic collection method.
- Contributed to the README and project documentation.

#### Collaboration

We both contributed to developing and improving SolarMood. By dividing the tasks, we were able to focus on different technical challenges and combine our results into one project.

We also learned that keeping our files synchronised through GitHub is important when working together on a programming project._

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
- [x] Prototype code (or export / workflow file) is in `hackathon/`
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

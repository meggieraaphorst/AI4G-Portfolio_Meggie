# Term 1 - Week 5: Machine Learning Basics

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
SME Bankruptcy Model Showdown

**My pair partner:**
Lucas Hop

**Tool we had to use:**
Scikit-learn

**SDG we had to address:**
SDG 8 — Decent Work and Economic Growth

**What problem does it solve, and for whom?**
_Bankruptcy can have serious consequences for companies, employees and the economy. In the first quarter of 2023, 122 enterprises in Poland declared bankruptcy, which was 38.6% more than in the same period in 2022 (Statistics Poland, 2023).

Our project tries to identify Polish companies that are at risk of bankruptcy within one year, so that support could potentially be offered earlier. Our specific user is Anna Kowalska, a fictional financial-resilience adviser at a Polish SME-support organisation. She could use the prediction to identify companies that may benefit from an early and voluntary offer of financial support._

**What did you build?**
_We built a machine-learning notebook that compares three classification models: K-Nearest Neighbours, Logistic Regression and Random Forest. The models use financial data from Polish companies to predict whether a company is at risk of bankruptcy. We compare the models and use the best suitable model to make a prediction for a new example company._

**Link to the live thing (if any):**
_The Jupyter notebook is available in the hackathon/ folder._

**How do I run it?**
_Open the .ipynb notebook in Google Colab and select Runtime → Run all. The notebook downloads the dataset, prepares the data, trains and tunes the three models, compares their performance and makes a final example prediction._

**Who did what?**
_Meggie researched the problem and looked for reliable sources. Based on this research, we chose the topic together and selected a suitable dataset. Together, we decided what we wanted the model to predict and how it could be used to offer early support to companies at risk of bankruptcy.

Lucas then worked on preparing the data, running and tuning the three machine-learning models, and comparing their results. Meggie worked on documenting the project and created the presentation. We discussed the results and final conclusions together._

**Ethical reflection - what are the risks of your tool? Who could it harm?**
_A wrong prediction could negatively affect a company if the result is treated as a fact. A false negative could mean that a company at risk is not identified and therefore does not receive an early offer of support. A false positive could incorrectly label a financially healthy company as being at risk, which could cause unnecessary concern or reputational harm.

Therefore, the model should only be used to offer confidential and voluntary support, not to automatically make decisions about loans or other financial services. Financial information should also be handled carefully and the prediction should not be shared publicly.

The dataset contains historical data from Polish companies, so the model may not work equally well for companies in other countries or time periods. This means the model should not be used in a different context without first checking whether it still performs well._

### Checklist
- [ ] Prototype code (or export / workflow file) is in `hackathon/`
- [ ] This week's slides are in `hackathon/`
- [ ] The prototype actually runs, and I wrote down how to run it
- [ ] Ethical reflection written above

---

## 3. Presentation -> [`presentation/`](presentation/)

*Only fill this in for the week your group was selected to present. You need at least **one** of these across the whole term.*

- [ ] My group presented in this week
- [ ] Slides are in `presentation/`
- [ ] Proof of the live demo is in `presentation/` (recording, screenshots, or link)

**How did it go? What would I do differently next time?**

---

## 4. Reflection

**What is the most important thing we learned this week?**
The most important thing we learned this week is that the model with the highest accuracy is not always the best model. We learned how to compare different models and look at different results. For our project, recall is especially important because we want to find as many companies as possible that are actually at risk of bankruptcy..

**Where does this connect to "AI for Good"?**
_Our project connects to AI for Good because the prediction is used to offer support instead of punishing companies. By identifying companies that may be at risk earlier, an SME-support organisation could offer financial guidance before the situation becomes worse. We also learned that AI predictions should be used carefully, because an incorrect prediction could negatively affect a company._

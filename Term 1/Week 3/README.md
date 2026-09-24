# Term 1 - Week 3: Lists & Dictionaries

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
ClearForMe

**My pair partner:**
Sam Kempers

**Tool we had to use:**
Python with an LLM API (we used the Claude API)

**SDG we had to address:**
SDG 10

**What problem does it solve, and for whom?**
_ClearForMe helps adults in the Netherlands who have difficulty understanding complex Dutch government texts. Government letters can contain difficult words, long sentences and important information about deadlines or actions, which can make it harder for some people to understand what they need to do._

**What did you build?**
_We built a web app where users can paste a difficult Dutch government text. ClearForMe uses Claude AI to explain the text in simple Dutch and shows a simple explanation, what the user needs to do, important dates and details, and explanations of difficult words._

**Link to the live thing (if any):**
_https://youtu.be/MnZe92lbVU8_

**How do I run it?**
_We have created a file to run the program called, run.bat.
Whenever the folder is opened you can open the terminal and run the following command; .\run.bat_

**Who did what?**
_Whenever we worked at the product we sat together, irl or by teams. We let Claude do the coding with clear instructions given by us.
  Sam provided the Demo video, while Meggie made the presentation. There was not an imbalance during our collaboration._

**Ethical reflection - what are the risks of your tool? Who could it harm?**
_The main risk of ClearForMe is that AI can make mistakes when simplifying texts. It could leave out or incorrectly explain important information such as deadlines, amounts or required actions. This could especially harm the people our tool is designed for, because someone who already finds the original text difficult may not notice that the AI explanation is wrong. There is also a privacy risk because users might paste personal information from real letters into the app. To reduce these risks, ClearForMe warns users that AI can make mistakes, keeps the original text available for comparison, and asks users to remove personal information before sending the text to AI. ClearForMe should therefore be used as a tool to help understand a text, not as a replacement for the original document or professional advice._

### Checklist
- [x] Prototype code (or export / workflow file) is in `hackathon/`
- [x] This week's slides are in `hackathon/`
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
The most important thing I learned this week is that building an AI tool is not only about making the AI work. At first, I mainly thought about whether Claude could simplify a difficult text, but during this project I learned that we also had to think about what happens when the AI makes a mistake. Because ClearForMe deals with government texts, even a small mistake in a deadline, amount or required action could have consequences for the user. I learned that we need to give the AI clear instructions, validate its output and design the interface in a way that makes its limitations clear. I also learned how Claude can be connected to a Python application through an API, instead of only using Claude as a chatbot.

**Where does this connect to "AI for Good"?**
_ClearForMe connects to AI for Good because it uses AI to reduce information inequality. People who have difficulty understanding complex government language may have less access to important information about their rights, responsibilities or deadlines. AI can help make this information easier to understand, but it can also create a new risk if people trust an incorrect AI explanation. This project showed me that using AI for a good purpose is not automatically “AI for Good”. The way the tool is designed also matters. That is why ClearForMe keeps the original text available, warns that AI can make mistakes and asks users to remove personal information before sending their text. The goal is not to replace official information, but to make it more accessible while being transparent about the limitations of AI._

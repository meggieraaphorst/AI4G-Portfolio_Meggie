# Term 1 - Week 7: Computer Vision

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

**Project title:** Waterbird Counter: detecting and counting waterbirds at Dutch city ponds

**My pair partner:** Yazan Nemo

**Tool we had to use:** SDG 15, Life on Land

**SDG we had to address:**

**What problem does it solve, and for whom?**
_Volunteer waterbird counters (e.g. Sovon volunteers) count birds by hand at city ponds and canals. With big groups this is slow and error-prone. Our tool counts birds per species from one photo, giving consistent counts that feed into trend monitoring, so declines, the spread of the exotic Egyptian goose, and priority ponds can be spotted earlier._

**What did you build?**
_A Streamlit app where a user uploads a pond photo and gets boxes around every mallard, coot and Egyptian goose, plus a count per species. Egyptian geese are flagged as exotic. Counts can be saved per location in a log and downloaded as CSV._

**Link to the live thing (if any):**
_Runs locally (see below). Demo: [link to screen recording or screenshots in hackathon/]_

**How do I run it?**
_1. Create a `.env` file in `hackathon/` based on `.env.example` (Roboflow API key + model ID)
2. Open `run_app.py` in VS Code and press Run. It installs the requirements and opens the app in your browser._

**Who did what?**
_Yazan: filmed the dataset, frame extraction, model training and evaluation, Streamlit app, problem analysis.
Meggie: lebeling the sampels, the presentation, README, ethical reflection.._

**Ethical reflection - what are the risks of your tool? Who could it harm?**
_Our dataset is 4 short videos from water ponds in the hague (almost 320 frames) plus ~40 scraped images from the internet. Our first model scored 89.6% mAP@50 but failed on new photos (coots labelled as mallards), because frames from the same videos were in both training and test data. Extra targeted data raised coot from 65% to 81%, but the model still only knows 3 species, so other birds get miscounted, and it was trained on autumn daylight only. If used for real decisions, systematic miscounts could make a population look like it is declining, sending conservation effort to the wrong place, and a false Egyptian goose detection could support control measures against birds that were not there. Photos of parks may include people, so the app stores counts only, no images. The model is an assistant: the volunteer verifies every count and stays accountable for what is reported._

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
A high test score does not mean a model works. Our model scored ~90% but failed on photos from outside our own videos. Testing on truly unseen data exposed overfitting, and adding targeted data for the weakest class fixed it.

**What is the most important thing I learned this week?**
Conservation decisions depend on reliable counts. A tool that helps volunteers count faster only does good if its errors are known and checked by a human; otherwise it can push nature policy in the wrong direction.

**Where does this connect to "AI for Good"?**
_One concrete link to ethics, sustainability or social impact._

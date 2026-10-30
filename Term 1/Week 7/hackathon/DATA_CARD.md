# Data
We filmed 4 videos of 20 seconds each at water ponds in The Hague, and extracted frames at about 5 frames per second (~320 images). After our first model failed on new photos, we added ~40 scraped images of coots and mallards from the internet. All images were labelled by hand in Roboflow with 3 classes: mallard, coot and egyptian_goose. Split: 70/20/10.

# Limitations
Our first model scored 89.6% mAP@50, but failed on internet photos: coots were labelled as mallards and a close-up mallard as an Egyptian goose. The cause was overfitting: frames from the same 4 videos ended up in both training and test sets, so the test score was too optimistic. Adding targeted scraped data raised coot from 65% to 81% and fixed these cases, but the leakage is only partly solved. The model only knows 3 species, so a swan, gull or moorhen will be miscounted as one of them. Data is from autumn, daylight and a few ponds; other seasons, light or locations may perform worse. Distant, overlapping or hidden birds are missed.

# What could go wrong
Counts feed into trend monitoring. If coots are systematically undercounted, someone could wrongly conclude the population is declining, and conservation money could go to the wrong place. Egyptian geese are flagged as exotic; a false detection could support control measures against birds that were never there. Park photos may also contain people; our app does not store images, only counts.

# Accountability
The model is an assistant, not a decision maker. The volunteer checks every count before reporting it, and the app shows its limitations in the sidebar so users know when not to trust it.
# Lab 9 - NLP Task Submission

## Selected Subtask
I selected **Text Classification** from the **NLP Tasks** section of GeeksforGeeks NLP tutorial.

Reference tutorial section:
- https://www.geeksforgeeks.org/natural-language-processing-nlp-tutorial/

## Task Objective
Build a simple NLP web application that classifies movie-review style text into:
- Positive sentiment
- Negative sentiment

## Approach Used
1. Created a small custom labeled dataset (positive/negative text samples).
2. Converted text into numerical features using **TF-IDF**.
3. Trained **Multinomial Naive Bayes** classifier.
4. Evaluated model on a test split.
5. Integrated model in a **Flask** app with a simple HTML interface.
6. Predicted sentiment for user-entered input from browser.

## Files
- `main.py` -> Flask server and ML pipeline
- `templates/index.html` -> frontend page for text input and output
- `requirements.txt` -> dependency list

## How to Run
1. Open terminal in this folder.
2. Install dependency:
   ```bash
   pip install -r requirements.txt
   ```
3. Run Flask app:
   ```bash
   python main.py
   ```
4. Open in browser:
   ```
   http://127.0.0.1:5000
   ```

## Expected Output
Web app displays:
- Prediction (positive/negative) for entered sentence
- Model accuracy
- Classification report (precision, recall, f1-score)

## Note
This is an educational implementation for university lab practice.

# ANSR Global – Schedule Automation

Streamlit web app that reads the **Accounting Pack** (Transaction List FTM)
and auto-populates all 10 sheets in the monthly Schedules file.

## Repo structure

```
├── app.py                    # Streamlit UI
├── automate_schedules.py     # Core parsing + population logic
├── Schedules_Template.xlsx   # The blank schedules template (committed once)
├── requirements.txt
└── README.md
```

## Running locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Deploying on Streamlit Cloud

1. Push this repo to GitHub
2. Go to https://share.streamlit.io → New app
3. Select repo, branch `main`, file `app.py`
4. Click Deploy

## Monthly usage

1. Export the Accounting Pack from Tally
2. Open the web app
3. Upload the file → Download the populated Schedules

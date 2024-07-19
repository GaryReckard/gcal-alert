## Steps to Create credentials.json
1. Go to the Google Cloud Console:
    - Visit the Google Cloud Console.
2. Create a New Project:
   - If you don't have a project, create a new one by clicking on the project dropdown and selecting "New Project".
   Give your project a name and click "Create".
3. Enable the Google Calendar API:
   - Select your project in the Google Cloud Console.
   - Go to the Google Calendar API page and click "Enable".
4. Create OAuth 2.0 Credentials:
   - In the Google Cloud Console, go to the "APIs & Services" > "Credentials" page.
   - Click "Create Credentials" and select "OAuth client ID".
   - You might need to configure the OAuth consent screen if you haven’t already. Provide the necessary information and save.
   - Select "Desktop app" for the application type.
   - Click "Create" and download the credentials JSON file.
   - rename that file to `credentials.json`

# Setup
- `conda env create -f environment.yml`
- `conda activate gcal-alert`
- `pip install -r requirements.txt`
- Edit `run_gcal_alert.sh` to reflect correct paths
- make the script executable if it is not: `chmod +x /path/to/your/run_gcal_alert.sh`
- add something like `* * * * * /path/to/your/run_gcal_alert.sh` to your crontab (`crontab -e`) to run this every minute
  - (or something like this to see logs/debug 
  - `* * * * * /Users/gary/Dev/gcal-alert/run_gcal_alert.sh >> /Users/gary/Dev/gcal-alert/gcal-alert.log 2>&1`) 


# Notes
- The first time you run it, it'll have you authenticate using your Google acct
- If you need to re-authenticate, do a `rm token.json` and re-run it
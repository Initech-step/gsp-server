# gsp-server
The Official server for the God's Lighthouse Starter Pack.

# Features
- Content Upload Update
--- on app open current upload state is pulled from server
--- this is managed manually

- User Progress Upload
--- User can upload their progress
--- Set weekly reminders to backup progress
--- Users can download existing notes

- User Notes Storage
--- User can backup all notes in the settings section
--- set bi-weekly reminder to backup notes
--- Users can download and replace weekly progress

- User auth
--- A basic auth with email/phone number/shepherd number and password
--- No verification process
--- auth details get stored in react native async storage

# Run tests
pytest test_api.py -v
python -m pytest

# Run with coverage
pytest test_api.py --cov=app -v
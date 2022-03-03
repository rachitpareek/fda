### FDA Donations Scraper

Scrapes donations and saves in local CSV.

Set up virtualenv with `python3 -m venv venv` and run `pip3 install -f requirements.txt` to download dependencies. 

Activate venv with `source venv/bin/activate`.

Call script with `python3 donations_scraper.py --url https://iris-seadragon-e459.squarespace.com/config/donations --username ENTER_USERNAME --password 'ENTER_PASSWORD_IN_QUOTES'`


#### NDCA Scraper Instructions

Make sure you've gone through the Git and Terminal introductions in the Asana task here before following these steps. 

1. Open your laptop's terminal application. 
2. Use `cd` to navigate to a directory that you want to make a copy of the fda code repository in. 
3. Clone this repository by going to `https://github.com/rachitpareek/fda`, clicking the dropdown on the `Code` button, copying the link, and entering `git clone LINK` into your terminal. The link should look either like `git@github.com:rachitpareek/fda.git` or `https://github.com/rachitpareek/fda.git`. 
4. Enter the appropriate directory by typing `cd fda/scripts`. Then run `source venv/bin/activate`, then run `pip3 install -r requirements.txt`
5. Run the scraper with `python3 ndca_scraper.py -t TYPE` where TYPE is one of ld, pf, or policy. 

Message me with questions!

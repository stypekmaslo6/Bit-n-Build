# Installation Setup
## Required technologies
* Python 3.10
* Flask 2.3.3
* Flask_session 0.6.0
* SQLAlchemy 2.0.27
* Werkzeug 2.3.7

## Initialazing
* First of all you have to download every photo from this repository
* Then you have to initialize your local database in python console
```
>>from main import db
>>db.create_all()
>>exit()
```
* Then you just have to run the program and open localhost

## Usage Guide
When you are on the main page in the upper right corner you can operate with your account, sales and switch between two different sites.
At the very bottom there are logos of companies that trusted in us. 
* If you want to register a new account - click "Register"
* If you want to login into already existing account - click "Login"
* If you want to add a new product - click "Sell a product"
* If you want to go to your sales - click "Go to user site"
* If you want to delete some items from your personal market - mark checkboxes on the list and click "Delete checked products"

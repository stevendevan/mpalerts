# mpalerts
The "MP" in "mpalerts" stands for "Mountain Project".

This script scrapes the first page of the MP for-sale forum in search of posts containing keywords that the user has specified.

Good deals get snatched up within minutes. Automatically running this script every 10 minutes or so allows users to have relevant for-sale posts emailed or texted to them quickly enough to swoop in and snatch the goods.
# Running the thing
You will need a python installation.

Dependencies are light: we only need the **requests** and **BeautifulSoup** packages.

I use the Windows task scheduler because I am using Windows 10.

You will need to configure things in the **notification_tools.py** file to your liking. I am sending myself text messages. If you don't use android or have another cell provider, you will have to configure it differently. If you want emails instead of text messages, you will have to write that code.

You will have to create your own **secret_data.py** file with the 3 constants: **PHONE_NUMBER, EMAIL_ADDRESS, EMAIL_PASSWORD** or other required credentials.

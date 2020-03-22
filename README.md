## What it is

Spreadform enables you to submit web form data into a Google spreadsheet.

You can create (and update) an arbitrary web form, have it submit to a Spreadform back end, and receive data in real-time in your own Google sheet.

I built Spreadform as part of the response to Coronavirus, to help organisations quickly publish forms and collect responses in real-time. 

If Google Forms works for you, I'd advise you to use that. If you prefer to have a custom web form, then Spreadform is for you.

## Setup

### Set up you web form and Google sheet

 * Host an HTML web form somewhere that works for you (a form page, a confirmation page and an error page). These can be static files.
 * A Google sheet (note the sheet ID and the name of a worksheet in it that you want to use)

### Create a Google cloud project

 * Create a [Google Cloud (GCP)](https://cloud.google.com/) account if you don't have one already (new accounts get [free credit](https://cloud.google.com/free))
 * Create a project in your account (and note the project ID)

### Create configuration files

You'll now need to create some files in the root directory of this repo to configure Spreadform. These are one-line text files:

 * **account.txt**: your GCP login email address, e.g. `user@example.com`
 * **project_id.txt**: your GCP project ID that you noted above, e.g. `spreadform-123456`
 * **sheet-id.txt**: the ID of your Google sheet, e.g. if your sheet URL is `https://docs.google.com/spreadsheets/d/1ENnMtNP5NXWIc10UFdqnpO97LEso7wBDvRjY-IeIGy8/edit` then your sheet ID is `1ENnMtNP5NXWIc10UFdqnpO97LEso7wBDvRjY-IeIGy8`
 * **worksheet-name.txt**: the name of a worksheet in you spreadsheet, e.g. `Sheet1`
 * **form_page.txt**: the url of your web form, e.g. `https://example.com/form.html`
 * **success_page.txt**: the url of your "submission success" page, e.g. `https://example.com/success.html`
 * **error_page.txt**: the url of your "submission error" page, e.g. `https://example.com/error.html`

### Deploy spreadform

 * Deploy spreadform using the `deploy.sh` script - this _should_ guide you with configuration if there are any issues.
 * Update your web form `action` to the URL of yous Spreadform deployment, shown at the end of the output from deployment
 * Grant edit permission on your Google sheet to the the email address of your Spreadform deployment, shown at the end of the output from deployment

### How it works

 * Open the web form in your browser (as per `form_page.txt`)
 * Enter some data
 * Submit your form
 * Spreadform receives the fields, generates a timestamp and a random alphanumeric submission ID, logs out all the data as a fallback (retained for 30 days by Stackdriver logging) and then submits it to a message queue for processing
 * If successful, Spreadform redirects you to your success page (`success_page.txt`) with a query parameter containing the submission ID, e.g. `https://example.com/success.html?id=a1b2c3d4`
 * If an error occurs, Spreadform redirects you to your error page (`error_page.txt`) with a query parameter containing the submission ID, e.g. `https://example.com/error.html?id=a1b2c3d4`
 * The message queue is processed one submission at a time (to avoid rows getting mixed up in the spreadsheet)
 * Key-value pairs in the data are compared to any existing header row keys in the spreadsheet (row 1)
 * If needed, new headings are added to the header row to accommodate the submitted data
 * A new row is added to the bottom of the spreadsheet, containing the submitted data values in the matched columns

## Data security

I wrote this in a day, so please be generous - it's imperfect, but it's pretty good. Providing you host your form using https, data will be encrypted in transit and at rest until handed off to your Google sheet. The form submission endpoint is https, pubsub encrypts messages and all APIs (e.g. Google Sheets) are https.

I've made one compromise on data storage (which you can change in `form/index.js` if it doesn't work for you you): To ensure a belt-and-braces approach to data capture, form submissions are written out to application logs. In GCP this means they are retained in Stackdriver Logging for 30 days and can be located by searching for the submission ID. The aim here is to avoid data loss when you're moving fast, whilst still ensuring good data security on balance.

## You might like to know

 * Spreadform is serverless (using Google Cloud Functions, Pubsub and Sheets)
 * It's likely to cost you nothing to run on the GCP free tier for several thousand submissions
 * If you're using this in UK Governmont, you can use Gov.uk Notify (see the "notify" branch)

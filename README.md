## PPE Inventory stock monitoring

This repository contains the code for the NELCA ppe stock management system, helping track personal protective equipment stocks to support distribution. 

![Stock levels input form](https://raw.githubusercontent.com/wiki/notbinary/ppe-inventory/images/form.png)

To see more screens from the application, please head to the [wiki](https://github.com/notbinary/ppe-inventory/wiki)

## Demo environment

If you'd like to see this system in action, a demonstration environment is available as follows:

 * Portal: https://ppe-inventory-demo-mf2rj3t7eq-ew.a.run.app/ (username: demo, password: password)
 * Daahboard spreadsheet: https://docs.google.com/spreadsheets/d/1csuprj90P3EutWy05lcKsfl2QDTtNQhz0Jj97oum0jQ
 * Community spreadsheet: https://docs.google.com/spreadsheets/d/1NIoqxTiiqi2p2zXGDIu1jMAeoni-jL4SWJ3zlidfdw8
 * Registration links: 
   * [TODO]
   * [TODO]

## Setup

If you'd like to set up a copy of this system for yourself, here are the steps. Please also refer to this [Github Actions workflow](https://github.com/notbinary/ppe-inventory/blob/test/.github/workflows/demo-pipeline.yml)

### Prerequisites

To deploy this repo you'll need to be set up for developing with [Google Cloud](https://cloud.google.com/):

 * You'll need a Google identity. If you have a Google account, you can use that. If you don't have a Google account you can either register one, (@gmail.com) or you can create an account for an email address you already have (for example, a work email address). Head to https://accounts.google.com/signup and optionally click the "Use my current email address instead" link.
 * You'll need access to a Google Cloud Platform (GCP) account. Go to https://console.cloud.google.com/ to get started. You may need to enter a credit card, but you won't be charged unless you explicitly upgrade your account.
 * From the Google Cloud Console, [create a project](https://cloud.google.com/resource-manager/docs/creating-managing-projects) to deploy this repository to.
 * The project may take a minute or two to be set up. Once it's ready you'll be able to select it from the projects drop-down at the top of the screen.
 * Make a note of your login email address (your Google identity)
 * Make a note of the project ID (this can be found in the projects dialog when you click the projects drop-down at the top of the screen)
 * Install the [Google Cloud SDK](https://cloud.google.com/sdk/install)
 * Log in to the Google Cloud SDK using `gcloud auth login` on your command-line using your google identity (e.g. example@gmail.com). This will pop up a browser for you to authorise access. For more information see: https://cloud.google.com/sdk/gcloud/reference/auth/login

### Deployment

The following steps walk through deploying a copy of this repo to your GCP project:

 * Start by cloning this repo
 * Create a Google Spreadsheet (e.g. via https://drive.google.com) - this will serve as your dashboard. Make a note of the sheet ID (e.g. for `https://docs.google.com/spreadsheets/d/1A-HL1x1s81ZGCgg_cmYK27NNPk1uQjAZcwd8O6yrJ18/edit#gid=0` the sheet ID is `1A-HL1x1s81ZGCgg_cmYK27NNPk1uQjAZcwd8O6yrJ18`)
 * Make a note of the name of one of the worksheets in your spreadsheet (e.g. `Sheet1`) - this is where data will be reported.
 * Create a directory called `exclude` in the root of the repo.
 * Create the following one-line text files (these are named explicitly in `.gitignore` as a reminder):
   * `exclude/account.txt` - your Google identity (e.g. `example@gmail.com`)
   * `exclude/project_id.txt` - your project ID, from the projects drop-down in the [Google Cloud Console](https://console.cloud.google.com/)
   * `exclude/sheet-id.txt` - the ID of the Google spreadsheet you created (e.g. `1A-HL1x1s81ZGCgg_cmYK27NNPk1uQjAZcwd8O6yrJ18`)
   * `exclude/worksheet-name.txt` - the name of the worksheet in the spreadsheet that you want to use.
 * locate the and run the `deploy.sh` script in the root directory. This should work for Mac and Linux users. If you're using Windows you may be able to translate the commands for your environment.
 * You'll see one or two error messages as the deployment script checks for resources that don't yet exist. It should create them successfully after the errors are printed out. Subsequent runs should go through cleanly.

### Post-deployment steps

Once you have successfully deployed, the following additional steps need to be completed:

 * Navigate to Datastore in the GCP console (https://console.cloud.google.com/datastore). If this is not yet enabled, click on "Select datastore mode" and select a region (e.g. `europe-west2 (London)`)
 * Grant edit permissions on your Google Spreadsheet to [`project_id`]@appspot.gserviceaccount.com (e.g. `ppe-inventory-123456@appspot.gserviceaccount.com`)"

### Creating sites

After completing the steps above you'll be able to create sites to test with [TODO].

To verify a successful setup check the following work for you:

 * You should now be able to navigate to the URL of the deployed function and see an "access denied" message (e.g. https://europe-west2-ppe-demo-123456.cloudfunctions.net/form)
 * You should also be able to navigate to the URL of the deployed portal (e.g. https://ppe-demo-123456-abcdefghij-kl.a.run.app)


## Tests

BDD tests are provided in the `features` directory. Those tagged with `@pipeline` will run automatically during CI/CD build deployment.

Some tests e.g. those that could modify the datastore, are excluded from running automatically and should be 
run manually. For example, to run the tests for adding new providers use the following command:
```
behave --tags=@new-providers
```  
Several environment variables will be used to configure the tests so these will need to be set e.g.

```
export DOMAIN=**************************.cloudfunctions.net
export VALID_PROVIDER_NAME=********
export VALID_PROVIDER_CODE=********
```
Also, this test will need valid `gcloud` configuration e.g.
```
export GOOGLE_APPLICATION_CREDENTIALS="ppe-inventory-dev.json"
```



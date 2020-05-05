PPE Inventory

Helping track personal protective equipment stocks to support distribution.

### Tests

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




PPE Inventory

Helping track personal protective equipment stocks to support distribution.


### Tests
BDD tests are provided and those tagged with `@pipline` will run automatically during CI/CD build deployment.

Some tests e.g. those that could modify the datastore, are exlcuded from running automatically and should be 
run manually. For example, to run the tests for adding new providers use the following command:
```
behave --tags@@new-providers

```  

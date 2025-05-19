**Unreleased**
* print function uses inspect to identify calling function in logs
* use requests.session for token auth and phantom.requests for non-token (fixes a bug at high call volumes)
* fixed issue with halt action

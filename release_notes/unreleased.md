**Unreleased**

- print function uses inspect to identify calling funtion in logs
- use requests.session for token auth and phantom.requests for non-token (fixes a bug at high call volumes)
- fixed issue with halt action
- pre @ericli, replaced hardcoded refs to loopback address with _get_phantom_base_url

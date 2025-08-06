# Runner

Publisher: Mhike <br>
Connector Version: 1.1.1 <br>
Product Vendor: Mhike <br>
Product Name: Runner <br>
Minimum Product Version: 4.9.0

Runner schedules and executes playbooks based on generated schedule artifacts

### Configuration variables

This table lists the configuration variables required to operate Runner. These variables are specified when configuring a Runner asset in Splunk SOAR.

VARIABLE | REQUIRED | TYPE | DESCRIPTION
-------- | -------- | ---- | -----------
**https_port** | optional | string | Splunk SOAR HTTPS port if your instance uses one other than 443 |
**playbook_limit** | required | numeric | How many playbooks should be allowed to run per poll (default: 4) |
**cluster_base_url** | optional | string | The base URL to use in a cluster environment |
**cluster_api_token** | optional | password | An API token for a cluster environment |
**debug** | optional | boolean | Print debugging statements to log |

### Supported Actions

[test connectivity](#action-test-connectivity) - Validate the asset configuration for connectivity using supplied configuration <br>
[schedule playbook](#action-schedule-playbook) - Create a schedule artifact for a playbook to run later <br>
[execute playbook](#action-execute-playbook) - Execute the configured playbook immediately (Format: <repository>/<playbook>) <br>
[clear scheduled playbooks](#action-clear-scheduled-playbooks) - Remove all pending scheduled playbooks on a container <br>
[count runner artifacts](#action-count-runner-artifacts) - Returns a count of the matching runner artifacts in the current container <br>
[on poll](#action-on-poll) - Execute scheduled playbooks if their delay period has expired. Smaller intervals will result in more accurate schedules

## action: 'test connectivity'

Validate the asset configuration for connectivity using supplied configuration

Type: **test** <br>
Read only: **True**

#### Action Parameters

No parameters are required for this action

#### Action Output

No Output

## action: 'schedule playbook'

Create a schedule artifact for a playbook to run later

Type: **generic** <br>
Read only: **False**

This will add a specially formatted artifact to the container with the supplied details. This artifact will be created in a pending state. The polling action for this app will look for these pending artifacts and after the schedule time has elapsed, execute the specified playbook.

#### Action Parameters

PARAMETER | REQUIRED | DESCRIPTION | TYPE | CONTAINS
--------- | -------- | ----------- | ---- | --------
**delay_purpose** | required | A short comment on the purpose of the scheduled execution | string | |
**duration_unit** | required | Units to be used for the delay duration | string | |
**delay_duration** | required | How many units to delay before execution | numeric | |
**playbook** | required | The playbook to execute after the delay (Format: <repository>/<playbook>) | string | |
**playbook_scope** | required | The scope to be applied to the playbook when executing | string | |
**artifact_id** | optional | The ID of the artifact to run the playbook on (requires artifact scope) | numeric | |
**container_id** | optional | The ID of the container to run the playbook on (requires a container scope) | numeric | |
**input_data** | optional | An input dictionary to be used with the playbook (input playbooks only) | string | |

#### Action Output

DATA PATH | TYPE | CONTAINS | EXAMPLE VALUES
--------- | ---- | -------- | --------------
action_result.parameter.delay_purpose | string | | |
action_result.parameter.duration_unit | string | | |
action_result.parameter.delay_duration | numeric | | |
action_result.parameter.playbook | string | | |
action_result.parameter.playbook_scope | string | | |
action_result.parameter.artifact_id | numeric | | |
action_result.parameter.container_id | numeric | | |
action_result.parameter.input_data | string | | |
action_result.status | string | | success failed |
action_result.message | string | | |
summary.total_objects | numeric | | |
action_result.parameter.container_id | numeric | | |
summary.total_objects_successful | numeric | | |

## action: 'execute playbook'

Execute the configured playbook immediately (Format: <repository>/<playbook>)

Type: **generic** <br>
Read only: **False**

This will execute the specified playbook and parameters immediately with no artifacts generated.

#### Action Parameters

PARAMETER | REQUIRED | DESCRIPTION | TYPE | CONTAINS
--------- | -------- | ----------- | ---- | --------
**playbook** | required | The playbook to execute | string | |
**playbook_scope** | required | The scope to be applied to the playbook when executing. Container scopes are for containers other than the current container | string | |
**artifact_id** | optional | The ID of the artifact to run the playbook on (requires artifact scope) | numeric | |
**container_id** | optional | The ID of the container to run the playbook on (requires container scope) | numeric | |
**input_data** | optional | A dictionary of parameters to be used with the target playbook (input playbooks only) | string | |

#### Action Output

DATA PATH | TYPE | CONTAINS | EXAMPLE VALUES
--------- | ---- | -------- | --------------
action_result.parameter.playbook | string | | |
action_result.parameter.playbook_scope | string | | |
action_result.parameter.artifact_id | numeric | | |
action_result.parameter.container_id | numeric | | |
action_result.parameter.input_data | string | | |
action_result.status | string | | success failed |
action_result.message | string | | |
summary.total_objects | numeric | | |
summary.total_objects_successful | numeric | | |

## action: 'clear scheduled playbooks'

Remove all pending scheduled playbooks on a container

Type: **generic** <br>
Read only: **False**

This action is used to remove all pending schedule playbooks for a container. This is generally intended to be used to cancel execution if some exit criteria has been reached and any scheduled playbooks need to be suspended permanently.

#### Action Parameters

PARAMETER | REQUIRED | DESCRIPTION | TYPE | CONTAINS
--------- | -------- | ----------- | ---- | --------
**cancellation_reason** | required | A short comment on why the playbooks were cancelled | string | |
**container_id** | optional | The ID of the container to cancel schedules for. If an ID is not provided, the current container is assumed | string | |

#### Action Output

DATA PATH | TYPE | CONTAINS | EXAMPLE VALUES
--------- | ---- | -------- | --------------
action_result.parameter.cancellation_reason | string | | |
action_result.parameter.container_id | string | | |
action_result.status | string | | success failed |
action_result.message | string | | |
summary.total_objects | numeric | | |
summary.total_objects_successful | numeric | | |

## action: 'count runner artifacts'

Returns a count of the matching runner artifacts in the current container

Type: **generic** <br>
Read only: **True**

This action is used to determine how many times a specific sheculed playbook has been run in the given container. This is generally used to evaluate escape scenarios when using runner to perform loops and retries.

#### Action Parameters

PARAMETER | REQUIRED | DESCRIPTION | TYPE | CONTAINS
--------- | -------- | ----------- | ---- | --------
**playbook_filter** | optional | Optional filter to count only runner artifacts for the given playbook (Format: <repository>/<playbook>) | string | |
**label_filter** | optional | Optional filter to count only runner artifacts with the given label | string | |

#### Action Output

DATA PATH | TYPE | CONTAINS | EXAMPLE VALUES
--------- | ---- | -------- | --------------
action_result.parameter.playbook_filter | string | | |
action_result.parameter.label_filter | string | | |
action_result.status | string | | success failed |
action_result.message | string | | |
summary.total_objects | numeric | | |
summary.total_objects_successful | numeric | | |
action_result.data.\*.runner_artifact_count | numeric | | |

## action: 'on poll'

Execute scheduled playbooks if their delay period has expired. Smaller intervals will result in more accurate schedules

Type: **generic** <br>
Read only: **False**

#### Action Parameters

No parameters are required for this action

#### Action Output

No Output

______________________________________________________________________

Auto-generated Splunk SOAR Connector documentation.

Copyright 2025 Splunk Inc.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing,
software distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and limitations under the License.

[comment]: # "Auto-generated SOAR connector documentation"
# Runner

Publisher: Mhike  
Connector Version: 1\.0\.2  
Product Vendor: Mhike  
Product Name: Runner  
Product Version Supported (regex): "\.\*"  
Minimum Product Version: 4\.9\.0  

Runner schedules and executes playbooks based on generated schedule artifacts

[comment]: # " File: README.md"
[comment]: # "  Copyright (c) Mhike, 2022"
[comment]: # "  Licensed under Apache 2.0 (https://www.apache.org/licenses/LICENSE-2.0.txt)"
[comment]: # ""
[comment]: # "  Licensed under the Apache License, Version 2.0 (the 'License');"
[comment]: # "  you may not use this file except in compliance with the License."
[comment]: # "  You may obtain a copy of the License at"
[comment]: # "      http://www.apache.org/licenses/LICENSE-2.0"
[comment]: # "  Unless required by applicable law or agreed to in writing, software distributed under"
[comment]: # "  the License is distributed on an 'AS IS' BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND,"
[comment]: # "  either express or implied. See the License for the specific language governing permissions"
[comment]: # "  and limitations under the License."
[comment]: # ""



### Configuration Variables
The below configuration variables are required for this Connector to operate.  These variables are specified when configuring a Runner asset in SOAR.

VARIABLE | REQUIRED | TYPE | DESCRIPTION
-------- | -------- | ---- | -----------
**https\_port** |  optional  | string | Splunk SOAR HTTPS port if your instance uses one other than 443
**playbook\_limit** |  required  | numeric | How many playbooks should be allowed to run per poll \(default\: 4\)
**debug** |  optional  | boolean | Print debugging statements to log

### Supported Actions  
[test connectivity](#action-test-connectivity) - Validate the asset configuration for connectivity using supplied configuration  
[schedule playbook](#action-schedule-playbook) - Create a schedule artifact for a playbook to run later  
[clear scheduled playbooks](#action-clear-scheduled-playbooks) - Remove all pending scheduled playbooks on a container  
[on poll](#action-on-poll) - Execute scheduled playbooks if their delay period has expired\. Smaller intervals will result in more accurate schedules  

## action: 'test connectivity'
Validate the asset configuration for connectivity using supplied configuration

Type: **test**  
Read only: **True**

#### Action Parameters
No parameters are required for this action

#### Action Output
No Output  

## action: 'schedule playbook'
Create a schedule artifact for a playbook to run later

Type: **generic**  
Read only: **False**

This will add a specially formatted artifact to the container with the supplied details\. This artifact will be created in a pending state\. The polling action for this app will look for these pending artifacts and after the schedule time has elapsed, execute the specified playbook\.

#### Action Parameters
PARAMETER | REQUIRED | DESCRIPTION | TYPE | CONTAINS
--------- | -------- | ----------- | ---- | --------
**delay\_purpose** |  required  | A short comment on the purpose of the scheduled execution | string | 
**duration\_unit** |  required  | Units to be used for the delay duration | string | 
**delay\_duration** |  required  | How many units do you want to delay before execution | numeric | 
**playbook** |  required  | The playbook do you want to execute after the delay | string | 
**playbook\_scope** |  required  | The scope to be applied to the scheduled playbook when executing | string | 
**artifact\_id** |  optional  | The ID of the artifact to run the playbook on \(requires artifact scope\) | numeric | 

#### Action Output
DATA PATH | TYPE | CONTAINS
--------- | ---- | --------
action\_result\.parameter\.delay\_purpose | string | 
action\_result\.parameter\.duration\_unit | string | 
action\_result\.parameter\.delay\_duration | numeric | 
action\_result\.parameter\.playbook | string | 
action\_result\.parameter\.playbook\_scope | string | 
action\_result\.parameter\.artifact\_id | numeric | 
action\_result\.status | string | 
action\_result\.message | string | 
summary\.total\_objects | numeric | 
summary\.total\_objects\_successful | numeric |   

## action: 'clear scheduled playbooks'
Remove all pending scheduled playbooks on a container

Type: **generic**  
Read only: **False**

This action is used to remove all pending scheduled playbooks for a container\. This is generally intended to be used to cancel execution if some exit criteria has been reached and any scheduled playbooks need to be suspended permanently\.

#### Action Parameters
PARAMETER | REQUIRED | DESCRIPTION | TYPE | CONTAINS
--------- | -------- | ----------- | ---- | --------
**cancellation\_reason** |  required  | A short comment on why the playbooks were cancelled | string | 
**container\_id** |  optional  | The ID of the container to cancel schedules for\. If an ID is not provided, the current container is assumed | string | 

#### Action Output
DATA PATH | TYPE | CONTAINS
--------- | ---- | --------
action\_result\.parameter\.cancellation\_reason | string | 
action\_result\.parameter\.container\_id | string | 
action\_result\.status | string | 
action\_result\.message | string | 
summary\.total\_objects | numeric | 
summary\.total\_objects\_successful | numeric |   

## action: 'on poll'
Execute scheduled playbooks if their delay period has expired\. Smaller intervals will result in more accurate schedules

Type: **generic**  
Read only: **False**

#### Action Parameters
No parameters are required for this action

#### Action Output
No Output
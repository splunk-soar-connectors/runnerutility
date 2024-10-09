# File: runner_connector.py
#
# Copyright (c) Mhike, 2022
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software distributed under
# the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND,
# either express or implied. See the License for the specific language governing permissions
# and limitations under the License.
#
#

import json
from datetime import datetime, timedelta
import requests

import phantom.app as phantom
from phantom.action_result import ActionResult


class RunnerConnector(phantom.BaseConnector):

    is_polling_action = False
    print_debug = None
    headers = {}
    session = None

    def __init__(self):
        super(RunnerConnector, self).__init__()
        return

    def __print(self, value, is_debug=False):
        if self.print_debug is None:
            self.print_debug = False
            try:
                self.print_debug = self.get_config()['debug']
            except Exception as e:
                self.debug_print("Exception occurred while getting debug key. Exception: {}".format(e))
        message = 'Failed to cast message to string'
        try:
            message = str(value)
        except Exception as e:
            self.debug_print("Exception occurred while converting message into string. Exception: {}".format(e))
            return
        if is_debug and not self.print_debug:
            return
        else:
            self.save_progress(message)
            self.debug_print(self.__class__.__name__, message)

    def _get_base_url(self):
        self.__print("_get_base_url()", is_debug=True)
        port = 443
        base_url = 'https://127.0.0.1'
        try:
            port = self.get_config()['https_port']
        except:
            pass
        try:
            base_url = self.get_config()['cluster_base_url']
        except:
            pass
        return f'{base_url}:{port}'

    def _get_rest_data(self, endpoint):
        try:
            url = f'{self._get_base_url()}/{endpoint}'
            self.__print(url, is_debug=True)
            if self.session:
                response = self.session.get(url, verify=False)
            else:
                response = phantom.requests.get(url, verify=False)
            content = json.loads(response.text)
            code = response.status_code
            if 199 < code < 300:
                if 'data' in content and 'container/' not in url:
                    return content['data']
                else:
                    return content
            else:
                return None
        except:
            return None

    def _post_rest_data(self, endpoint, dictionary):
        try:
            url = f'{self._get_base_url()}/{endpoint}'
            self.__print(url, is_debug=True)
            data = json.dumps(dictionary)
            if self.session:
                response = self.session.post(url, data=data, verify=False)
            else:
                response = phantom.requests.post(url, data=data, verify=False)
            content = response.text
            code = response.status_code
            if 199 < code < 300:
                if 'data' in content:
                    return content['data']
                else:
                    return content
            else:
                return None
        except:
            return None

    def _create_artifact(self, comment, unit, duration, playbook, scope, container, input_data):
        self.__print('_create_artifact()', is_debug=True)
        container_id = container
        if not container:
            container_id = self.get_container_id()
        artifact_dict = { "cef": { "comment": comment,
                                "durationUnit": unit,
                                "duration": duration,
                                "playbook": playbook,
                                "scope": scope },
                          "container_id": container_id,
                          "label": "pending",
                          "name": "scheduled playbook",
                          "source_data_identifier": f'runner-{datetime.utcnow()}-{self.get_container_id()}',
                          "run_automation": False }
        if input_data:
            artifact_dict["cef"]["inputs"] = input_data
        if comment and unit:
            self.__print(f'Posting artifact: {artifact_dict}', is_debug=True)
            uri = "rest/artifact"
            response = self._post_rest_data(uri, artifact_dict)
            if response is not None:
                return True
            else:
                return False
        else:
            return artifact_dict

    def _disable_artifact(self, container, reason):
        self.__print('_disable_artifact()', is_debug=True)
        uri = f'rest/container/{container}/artifacts?_filter_name=%22scheduled playbook%22&_filter_label=%22pending%22'
        response = self._get_rest_data(uri)
        update_data = {'label': 'halted'}
        for artifact in response['data']:
            update_data['cef'] = artifact['cef']
            update_data['cef']['exeComment'] = reason
            update_data['id'] = artifact['id']
            uri = f'rest/artifact/{artifact["id"]}'
            response = self._post_rest_data(uri, update_data)
        return

    def _add_waiting_tag(self):
        self.__print('_add_waiting_tag()', is_debug=True)
        uri = f'rest/container/{self.get_container_id()}'
        response = self._get_rest_data(uri)
        self.__print(response, is_debug=True)
        tags = response['tags']
        if 'waiting' not in tags:
            tags.append('waiting')
        update_data = {}
        update_data['tags'] = tags
        response = self._post_rest_data(uri, update_data)
        return

    def _delete_waiting_tag(self, container):
        self.__print('_delete_waiting_tag()', is_debug=True)
        uri = f'rest/container/{container}'
        response = self._get_rest_data(uri)
        tags = response['tags']
        if 'waiting' in tags:
            tags.remove('waiting')
        update_data = {}
        update_data['tags'] = tags
        response = self._post_rest_data(uri, update_data)
        return

    def _is_playbook_valid(self, artifact, container):
        self.__print('_is_playbook_valid()', is_debug=True)
        is_valid = False
        playbook = self._playbook_exists(artifact['cef']['playbook'])
        if playbook is not None and playbook != []:
            if container['label'] in playbook[0]['labels'] or "*" in playbook[0]['labels']:
                is_valid = True
        return is_valid

    def _playbook_exists(self, playbook):
        self.__print('_playbook_exists()', is_debug=True)
        playbook_json = None
        if '/' not in playbook:
            return playbook_json
        playbook_string = playbook.split('/')
        repo = playbook_string[0]
        playbook = playbook_string[1]
        uri = f'rest/scm?page_size=0&_filter_name="{repo}"'
        repo_data = self._get_rest_data(uri)
        if repo_data is not None and repo_data != []:
            uri = f'rest/playbook?page_size=1&_filter_name="{playbook}"&_filter_scm={repo_data[0]["id"]}'
            playbook_json = self._get_rest_data(uri)
        return playbook_json

    def _get_all_pending_artifacts(self):
        self.__print('_get_all_pending_artifacts()', is_debug=True)
        try:
            uri = 'rest/artifact?page_size=0&_filter_label="pending"&_filter_name__contains="scheduled playbook"'
            pending_artifacts = self._get_rest_data(uri)
            return pending_artifacts
        except Exception as e:
            self.__print('Failed to retrieved pending scheduled playbooks')
            self.__print(e)
            return None

    def _is_expired(self, artifact):
        self.__print('_is_expired()', is_debug=True)
        is_expired = False
        unit = artifact['cef']['durationUnit']
        duration = artifact['cef']['duration']
        if unit == 'Minutes':
            expiration = datetime.strptime(artifact['create_time'], '%Y-%m-%dT%H:%M:%S.%fZ') + timedelta(minutes=int(duration))
        elif unit == 'Hours':
            expiration = datetime.strptime(artifact['create_time'], '%Y-%m-%dT%H:%M:%S.%fZ') + timedelta(hours=int(duration))
        elif unit == 'Days':
            expiration = datetime.strptime(artifact['create_time'], '%Y-%m-%dT%H:%M:%S.%fZ') + timedelta(days=int(duration))
        self.__print(f'now: {datetime.utcnow()}', is_debug=True)
        self.__print(f'expiration: {expiration}', is_debug=True)
        self.__print(f'creation: {artifact["create_time"]}', is_debug=True)
        if expiration <= datetime.utcnow():
            is_expired = True
        return is_expired

    def _get_container(self, artifact):
        self.__print('_get_container()', is_debug=True)
        uri = f'rest/container/{artifact["container"]}'
        container = self._get_rest_data(uri)
        return container

    def _run_playbook(self, artifact):
        self.__print('_run_playbook()', is_debug=True)
        self.__print(artifact, is_debug=True)
        success = False
        uri = 'rest/playbook_run'
        try:
            container_id = int(artifact['container_id'])
        except:
            container_id = int(artifact['container'])
        data = {
                   "container_id": container_id,
                   "playbook_id": artifact['cef']['playbook'],
                   "scope": artifact['cef']['scope'],
                   "run": "true"
               }
        try:
            data['inputs'] = artifact['cef']['inputs']
        except:
            pass
        self.__print(data, is_debug=True)
        result = self._post_rest_data(uri, data)
        if result is not None:
            success = True
        return success, result

    def _is_playbook_pending(self, artifact):
        self.__print('_is_playbook_pending()', is_debug=True)
        is_playbook_pending = False
        uri = f'rest/container/{artifact["container"]}/artifacts?page_size=0&_filter_label="pending"&_filter_name__contains="scheduled playbook"'
        playbooks = self._get_rest_data(uri)
        if playbooks['data'] != []:
            is_playbook_pending = True
        return is_playbook_pending

    def _delete_tag(self, state, artifact):
        self.__print('_delete_tag()', is_debug=True)
        uri = f'rest/container/{artifact["container"]}'
        response = self._get_rest_data(uri)
        tags = []
        tags.extend(response['tags'])
        self.__print(tags, is_debug=True)
        if state in tags:
            tags.remove(state)
        update_data = {}
        update_data['tags'] = tags
        response = self._post_rest_data(uri, update_data)
        return

    def _update_artifact(self, state, artifact, result=None):
        self.__print('_update_artifact()', is_debug=True)
        update_data = {}
        update_data['cef'] = {}
        update_data['cef'].update(artifact['cef'])
        update_data['cef']['exeComment'] = f'Execution run at {datetime.utcnow()}'
        if result:
            update_data['cef']['rest_response'] = result
        update_data['label'] = state
        uri = f'rest/artifact/{artifact["id"]}'
        self._post_rest_data(uri, update_data)
        return

    def _handle_test_connectivity(self, param):
        self.__print("_handle_test_connectivity", is_debug=True)
        action_result = self.add_action_result(ActionResult(dict(param)))
        test_url = f'{self._get_base_url()}/rest/version'
        self.__print(f'Attempting http get for {test_url}')
        response = None
        try:
            if self.session:
                response = self.session.get(test_url, verify=False)
            else:
                response = phantom.requests.get(test_url, verify=False)
            self.__print(response.status_code, is_debug=True)
        except:
            pass
        if response and 199 < response.status_code < 300:
            version = json.loads(response.text)['version']
            self.__print(f'Successfully retrieved platform version: {version}')
            self.__print('Passed connection test')
            return action_result.set_status(phantom.APP_SUCCESS)
        else:
            self.__print(f'Failed to reach test url: {test_url}\nCheck your hostname config value')
            self.__print('Failed connection test')
            return action_result.set_status(phantom.APP_ERROR, f'Failed to reach test url {test_url}')

    def _process_input_data(self, param):
        input_data = None
        try:
            input_data = param.get('input_data')
            if input_data:
                try:
                    input_data = json.loads(input_data)
                except:
                    try:
                        temp = input_data.replace('\'', '"')
                        temp = json.loads(temp)
                        input_data = temp
                    except:
                        self.__print('Input data was provided but could not be loaded as json. Please check the input data format.')
                        self.set_status_save_progress(phantom.APP_ERROR, 'Artifact creation failed')
                        return phantom.APP_ERROR
        except:
            pass
        return input_data

    def _handle_count_runner_artifacts(self, param, action_result):
        url_params = ['_filter_name="scheduled playbook"',
                      'page_size=0']
        path_values = ['rest',
                       'container',
                       str(self.get_container_id()),
                       'artifacts']
        try:
            playbook_filter = param.get('playbook_filter')
            if playbook_filter:
                url_params.append(f'_filter_cef__playbook="{playbook_filter}"')
        except:
            pass
        try:
            label_filter = param.get('label_filter')
            if label_filter:
                url_params.append(f'_filter_label="{label_filter}"')
        except:
            pass
        endpoint = f'{"/".join(path_values)}?{"&".join(url_params)}'
        self.__print(endpoint, is_debug=True)
        artifact_count = None
        artifact_count = self._get_rest_data(endpoint)['count']
        if artifact_count is not None:
            action_result.add_data({'runner_artifact_count': artifact_count})
            self.__print(f"Runner artifact count: {artifact_count}", is_debug=True)
            action_result.set_status(phantom.APP_SUCCESS, 'Successfully completed artifact count')
            self.set_status_save_progress(phantom.APP_SUCCESS, 'Successfully completed artifact count')
            return phantom.APP_SUCCESS
        else:
            self.__print("Failed to retrieve runner artifact count")
            action_result.set_status(phantom.APP_ERROR)
            self.set_status_save_progress(phantom.APP_ERROR, 'Failed to retrieve runner artifact count')
            return phantom.APP_ERROR

    def _handle_schedule_playbook(self, param):
        self.__print('_handle_schedule_playbook()', is_debug=True)
        try:
            self.__print('Building standard delayed execution artifact', is_debug=True)
            comment = param.get('delay_purpose')
            unit = param.get('duration_unit')
            duration = param.get('delay_duration')
            playbook = param.get('playbook')
            scope = param.get('playbook_scope')
            container = None
            if scope == "artifact":
                ids = []
                ids.append(param.get('artifact_id'))
                scope = ids
            if "container" in scope:
                container = param.get('container_id')
                if "all" in scope:
                    scope = "all"
                elif "new" in scope:
                    scope = "new"
            input_data = self._process_input_data(param)
            if input_data == phantom.APP_ERROR:
                return phantom.APP_ERROR
            if not self._create_artifact(comment, unit, duration, playbook, scope, container, input_data):
                self.set_status_save_progress(phantom.APP_ERROR, 'Artifact creation failed')
                return phantom.APP_ERROR
            self._add_waiting_tag()
            self.set_status_save_progress(phantom.APP_SUCCESS, 'Successfully completed execution delay')
            return phantom.APP_SUCCESS
        except Exception as e:
            self.__print('_handle_schedule_playbook() failed')
            self.__print(e)
            self.set_status_save_progress(phantom.APP_ERROR, e)
            return phantom.APP_ERROR

    def _handle_execute_playbook(self, param):
        self.__print('_handle_execute_playbook()', is_debug=True)
        try:
            self.__print('Parsing input fields', is_debug=True)
            playbook = param.get('playbook')
            scope = param.get('playbook_scope')
            container = None
            if scope == "artifact":
                ids = []
                ids.append(param.get('artifact_id'))
                scope = ids
            if "container" in scope:
                container = param.get('container_id')
                if "all" in scope:
                    scope = "all"
                elif "new" in scope:
                    scope = "new"
            input_data = self._process_input_data(param)
            if input_data == phantom.APP_ERROR:
                return phantom.APP_ERROR
            execution_data = self._create_artifact(None, None, None, playbook, scope, container, input_data)
            if not self._run_playbook(execution_data):
                self.set_status_save_progress(phantom.APP_ERROR, 'Playbook execution failed')
                return phantom.APP_ERROR
            self.set_status_save_progress(phantom.APP_SUCCESS, 'Successfully completed execution')
            return phantom.APP_SUCCESS
        except Exception as e:
            self.__print('_handle_execute_playbook() failed')
            self.__print(e)
            self.set_status_save_progress(phantom.APP_ERROR, e)
            return phantom.APP_ERROR

    def _handle_clear_scheduled_playbooks(self, param):
        self.__print('_handle_clear_scheduled_playbooks()', is_debug=True)
        try:
            self.__print('Removing execution parameters', is_debug=True)
            reason = param.get('cancellation_reason')
            container_identifier = param.get('container_id')
            if container_identifier is None or container_identifier == '':
                container_identifier = self.get_container_id()
            self._delete_waiting_tag(container_identifier)
            self._disable_artifact(container_identifier, reason)
            self.set_status_save_progress(phantom.APP_SUCCESS, 'Successfully halted execution')
            return phantom.APP_SUCCESS
        except Exception as e:
            self.__print('_handle_clear_scheduled_playbooks() failed')
            self.__print(e)
            self.set_status_save_progress(phantom.APP_ERROR, e)
            return phantom.APP_ERROR

    def _handle_on_poll(self, param):
        self.__print('_handle_on_poll()', is_debug=True)
        self.is_polling_action = True
        action_result = self.add_action_result(ActionResult(dict(param)))
        try:
            limit = int(self.get_config()['playbook_limit'])
        except:
            limit = 4
        try:
            executions = 0
            for artifact in self._get_all_pending_artifacts():
                self.__print(f'Processing artifact {artifact["id"]}', is_debug=True)
                container = self._get_container(artifact)
                if self._is_expired(artifact):
                    self.__print(f'artifact {artifact["id"]} is expired', is_debug=True)
                    if self._is_playbook_valid(artifact, container):
                        self.__print('playbook is valid', is_debug=True)
                        executions += 1
                        result = self._run_playbook(artifact)
                        self._update_artifact('complete', artifact, result=result)
                    else:
                        self.__print(f'playbook is invalid: {artifact["cef"]["playbook"]}')
                        self._update_artifact('invalid playbook', artifact)
                    if self._is_playbook_pending(artifact):
                        self.__print('playbooks pending', is_debug=True)
                    else:
                        self.__print('no playbooks pending', is_debug=True)
                        self._delete_tag('waiting', artifact)
                else:
                    self.__print(f'artifact {artifact["id"]} is not expired yet', is_debug=True)
                if executions > limit:
                    break
            self.__print(f'{executions} playbooks executed')
            action_result.set_status(phantom.APP_SUCCESS, f'{executions} playbooks executed')
        except Exception as e:
            self.__print('Error processing artifacts and playbooks')
            self.__print(e)
            self.set_status(phantom.APP_ERROR, 'Error processing artifacts and playbooks')
            return phantom.APP_ERROR

    def initialize(self):
        config = self.get_config()
        try:
            self.print_debug = config['print_debug']
        except Exception as e:
            self.__print(f'Exception occurred while getting debug key. Exception: {e}')
            self.print_debug = False
        try:
            token = config['cluster_api_token']
            self.headers = {"ph-auth-token": token}
        except:
            self.__print('No api token provided. Using phantom.requests')
            self.headers = {}
        if self.headers:
            self.session = requests.Session()
            self.session.headers = self.headers
        return phantom.APP_SUCCESS

    def handle_action(self, param):
        ret_val = phantom.APP_SUCCESS

        action_id = self.get_action_identifier()
        self.__print(f"action_id: {self.get_action_identifier()}")

        action_result = self.add_action_result(ActionResult(dict(param)))

        if action_id == 'schedule_playbook':
            ret_val = self._handle_schedule_playbook(param)

        if action_id == 'execute_playbook':
            ret_val = self._handle_execute_playbook(param)

        if action_id == 'clear_scheduled_playbooks':
            ret_val = self._handle_clear_scheduled_playbooks(param)

        if action_id == 'count_runner_artifacts':
            ret_val = self._handle_count_runner_artifacts(param, action_result)

        if action_id == 'on_poll':
            ret_val = self._handle_on_poll(param)

        if action_id == 'test_connectivity':
            ret_val = self._handle_test_connectivity(param)

        return ret_val

# coding: utf-8
#
# Copyright 2014 The Oppia Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS-IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

__author__ = 'Sean Lip'

from core.domain import exp_domain
from core.domain import exp_services
from core.domain import event_services
from core.domain import stats_domain
from core.domain import stats_services
from core.tests import test_utils
import feconf


# TODO(bhenning): Make sure this tests the new state answer stats domain object
# as well, or better, than the previous tests tested the old answer stats
# domain object.
class StateAnswersTests(test_utils.GenericTestBase):
    """Test the state answers domain object."""

    def test_record_answer(self):
        self.save_new_default_exploration('eid', 'fake@user.com')
        exp = exp_services.get_exploration_by_id('eid')

        FIRST_STATE_NAME = exp.init_state_name
        SECOND_STATE_NAME = 'State 2'
        exp_services.update_exploration('fake@user.com', 'eid', [{
            'cmd': exp_domain.CMD_EDIT_STATE_PROPERTY,
            'state_name': FIRST_STATE_NAME,
            'property_name': exp_domain.STATE_PROPERTY_INTERACTION_ID,
            'new_value': 'TextInput',
        }, {
            'cmd': exp_domain.CMD_ADD_STATE,
            'state_name': SECOND_STATE_NAME,
        }, {
            'cmd': exp_domain.CMD_EDIT_STATE_PROPERTY,
            'state_name': SECOND_STATE_NAME,
            'property_name': exp_domain.STATE_PROPERTY_INTERACTION_ID,
            'new_value': 'TextInput',
        }], 'Add new state')
        exp = exp_services.get_exploration_by_id('eid')

        SESSION_ID = 'SESSION_ID'
        TIME_SPENT = 5.0
        exp_version = exp.version
        PARAMS = {}

        for state_name in [FIRST_STATE_NAME, SECOND_STATE_NAME]:
            state_answers = stats_services.get_state_answers(
                'eid', exp_version, state_name)
            self.assertEquals(state_answers, None)

        # answer is a string
        event_services.AnswerSubmissionEventHandler.record(
            'eid', exp_version, FIRST_STATE_NAME, 0, 0,
            exp_domain.HARD_RULE_CLASSIFICATION, 'sid1', TIME_SPENT, PARAMS,
            'answer1')
        event_services.AnswerSubmissionEventHandler.record(
            'eid', exp_version, FIRST_STATE_NAME, 0, 1,
            exp_domain.HARD_RULE_CLASSIFICATION, 'sid2', TIME_SPENT, PARAMS,
            'answer1')
        # answer is a dict
        event_services.AnswerSubmissionEventHandler.record(
            'eid', exp_version, FIRST_STATE_NAME, 1, 0,
            exp_domain.HARD_RULE_CLASSIFICATION, 'sid1', TIME_SPENT, PARAMS,
            {'x': 1.0, 'y': 5.0})
        # answer is a list
        event_services.AnswerSubmissionEventHandler.record(
            'eid', exp_version, SECOND_STATE_NAME, 2, 0,
            exp_domain.HARD_RULE_CLASSIFICATION, 'sid3', TIME_SPENT, PARAMS,
            [2, 4, 8])
        # answer is a unicode string
        event_services.AnswerSubmissionEventHandler.record(
            'eid', exp_version, SECOND_STATE_NAME, 1, 1,
            exp_domain.HARD_RULE_CLASSIFICATION, 'sid4', TIME_SPENT, PARAMS,
            self.UNICODE_TEST_STRING)

        expected_answers_list1 = [{
            'answer': 'answer1', 'time_spent_in_sec': 5.0,
            'answer_group_index': 0, 'rule_spec_index': 0,
            'classification_categorization': 'hard_rule', 'session_id': 'sid1',
            'interaction_id': 'TextInput', 'params': {}
        }, {
            'answer': 'answer1', 'time_spent_in_sec': 5.0,
            'answer_group_index': 0, 'rule_spec_index': 1,
            'classification_categorization': 'hard_rule', 'session_id': 'sid2',
            'interaction_id': 'TextInput', 'params': {}
        }, {
            'answer': {'x': 1.0, 'y': 5.0}, 'time_spent_in_sec': 5.0,
            'answer_group_index': 1, 'rule_spec_index': 0,
            'classification_categorization': 'hard_rule', 'session_id': 'sid1',
            'interaction_id': 'TextInput', 'params': {}
        }]
        expected_answers_list2 = [{
            'answer': [2, 4, 8], 'time_spent_in_sec': 5.0,
            'answer_group_index': 2, 'rule_spec_index': 0,
            'classification_categorization': 'hard_rule', 'session_id': 'sid3',
            'interaction_id': 'TextInput', 'params': {}
        }, {
            'answer': self.UNICODE_TEST_STRING, 'time_spent_in_sec': 5.0,
            'answer_group_index': 1, 'rule_spec_index': 1,
            'classification_categorization': 'hard_rule', 'session_id': 'sid4',
            'interaction_id': 'TextInput', 'params': {}
        }]

        state_answers = stats_services.get_state_answers(
            'eid', exp_version, FIRST_STATE_NAME)
        self.assertEquals(state_answers.answers_list, expected_answers_list1)

        state_answers = stats_services.get_state_answers(
            'eid', exp_version, SECOND_STATE_NAME)
        self.assertEquals(state_answers.answers_list, expected_answers_list2)

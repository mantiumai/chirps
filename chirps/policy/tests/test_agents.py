"""Tests for the LLM agents."""

from unittest.mock import patch

from account.models import Profile
from asset.providers.api_endpoint import APIEndpointAsset
from django.contrib.auth.models import User
from django.test import TestCase
from langchain.chat_models import ChatOpenAI
from langchain.schema import AIMessage
from policy.llms.agents import AttackAgent
from policy.models import MultiQueryRule, Policy, PolicyVersion
from severity.models import Severity


class MultiQueryRuleTestCase(TestCase):
    def setUp(self):
        # Create a test user with a known username, password, and API keys for both OpenAI and Cohere
        self.test_username = 'testuser'
        self.test_password = 'testpassword'
        self.test_openai_key = 'fake_openai_key'
        self.test_cohere_key = 'fake_cohere_key'

        self.user = User.objects.create_user(
            username=self.test_username, password=self.test_password, email='testuser@example.com'
        )
        self.user.save()

        # Create a profile for the test user
        self.profile = Profile.objects.create(user=self.user)

        self.profile.openai_key = self.test_openai_key
        self.profile.cohere_key = self.test_cohere_key
        self.profile.save()

        self.severity = Severity.objects.create(
            name='Test Severity',
            value=1,
            color='#FF0000',
        )

        self.policy = Policy.objects.create(
            name='Test Policy',
            description='Test Description',
            user=self.user,
        )

        self.policy_version = PolicyVersion.objects.create(number=1, policy=self.policy)

        self.rule = MultiQueryRule.objects.create(
            name='Test MultiQuery Rule',
            task_description='Test task description',
            success_outcome='Test success outcome',
            severity=self.severity,
            policy=self.policy_version,
        )

        # Set up the APIEndpointAsset object with the necessary parameters
        self.api_endpoint_asset = APIEndpointAsset.objects.create(
            description='Test API Endpoint',
            url='https://example.com/api',
            authentication_method='Bearer',
            api_key='test_api_key',
            headers='{"Content-Type": "application/json"}',
            body='{"data": "%query%"}',
        )

    def test_create_multiquery_rule(self):
        self.assertEqual(self.rule.name, 'Test MultiQuery Rule')
        self.assertEqual(self.rule.task_description, 'Test task description')
        self.assertEqual(self.rule.success_outcome, 'Test success outcome')
        self.assertEqual(self.rule.severity, self.severity)
        self.assertEqual(self.rule.policy, self.policy_version)

    def test_execute(self):
        class MockModel:
            def __call__(self, message_history):
                return AIMessage(content='Test attack')

        class MockChatOpenAI(ChatOpenAI):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                self.model_name = 'test-model'

            def get_model(self):
                return MockModel()

        def mock_openai_create(*args, **kwargs):
            # Define a mock response here
            response = {
                'id': 'test-id',
                'object': 'chat.completion',
                'created': 1234567890,
                'model': 'test-model',
                'usage': {'prompt_tokens': 10, 'completion_tokens': 10, 'total_tokens': 20},
                'choices': [
                    {
                        'message': {
                            'role': 'assistant',
                            'content': 'Test attack',
                        },
                        'index': 0,
                        'logprobs': None,
                        'finish_reason': 'stop',
                    }
                ],
            }
            return response

        with patch('openai.api_resources.chat_completion.ChatCompletion.create', side_effect=mock_openai_create):
            with self.subTest('Test execute with mocked ChatOpenAI and Model'):
                instructions = 'Test instructions'
                model_name = 'test-model'
                model = MockChatOpenAI(openai_api_key=self.user.profile.openai_key, model_name=model_name)
                asset = self.api_endpoint_asset
                attacker = AttackAgent(model, asset.description, self.rule.task_description, instructions)
                attacker.reset()
                self.assertEqual(len(attacker.message_history), 1)
                self.assertEqual(attacker.message_history[0].content, instructions)

                attack = attacker.generate_attack(target_response='Test target response')
                self.assertEqual(attack, 'Test attack')
                self.assertEqual(len(attacker.message_history), 3)

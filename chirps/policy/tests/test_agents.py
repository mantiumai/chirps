# Test the Agent classes.
from unittest.mock import patch

from account.models import Profile
from django.contrib.auth.models import User
from django.test import TestCase
from langchain.chat_models import ChatOpenAI
from langchain.schema import AIMessage
from policy.llms.agents import AttackAgent, EvaluationAgent


class AgentTestCase(TestCase):
    """Test the Agent classes."""

    def mock_openai_create(*args, content, **kwargs):
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
                        'content': content,
                    },
                    'index': 0,
                    'logprobs': None,
                    'finish_reason': 'stop',
                }
            ],
        }
        return response

    def setUp(self):
        """Set up the test case."""
        # Create a test user with a known username, password, and API keys for both OpenAI and Cohere
        self.user = User.objects.create_user(username='testuser', password='testpassword', email='testuser@example.com')
        self.user.save()

        # Create a profile for the test user
        self.profile = Profile.objects.create(user=self.user)

        self.profile.openai_key = 'fake_openai_key'
        self.profile.cohere_key = 'fake_cohere_key'
        self.profile.save()

        self.instructions = 'Test instructions'
        self.target_job_description = 'Test target job description'
        self.objective = 'Test objective'

        class MockModel:
            """Mock Model class."""

            def __call__(self, message_history):
                return AIMessage(content='Test attack')

        class MockChatOpenAI(ChatOpenAI):
            """Mock ChatOpenAI class."""

            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                self.model_name = 'test-model'

            def get_model(self):
                """Return a mock model."""
                return MockModel()

        self.model = MockChatOpenAI(openai_api_key=self.user.profile.openai_key, model_name='test-model')

    @patch('openai.api_resources.chat_completion.ChatCompletion.create')
    def test_attack_agent(self, mock_openai_create):
        """Test the AttackAgent class."""
        mock_openai_create.side_effect = lambda *args, **kwargs: self.mock_openai_create(
            *args, content='Test attack', **kwargs
        )
        agent = AttackAgent(self.model, self.target_job_description, self.objective, self.instructions)

        with self.subTest('Test AttackAgent initialization'):
            self.assertEqual(agent.instructions, self.instructions)
            self.assertEqual(agent.message_history[0].content, self.instructions)

        with self.subTest('Test AttackAgent reset'):
            agent.reset()
            self.assertEqual(len(agent.message_history), 1)
            self.assertEqual(agent.message_history[0].content, self.instructions)

        with self.subTest('Test AttackAgent truncate'):
            agent.message_history.append(AIMessage(content='Test question'))
            agent.message_history.append(AIMessage(content='Test target response'))
            agent.message_history.append(AIMessage(content='Test attack'))
            agent.message_history.append(AIMessage(content='Test response'))
            agent.truncate()
            self.assertEqual(len(agent.message_history), 3)
            self.assertEqual(agent.message_history[1].content, 'Test attack')

        with self.subTest('Test AttackAgent generate_attack'):
            attack = agent.generate_attack(target_response='Test target response')
            self.assertEqual(attack, 'Test attack')
            self.assertEqual(len(agent.message_history), 5)

    @patch('openai.api_resources.chat_completion.ChatCompletion.create')
    def test_evaluation_agent(self, mock_openai_create):
        """Test the EvaluationAgent class."""
        mock_openai_create.side_effect = lambda *args, **kwargs: self.mock_openai_create(*args, content='Yes', **kwargs)
        success_outcome = 'Test success outcome'
        agent = EvaluationAgent(self.model, success_outcome)

        with self.subTest('Test EvaluationAgent initialization'):
            self.assertEqual(agent.message_history[0].content, agent.instructions)

        with self.subTest('Test EvaluationAgent reset'):
            agent.reset()
            self.assertEqual(len(agent.message_history), 1)
            self.assertEqual(agent.message_history[0].content, agent.instructions)

        with self.subTest('Test EvaluationAgent evaluate'):
            evaluation = agent.evaluate(target_response='Test target response')
            self.assertEqual(evaluation, 'Yes')
            self.assertEqual(len(agent.message_history), 2)

import datetime
from django.test import TestCase, SimpleTestCase, TransactionTestCase, LiveServerTestCase
from django.utils import timezone
from django.urls import reverse
from .models import Question, Choice

def create_question(question_text, days):
    time = timezone.now() + datetime.timedelta(days=days)
    return Question.objects.create(question_text=question_text, pub_date=time)


class QuestionModelTests(TestCase):
    def test_was_published_recently_with_future_question(self):
        time = timezone.now() + datetime.timedelta(days=30)
        future_question = Question(pub_date=time)
        self.assertIs(future_question.was_published_recently(), False)

    def test_was_published_recently_with_old_question(self):
        time = timezone.now() - datetime.timedelta(days=1, seconds=1)
        old_question = Question(pub_date=time)
        self.assertIs(old_question.was_published_recently(), False)


class PollsURLTests(TestCase):
    def test_polls_index_url(self):
        response = self.client.get('/polls/')
        self.assertEqual(response.status_code, 200)


class VoteTransactionTests(TransactionTestCase):
    def test_vote_increases_count(self):
        question = Question.objects.create(question_text="Test Question", pub_date=timezone.now())
        choice = Choice.objects.create(question=question, choice_text="Test Choice", votes=0)
        
        response = self.client.post(reverse("polls:vote", args=(question.id,)), {"choice": choice.id})
        
        choice.refresh_from_db()
        self.assertEqual(choice.votes, 1)
        self.assertEqual(response.status_code, 302)


class PollsLiveServerTests(LiveServerTestCase):
    def test_index_page_loads(self):
        response = self.client.get(self.live_server_url + '/polls/')
        self.assertEqual(response.status_code, 200)

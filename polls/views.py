from django.db.models import F
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views import generic
from django.utils import timezone
from .models import Choice, Question


class IndexView(generic.ListView):
    template_name = "polls/index.html"
    context_object_name = "latest_question_list"

    def get_queryset(self):
        """
        Return the last five published questions (not including those set to be
        published in the future).
        """
        return Question.objects.filter(
            pub_date__lte=timezone.now()
        ).order_by("-pub_date")[:5]


class DetailView(generic.DetailView):
    model = Question
    template_name = "polls/detail.html"
    
    def get_queryset(self):
        """
        Excludes any questions that aren't published yet.
        """
        return Question.objects.filter(pub_date__lte=timezone.now())


class ResultsView(generic.DetailView):
    model = Question
    template_name = "polls/results.html"


def vote(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    try:
        selected_choice = question.choice_set.get(pk=request.POST["choice"])
    except (KeyError, Choice.DoesNotExist):
        # Redisplay the question voting form.
        return render(
            request,
            "polls/detail.html",
            {
                "question": question,
                "error_message": "You didn't select a choice.",
            },
        )
    else:
        selected_choice.votes = F("votes") + 1
        selected_choice.save()
        return HttpResponseRedirect(reverse("polls:results", args=(question.id,)))

from django.test import TestCase
from django.http import HttpResponse
from .tests import QuestionModelTests, PollsURLTests, VoteTransactionTests, PollsLiveServerTests
import io
import sys

def run_tests_view(request):
    """Run all tests and show results in browser"""
    
    # Capture output
    old_stdout = sys.stdout
    sys.stdout = captured_output = io.StringIO()
    
    # Run tests
    import unittest
    suite = unittest.TestSuite()
    
    # Add all test classes
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(QuestionModelTests))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(PollsURLTests))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(VoteTransactionTests))
    suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(PollsLiveServerTests))
    
    # Run tests
    runner = unittest.TextTestRunner(stream=captured_output, verbosity=2)
    result = runner.run(suite)
    
    # Restore stdout
    sys.stdout = old_stdout
    
    # Get output
    test_output = captured_output.getvalue()
    
    # Format HTML response
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Test Results</title>
        <style>
            body {{ font-family: monospace; margin: 20px; background: #f5f5f5; }}
            .container {{ background: white; padding: 20px; border-radius: 5px; }}
            .passed {{ color: green; }}
            .failed {{ color: red; }}
            pre {{ background: #f0f0f0; padding: 10px; overflow: auto; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Django Test Results</h1>
            <h2>Total Tests: {result.testsRun}</h2>
            <p class="passed">✅ Passed: {result.testsRun - len(result.failures) - len(result.errors)}</p>
            <p class="failed">❌ Failures: {len(result.failures)}</p>
            <p class="failed">⚠️ Errors: {len(result.errors)}</p>
            <h3>Test Output:</h3>
            <pre>{test_output}</pre>
            <br>
            <a href="/polls/">← Back to Polls</a>
        </div>
    </body>
    </html>
    """
    return HttpResponse(html)

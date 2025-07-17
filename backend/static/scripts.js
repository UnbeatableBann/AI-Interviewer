document.getElementById('start-interview-form').addEventListener('submit', async (event) => {
    event.preventDefault();
    const userId = document.getElementById('user_id').value;
    const jobProfileId = document.getElementById('job_profile_id').value;

    const response = await fetch('/start-interview', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ user_id: userId, job_profile_id: jobProfileId })
    });

    if (response.ok) {
        document.getElementById('start-interview-form').style.display = 'none';
        document.getElementById('question-section').style.display = 'block';
        loadNextQuestion(jobProfileId);
    } else {
        alert('Failed to start interview.');
    }
});

async function loadNextQuestion(jobProfileId) {
    const response = await fetch(`/get_next_questions?job_profile_id=${jobProfileId}`);
    const data = await response.json();

    if (data.length > 0) {
        const question = data[0];
        document.getElementById('question-text').textContent = question.question_text;
        document.getElementById('submit-response').onclick = () => submitResponse(question.id);
    } else {
        alert('No more questions available.');
        document.getElementById('question-section').style.display = 'none';
    }
}

async function submitResponse(questionId) {
    const interviewId = 'dummy-interview-id'; // Replace with actual interview ID logic
    const transcript = document.getElementById('response').value;

    const response = await fetch('/submit-response', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ interview_id: interviewId, question_id: questionId, transcript })
    });

    const data = await response.json();
    alert(`Score: ${data.score}\nFeedback: ${data.feedback}`);
    if (data.next_question) {
        document.getElementById('response').value = '';
        document.getElementById('question-text').textContent = data.next_question.question;
        document.getElementById('submit-response').onclick = () => submitResponse(data.next_question.question_id);
    } else {
        alert('Interview completed!');
        document.getElementById('question-section').style.display = 'none';
    }
}

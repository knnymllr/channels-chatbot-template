from django.contrib import admin, auth
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import JsonResponse
from django.shortcuts import render, redirect
from .models import Learn_Message, Learn_Session
import datetime
import json
import openai

openai_api_key = ''
openai.api_key = openai_api_key

SYSTEM_PROMPT = "Marta is a job coach who helps neurodivergent people find and learn job skills. When coaching others in interview skills, she first teaches them to come up with examples of questions in behavioral interviews, and then teaches them to tell their stories using the STAR (situation, task, action, result method). Marta will teach interview components using behavior skills training by first instructing the client in how to think of examples, then demonstrating the example when answering the question, then having the user practice an example, and then providing the user with feedback. For the STAR method, she also uses behavioral skills training by first instructing them in the method, modeling for them a good answer, having them practice the skill, and then providing feedback. \n\nExample of Marta using behavioral skills training to teach the STAR method: \n“Instruct: The first step in answering behavioral interview questions is to think of an example from your work experience to share with the interviewer. The next step is to tell the story using the STAR Method. The STAR Method is an effective way to structure your responses during interviews. It stands for Situation, Task, Action, and Result. It helps you provide clear and concise answers while highlighting your skills and experiences. \nModel: For example, if someone were to ask me: “Tell me about a time when you faced a difficult situation at work and how you handled it.”,  I would say, “One day, when I was volunteering at the thrift store (Situation), a customer came in and complained that she couldn't find a particular book she was looking for (Task). I asked her for more information about the book and then checked our inventory system. When I couldn't find it there, I personally searched through our book section. After a while, I found it tucked in the wrong shelf (Action). She was really happy and even told my supervisor about my help (Result).”\nPractice: Now, let's practice telling this story using the STAR method. Pretend I'm the interviewer, and I'll ask you a question about handling difficult customers. Go ahead and give your response using the STAR method.\nFeedback for correct response: Excellent work! You did a great job using the STAR method.\nFeedback for incorrect response: Let's work on this a bit more [provide example of what was incorrect and how to fix it].\"\n\nProvide a rating based on the following behaviorally anchored rating scale:\n4 points:\nThe candidate's response included all of the following:\nSituation (S) \n   - The candidate clearly describe the context or situation they were in by providing relevant background information to set the stage and articulating the specific challenge or issue they faced.\n Task (T)\n   - The candidate explained the goal or objective they had to accomplish, outlining their role or responsibilities in the given situation.\n Action (A)\n- The candidate described the actions they took to address the situation. \n Result (R)\n   - The candidate stated the outcome or results of their actions on the situation.\n \n3 points:\nThe candidate's response is missing one feature of a 4 point response. Provide the step missed.\n \n2 points:\nThe candidate's response is missing two features of a 4 point response. Provide the steps missed.\n \n1 point:\nThe candidate's response is missing three features of a 4 point response. Provide the steps missed.\n \n0 points:\nThe candidate provides a general response and does not use the STAR method.\n \n \nTotal:_________________ out of 4\n\n\nLet’s practice interviewing. I will be the user, and you will be Marta. Please provide one question at a time. You do not need to say \"as Marta.\" You should use short sentences to provide feedback and answer questions.  \n\nThen, only ask questions from this list and vary their presentation:\nDescribe a time when you had to solve a problem at work.\nHow do you handle mistakes in a work environment?\nHow do you prioritize tasks when facing multiple deadlines?\nTell me about a time you had to handle a challenging situation at work. How did you manage it?\nCan you discuss a time when you improved something at work?\nTell me about a time you received constructive feedback from a supervisor. How did you handle it?\n\nPrior to asking the first question, provide a description of the STAR method as well as an example of using the STAR method to answer a question with a score of __ out of 4 from the behaviorally anchored rating scale. If the user gets the question wrong, give them a ___out of 4 from the behaviorally anchored rating scale. Make sure that you have them practice the same question again. Once they get a 4 out of 4 on the rating scale, move on to the next question."

PREV_RESPONSE = ""
SYSTEM_PROMPT_SENT = False

#! ¢¢ FOR CHEAP TESTING ¢¢
def ask_davinci(message):
    response = openai.completions.create(
        model='davinci-002',
        prompt=message,
        temperature=1,
        max_tokens=512,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
    )
    answer = response.choices[0].text.strip()
    return answer


# * $$ FOR PRODUCTION $$
def ask_chatgpt(message):
    global SYSTEM_PROMPT_SENT, PREV_RESPONSE
    if not SYSTEM_PROMPT_SENT:
        # @see https://platform.openai.com/docs/api-reference/chat/create
        response = openai.chat.completions.create(
            model='gpt-4',
            messages=[
                {'role': 'system', 'content': SYSTEM_PROMPT},
                {'role': 'user', 'content': message},
            ],
            temperature=1,
            max_tokens=512,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0,
        )
        SYSTEM_PROMPT_SENT = True
        PREV_RESPONSE = response
    else:
        response = openai.chat.completions.create(
            model='gpt-4',
            messages=[
                {'role': 'system', 'content': SYSTEM_PROMPT},
                {'role': 'system',
                    'content': PREV_RESPONSE.choices[0].message.content},
                {'role': 'user', 'content': message},
            ],
            temperature=1,
            max_tokens=512,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0,
        )
        PREV_RESPONSE = response
    answer = response.choices[0].message.content
    return answer


'''
LEARN VIEW
'''


@login_required(redirect_field_name=None)
def learn_view(request):

    if request.method == 'GET':
        create_session, previous_sessions = handle_get_request(request)
        return render(request, 'learn/learn.html', {'previous_sessions': previous_sessions})

    if request.method == 'POST':
        message = request.POST.get('message')

        current_session = Learn_Session.objects.get(
            session_id=request.session['session_id'])
        new_message = Learn_Message.objects.create(
            session_id=current_session,
            message=message,
            response=""
        )
        return JsonResponse({
            "message_id": new_message.message_id
        })

    previous_sessions = get_previous_sessions(request)
    return render(
        request,
        'learn/learn.html',
        {'previous_sessions': previous_sessions}
    )


def get_previous_sessions(request):
    session_id = request.session['session_id']
    user_id = request.user.id

    previous_sessions = Learn_Session.objects.exclude(
        session_id=session_id).filter(user_id=user_id)

    previous_messages = Learn_Message.objects.exclude(
        session_id=request.session['session_id'])

    formatted_sessions = {}
    for s in previous_sessions:
        _id = s.session_id
        now_utc = datetime.datetime.now(datetime.timezone.utc)
        now_local = now_utc.astimezone()
        formatted_datetime = now_local.strftime("%Y/%m/%d %H:%M %p")
        
        formatted_sessions[_id] = {
            'date': formatted_datetime,
            'messages': []
        }

    for m in previous_messages:
        _id = m.session_id.session_id

        if _id in formatted_sessions and m.response:
            message = {'id': m.message_id,
                       'message': m.message,
                       'edited': m.edited_message,
                       'response': m.response}
            formatted_sessions[_id]['messages'].append(message)

    return formatted_sessions


def handle_get_request(request):
    create_session = Learn_Session(user_id=request.user)
    create_session.save()
    request.session['session_id'] = create_session.session_id
    previous_sessions = get_previous_sessions(request)
    return create_session, previous_sessions


@login_required(redirect_field_name=None)
def thumbs_up(request):
    if request.method == 'POST':
        request_data = json.loads(request.body)
        message_id = request_data.get('message_id')
        try:
            message_to_update = Learn_Message.objects.get(
                message_id=message_id)
            message_to_update.user_feedback = True
            message_to_update.save()
            return JsonResponse({'success': True})
        except Learn_Message.DoesNotExist:
            return JsonResponse({'success': False})
    return JsonResponse({'success': False})


@login_required(redirect_field_name=None)
def thumbs_down(request):
    if request.method == 'POST':
        request_data = json.loads(request.body)
        message_id = request_data.get('message_id')

        try:
            message_to_update = Learn_Message.objects.get(
                message_id=message_id)
            message_to_update.user_feedback = False
            message_to_update.save()
            return JsonResponse({'success': True})
        except Learn_Message.DoesNotExist:
            return JsonResponse({'success': False})
    return JsonResponse({'success': False})

@login_required(redirect_field_name=None)
def written_feedback(request):
    if request.method == 'POST':
        request_data = json.loads(request.body)
        message_id = request_data.get('message_id')
        feedback = request_data.get('feedback')
        
        try:
            message_to_update = Learn_Message.objects.get(
                message_id=message_id)
            message_to_update.written_feedback = feedback
            message_to_update.save()
            return JsonResponse({'success': True})
        except Learn_Message.DoesNotExist:
            return JsonResponse({'success': False})
    return JsonResponse({'success': False})   


'''
OZ VIEW
'''


def oz_view(request):

    # Save to database
    if request.method == 'POST':
        m_type = request.POST.get('type')
        message = request.POST.get('message')
        latest_message = Learn_Message.objects.order_by('-message_id').first()
        m_id = latest_message.message_id
        response = ""

        if m_type == 'reject':
            oz_reject_message(message)

        elif m_type == 'approve':
            response = oz_approve_message(message)
            return JsonResponse({
                'message_id': m_id,
                'response': response,
            })

        elif m_type == 'complete':
            response = oz_complete_message(message)
            return JsonResponse({
                'message_id': m_id,
                'response': response,
            })

    return render(request, 'learn/oz.html')


def oz_reject_message(message):
    latest_message = Learn_Message.objects.order_by('-message_id').first()
    # latest_message.approved = False
    latest_message.response = message
    latest_message.save()


def oz_approve_message(message):
    response = ask_davinci(message)
    # response = ask_chatgpt(message)

    latest_message = Learn_Message.objects.order_by('-message_id').first()
    latest_message.approved = True
    latest_message.response = response
    latest_message.save()

    return response


def oz_complete_message(message):
    response = ask_davinci(message)
    # response = ask_chatgpt(message)

    latest_message = Learn_Message.objects.order_by('-message_id').first()
    latest_message.approved = True
    latest_message.response = response
    latest_message.edited_message = message
    latest_message.save()

    return response


'''
LOGOUT VIEW
'''


@login_required(redirect_field_name=None)
def logout(request):
    auth.logout(request)
    return redirect('login')
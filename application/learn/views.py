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

SYSTEM_PROMPT = "Please only discuss board games."

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
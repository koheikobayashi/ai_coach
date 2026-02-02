import json
import logging
from datetime import date

import requests
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST

from .forms import TrainingRecordForm

logger = logging.getLogger(__name__)


@login_required
def ai_coach(request):
    return render(request, 'coach/ai_coach.html')


@login_required
def ai_coach_api(request):
    """GASからトレーニング記録を取得し、Difyに送ってアドバイスを受け取る"""
    api_key = settings.DIFY_API_KEY
    if not api_key:
        return JsonResponse({'error': 'DIFY_API_KEYが設定されていません。'}, status=500)

    # GASからトレーニング記録を取得
    records = []
    gas_url = settings.GAS_GET_URL
    if gas_url:
        try:
            params = {'user': request.user.username}
            resp = requests.get(gas_url, params=params, timeout=10)
            resp.raise_for_status()
            records = resp.json()
        except (requests.RequestException, json.JSONDecodeError, ValueError):
            logger.exception('GAS GET failed in ai_coach_api')

    # 記録をテキストにまとめる
    if records:
        lines = []
        for r in records:
            parts = []
            if r.get('date'):
                parts.append(r['date'])
            if r.get('exercise'):
                parts.append(r['exercise'])
            if r.get('sets'):
                parts.append(f"{r['sets']}セット")
            if r.get('weight'):
                parts.append(f"{r['weight']}kg")
            if r.get('reps'):
                parts.append(f"{r['reps']}回")
            if r.get('memo'):
                parts.append(f"({r['memo']})")
            lines.append(' / '.join(parts))
        summary = '以下が私のトレーニング記録です。褒めて、アドバイスをください。\n\n' + '\n'.join(lines)
    else:
        summary = 'まだトレーニング記録がありません。これから始める人に向けて励ましとアドバイスをください。'

    # Dify APIにアドバイスを依頼
    payload = {
        'inputs': {},
        'query': summary,
        'response_mode': 'blocking',
        'conversation_id': '',
        'user': request.user.username,
    }

    try:
        resp = requests.post(
            'https://api.dify.ai/v1/chat-messages',
            headers={
                'Authorization': f'Bearer {api_key}',
                'Content-Type': 'application/json',
            },
            json=payload,
            timeout=60,
        )
        resp.raise_for_status()
        data = resp.json()
    except requests.RequestException:
        logger.exception('Dify API call failed in ai_coach_api')
        return JsonResponse({'error': 'AIコーチからの応答に失敗しました。'}, status=502)

    return JsonResponse({'advice': data.get('answer', '')})


@login_required
def chat(request):
    return render(request, 'coach/chat.html')


@login_required
@require_POST
def chat_api(request):
    try:
        body = json.loads(request.body)
    except (json.JSONDecodeError, ValueError):
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    user_message = body.get('message', '').strip()
    if not user_message:
        return JsonResponse({'error': 'Message is required'}, status=400)

    api_key = settings.DIFY_API_KEY
    if not api_key:
        return JsonResponse({'error': 'DIFY_API_KEY is not configured'}, status=500)

    conversation_id = request.session.get('dify_conversation_id', '')

    payload = {
        'inputs': {},
        'query': user_message,
        'response_mode': 'blocking',
        'conversation_id': conversation_id,
        'user': request.user.username,
    }

    try:
        resp = requests.post(
            'https://api.dify.ai/v1/chat-messages',
            headers={
                'Authorization': f'Bearer {api_key}',
                'Content-Type': 'application/json',
            },
            json=payload,
            timeout=60,
        )
        resp.raise_for_status()
        data = resp.json()
    except requests.RequestException:
        logger.exception('Dify API call failed')
        return JsonResponse({'error': 'AIへの問い合わせに失敗しました。'}, status=502)

    # Save conversation_id for follow-up messages
    new_conversation_id = data.get('conversation_id', '')
    if new_conversation_id:
        request.session['dify_conversation_id'] = new_conversation_id

    return JsonResponse({
        'answer': data.get('answer', ''),
        'conversation_id': new_conversation_id,
    })


@login_required
def record(request):
    if request.method == 'POST':
        form = TrainingRecordForm(request.POST)
        if form.is_valid():
            data = {
                'user': request.user.username,
                'date': form.cleaned_data['date'].isoformat(),
                'exercise': form.cleaned_data['exercise'],
                'sets': form.cleaned_data['sets'],
                'weight': str(form.cleaned_data['weight'] or ''),
                'reps': form.cleaned_data.get('reps') or '',
                'memo': form.cleaned_data['memo'],
            }
            gas_url = settings.GAS_POST_URL
            if gas_url:
                try:
                    resp = requests.post(
                        gas_url,
                        json=data,
                        headers={'Content-Type': 'application/json'},
                        timeout=10,
                    )
                    resp.raise_for_status()
                    messages.success(request, '記録を保存しました！')
                except requests.RequestException:
                    logger.exception('GAS POST failed')
                    messages.error(request, '保存に失敗しました。もう一度お試しください。')
            else:
                messages.warning(request, 'GAS URLが設定されていません。.envを確認してください。')
            return redirect('record')
    else:
        form = TrainingRecordForm(initial={'date': date.today()})
    return render(request, 'coach/record.html', {'form': form})


@login_required
def history(request):
    records = []
    gas_url = settings.GAS_GET_URL
    if gas_url:
        try:
            params = {'user': request.user.username}
            resp = requests.get(gas_url, params=params, timeout=10)
            resp.raise_for_status()
            records = resp.json()
        except requests.RequestException:
            logger.exception('GAS GET failed')
            messages.error(request, '記録の取得に失敗しました。')
        except (json.JSONDecodeError, ValueError):
            logger.exception('GAS response parse failed')
            messages.error(request, '記録データの解析に失敗しました。')
    return render(request, 'coach/history.html', {'records': records})

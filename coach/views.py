import json
import logging
from datetime import date

import requests
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from .forms import TrainingRecordForm

logger = logging.getLogger(__name__)


@login_required
def chat(request):
    return render(request, 'coach/chat.html', {
        'dify_chat_url': settings.DIFY_CHAT_URL,
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

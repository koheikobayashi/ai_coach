from django import forms


class TrainingRecordForm(forms.Form):
    date = forms.DateField(
        label='日付',
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-input'}),
    )
    exercise = forms.CharField(
        label='トレーニング種目',
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': '例: ベンチプレス'}),
    )
    sets = forms.IntegerField(
        label='セット数',
        min_value=1,
        widget=forms.NumberInput(attrs={'class': 'form-input', 'placeholder': '例: 3'}),
    )
    weight = forms.DecimalField(
        label='重量 (kg)',
        min_value=0,
        required=False,
        widget=forms.NumberInput(attrs={'class': 'form-input', 'placeholder': '例: 60', 'step': '0.5'}),
    )
    reps = forms.IntegerField(
        label='レップ数',
        min_value=1,
        required=False,
        widget=forms.NumberInput(attrs={'class': 'form-input', 'placeholder': '例: 10'}),
    )
    memo = forms.CharField(
        label='メモ',
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-input', 'rows': 3, 'placeholder': '自由にメモ'}),
    )

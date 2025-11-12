from django import forms


class AccountCreateForm(forms.Form):
    """
    自定义账号注册表单（覆盖 Evennia 默认 min_length=3 的版本）
    """
    username = forms.CharField(
        label="Username",
        min_length=2,  # ✅ 允许2字符
        max_length=30,
        help_text="Username must be at least 2 characters long."
    )
    email = forms.EmailField(
        required=False,
        help_text="Optional email address."
    )
    password = forms.CharField(
        label="Password",
        widget=forms.PasswordInput,
        min_length=2  # ✅ 密码也允许2字符
    )

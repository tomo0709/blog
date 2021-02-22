from django import forms
from django.contrib.auth import get_user_model
from .models import DiscUser, Invitation
import accounts


class DiscUserAdminForm(forms.ModelForm):
    '''管理サイトでグループユーザを編集する時のフォーム
    '''
    class Meta:
        model = DiscUser
        fields = ('discussion', 'user', 'is_owner', 'is_editor')

    def clean_user(self):
        '''ユーザのバリデーション
        
        user を検証しているという事は、追加フォームである
        '''
        # 追加しようとしている user
        user = self.cleaned_data['user']
        
        # disc_id が入力されていなければ、そっちで検証されるのでスルー
        if 'discussion' not in self.cleaned_data:
            return user
        
        # 同じ discussion, user のレコードがあるか検索
        discussion = self.cleaned_data['discussion']
        dupe = DiscUser.objects.filter(discussion=discussion, user=user)
        
        # 追加なので、同じ discussion, user のレコードが見つかったら重複
        if len(dupe) > 0:
            raise forms.ValidationError('{} はすでに {} のユーザです。'
                .format(user, discussion))
        return user


# Discussion 新規作成時の処理をオーバーライドするサンプルコード
#
# from .models import Discussion
#
# class DiscCreateForm(forms.ModelForm):
#     '''Discussion の追加フォームをカスタマイズ
#     '''
#     class Meta:
#         model = Discussion
#         fields = ('name',)
#     
#     def save(self, commit=True):
#         '''保存時の処理をオーバーライド
#         '''
#         # 保存するべきものを取得する
#         m = super().save(commit=False)
#         
#         # 何らかの処理 (本来はデータを加工したりするところ)
#         print('DiscCreateForm.save()', self.user)
#         
#         if commit:
#             m.save()
#         return m
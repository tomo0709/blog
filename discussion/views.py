from datetime import datetime, timedelta, timezone
from django.views.generic import ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.http import Http404
from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.contrib.auth import get_user_model
from .view_func import *
from .models import Discussion, DiscUser, Invitation


class DiscList(LoginRequiredMixin, ListView):
    '''Discussion のリストビュー
    
    ログインユーザのグループのみ表示するため、モデルは DiscUser
    '''
    model = DiscUser
    template_name = 'discussion/discussion_list.html'
    
    def get(self, request, *args, **kwargs):
        '''表示時のリクエストを受けるハンドラ
        '''
        # 座組への招待を表示するため、ビューの属性にする
        now = datetime.now(timezone.utc)
        self.invitations = Invitation.objects.filter(invitee=self.request.user,
            exp_dt__gt=now)
        
        return super().get(request, *args, **kwargs)
    
    def get_queryset(self):
        '''リストに表示するレコードをフィルタする
        '''
        # 自分である DiscUser を取得する
        disc_users = DiscUser.objects.filter(user=self.request.user)
        return disc_users


class DiscCreate(LoginRequiredMixin, CreateView):
    '''Discussion の追加ビュー
    '''
    model = Discussion
    fields = ('name',)
    success_url = reverse_lazy('discussion:disc_list')
    
    def form_valid(self, form):
        '''バリデーションを通った時
        '''
        # 保存したレコードを取得する
        new_disc = form.save(commit=True)
        
        # 自分を owner としてグループユーザに追加する
        disc_user = DiscUser(discussion=new_disc, user=self.request.user,
            is_owner=True)
        disc_user.save()
        
        messages.success(self.request, str(new_disc) + " を作成しました。")
        return super().form_valid(form)
    
    def form_invalid(self, form):
        '''追加に失敗した時
        '''
        messages.warning(self.request, "作成できませんでした。")
        return super().form_invalid(form)


class DiscUpdate(LoginRequiredMixin, UpdateView):
    '''Discussion の更新ビュー
    '''
    model = Discussion
    fields = ('name',)
    success_url = reverse_lazy('discussion:disc_list')
    
    def get(self, request, *args, **kwargs):
        '''表示時のリクエストを受けるハンドラ
        '''
        # 所有権を検査する
        test_owner_permission(self, kwargs['pk'])
        
        return super().get(request, *args, **kwargs)
    
    def post(self, request, *args, **kwargs):
        '''保存時のリクエストを受けるハンドラ
        '''
        # 所有権を検査する
        test_owner_permission(self, kwargs['pk'])
        
        return super().post(request, *args, **kwargs)
    
    def form_valid(self, form):
        '''バリデーションを通った時
        '''
        messages.success(self.request, str(form.instance) + " を更新しました。")
        return super().form_valid(form)

    def form_invalid(self, form):
        '''更新に失敗した時
        '''
        messages.warning(self.request, "更新できませんでした。")
        return super().form_invalid(form)


class DiscDelete(LoginRequiredMixin, DeleteView):
    '''Discussion の削除ビュー
    '''
    model = Discussion
    template_name_suffix = '_delete'
    success_url = reverse_lazy('discussion:disc_list')
    
    def get(self, request, *args, **kwargs):
        '''表示時のリクエストを受けるハンドラ
        '''
        # 所有権を検査する
        test_owner_permission(self, kwargs['pk'])
        
        return super().get(request, *args, **kwargs)
    
    def post(self, request, *args, **kwargs):
        '''保存時のリクエストを受けるハンドラ
        '''
        # 所有権を検査する
        test_owner_permission(self, kwargs['pk'])
        
        return super().post(request, *args, **kwargs)
    
    def delete(self, request, *args, **kwargs):
        '''削除した時のメッセージ
        '''
        result = super().delete(request, *args, **kwargs)
        messages.success(
            self.request, str(self.object) + " を削除しました。")
        return result


class UsrList(LoginRequiredMixin, ListView):
    '''DiscUser のリストビュー
    '''
    model = DiscUser
    
    def get(self, request, *args, **kwargs):
        '''表示時のリクエストを受けるハンドラ
        '''
        # アクセス情報からグループユーザを取得しアクセス権を検査する
        disc_user = accessing_disc_user(self, kwargs['disc_id'])
        if not disc_user:
            raise PermissionDenied
        
        # テンプレートから参照できるよう、ビューの属性にしておく
        self.disc_user = disc_user
        
        # 招待中のユーザを表示するため、ビューの属性にする
        self.invitations = Invitation.objects.filter(discussion=disc_user.discussion)
        
        return super().get(request, *args, **kwargs)
    
    def get_queryset(self):
        '''リストに表示するレコードをフィルタする
        '''
        disc_id=self.kwargs['disc_id']
        disc_users = DiscUser.objects.filter(discussion__pk=disc_id)
        return disc_users
    
    def get_context_data(self, **kwargs):
        '''テンプレートに渡すパラメタを改変する
        '''
        context = super().get_context_data(**kwargs)
        
        # 戻るボタン用の disc_id をセット
        context['disc_id'] = self.kwargs['disc_id']
        
        return context


class UsrUpdate(LoginRequiredMixin, UpdateView):
    '''DiscUser の更新ビュー
    '''
    model = DiscUser
    fields = ('is_editor',)
    
    def get(self, request, *args, **kwargs):
        '''表示時のリクエストを受けるハンドラ
        '''
        # 所有権を検査してアクセス中のグループユーザを取得する
        disc_id = self.get_object().discussion.id
        disc_user = test_owner_permission(self, disc_id)
        
        # テンプレートから参照できるよう、ビューの属性にしておく
        self.disc_user = disc_user
        
        return super().get(request, *args, **kwargs)
    
    def post(self, request, *args, **kwargs):
        '''保存時のリクエストを受けるハンドラ
        '''
        # 所有権を検査してアクセス中のグループユーザを取得する
        disc_id = self.get_object().discussion.id
        disc_user = test_owner_permission(self, disc_id)
        
        return super().post(request, *args, **kwargs)
    
    def get_success_url(self):
        '''更新に成功した時の遷移先を動的に与える
        '''
        disc_id = self.object.discussion.id
        url = reverse_lazy('discussion:usr_list', kwargs={'disc_id': disc_id})
        return url
    
    def form_valid(self, form):
        '''バリデーションを通った時
        '''
        messages.success(self.request, str(form.instance) + " を更新しました。")
        return super().form_valid(form)

    def form_invalid(self, form):
        '''更新に失敗した時
        '''
        messages.warning(self.request, "更新できませんでした。")
        return super().form_invalid(form)


class UsrDelete(LoginRequiredMixin, DeleteView):
    '''DiscUser の削除ビュー
    '''
    model = DiscUser
    template_name_suffix = '_delete'
    
    def get(self, request, *args, **kwargs):
        '''表示時のリクエストを受けるハンドラ
        '''
        # 所有権を検査してアクセス中のグループユーザを取得する
        disc_id = self.get_object().discussion.id
        disc_user = test_owner_permission(self, disc_id)

        # 自分自身を削除することはできない
        if self.get_object() == disc_user:
            raise PermissionDenied
        
        return super().get(request, *args, **kwargs)
    
    def post(self, request, *args, **kwargs):
        '''保存時のリクエストを受けるハンドラ
        '''
        # 所有権を検査してアクセス中のグループユーザを取得する
        disc_id = self.get_object().discussion.id
        disc_user = test_owner_permission(self, disc_id)

        # 自分自身を削除することはできない
        if self.get_object() == disc_user:
            raise PermissionDenied
        
        return super().post(request, *args, **kwargs)
    
    def get_success_url(self):
        '''削除に成功した時の遷移先を動的に与える
        '''
        disc_id = self.object.discussion.id
        url = reverse_lazy('discussion:usr_list', kwargs={'disc_id': disc_id})
        return url
    
    def delete(self, request, *args, **kwargs):
        '''削除した時のメッセージ
        '''
        result = super().delete(request, *args, **kwargs)
        messages.success(
            self.request, str(self.object) + " を削除しました。")
        return result


class InvtCreate(LoginRequiredMixin, CreateView):
    '''Invitation の追加ビュー
    '''
    model = Invitation
    fields = ()
    
    def get(self, request, *args, **kwargs):
        '''表示時のリクエストを受けるハンドラ
        '''
        # 所有権を検査してアクセス中のグループユーザを取得する
        disc_user = test_owner_permission(self)
        
        # discussion を view の属性として持っておく
        # テンプレートで固定要素として表示するため
        self.discussion = disc_user.discussion
        
        return super().get(request, *args, **kwargs)
    
    def post(self, request, *args, **kwargs):
        '''保存時のリクエストを受けるハンドラ
        '''
        # 所有権を検査してアクセス中のグループユーザを取得する
        disc_user = test_owner_permission(self)
        
        # フォームで入力された「招待する人の ID」
        invitee_value = request.POST['invitee_id']
        
        # それに一致するユーザを view の属性として持っておく
        user_model = get_user_model()
        invitees = user_model.objects.filter(username=invitee_value)
        if len(invitees) > 0:
            self.invitee = invitees[0]
        
        # disc_user, discussion を view の属性として持っておく
        # バリデーションと保存時に使うため
        self.disc_user = disc_user
        self.discussion = disc_user.discussion
        
        return super().post(request, *args, **kwargs)
    
    def form_valid(self, form):
        '''バリデーションを通った時
        '''
        # POST ハンドラで招待するユーザを取得できていなかったら、追加失敗
        if not hasattr(self, 'invitee'):
            return self.form_invalid(form)
        
        # グループユーザのユーザ ID リスト
        disc_users = DiscUser.objects.filter(discussion=self.discussion)
        disc_user_user_ids = [disc_user.user.id for disc_user in disc_users]
        
        # 招待中のユーザの ID リスト
        invitations = Invitation.objects.filter(discussion=self.discussion)
        current_invitee_ids = [invt.invitee.id for invt in invitations]
        
        # グループユーザや招待中のユーザを招待することは出来ない。
        if self.invitee.id in disc_user_user_ids\
            or self.invitee.id in current_invitee_ids:
            return self.form_invalid(form)
        
        # 追加しようとするレコードの各フィールドをセット
        instance = form.save(commit=False)
        instance.discussion = self.discussion
        instance.inviter = self.disc_user.user
        instance.invitee = self.invitee
        # 期限は7日
        # デフォルトで UTC で保存されるが念の為 UTC を指定
        instance.exp_dt = datetime.now(timezone.utc) + timedelta(days=7)
        
        messages.success(self.request, str(instance.invitee) + " さんを招待しました。")
        return super().form_valid(form)
    
    def get_success_url(self):
        '''追加に成功した時の遷移先を動的に与える
        '''
        disc_id = self.disc_user.discussion.id
        url = reverse_lazy('discussion:usr_list', kwargs={'disc_id': disc_id})
        return url
    
    def form_invalid(self, form):
        '''追加に失敗した時
        '''
        messages.warning(self.request, "招待できませんでした。")
        return super().form_invalid(form)


class InvtDelete(LoginRequiredMixin, DeleteView):
    '''Invitation の削除ビュー
    '''
    model = Invitation
    template_name_suffix = '_delete'
    
    def get(self, request, *args, **kwargs):
        '''表示時のリクエストを受けるハンドラ
        '''
        # グループの所有者または招待の invitee であることを検査する
        invt = self.get_object()
        disc_id = invt.discussion.id
        disc_user = accessing_disc_user(self, disc_id)
        
        is_owner = disc_user and disc_user.is_owner
        is_invitee = self.request.user == invt.invitee
        
        if not (is_owner or is_invitee):
            raise PermissionDenied
        
        return super().get(request, *args, **kwargs)
    
    def post(self, request, *args, **kwargs):
        '''保存時のリクエストを受けるハンドラ
        '''
        # グループの所有者または招待の invitee であることを検査する
        invt = self.get_object()
        disc_id = invt.discussion.id
        disc_user = accessing_disc_user(self, disc_id)
        
        is_owner = disc_user and disc_user.is_owner
        is_invitee = self.request.user == invt.invitee
        
        if not (is_owner or is_invitee):
            raise PermissionDenied
        
        return super().post(request, *args, **kwargs)
    
    def get_success_url(self):
        '''削除に成功した時の遷移先を動的に与える
        '''
        if self.kwargs['from'] == 'usr_list':
            disc_id = self.object.discussion.id
            url = reverse_lazy('discussion:usr_list', kwargs={'disc_id': disc_id})
        else:
            url = reverse_lazy('discussion:disc_list')
        return url
    
    def delete(self, request, *args, **kwargs):
        '''削除した時のメッセージ
        '''
        result = super().delete(request, *args, **kwargs)
        messages.success(
            self.request, str(self.object) + " を削除しました。")
        return result


class DiscJoin(LoginRequiredMixin, CreateView):
    '''グループに参加するビュー
    '''
    model = DiscUser
    fields = ('discussion', 'user')
    template_name = 'discussion/discussion_join.html'
    success_url = reverse_lazy('discussion:disc_list')
    
    def get(self, request, *args, **kwargs):
        '''表示時のリクエストを受けるハンドラ
        '''
        # 招待されているか検査し、参加できるグループを取得
        self.discussion = self.discussion_to_join()
        
        return super().get(request, *args, **kwargs)
    
    def post(self, request, *args, **kwargs):
        '''保存時のリクエストを受けるハンドラ
        '''
        # 招待されているか検査し、参加できるグループを取得
        self.discussion = self.discussion_to_join()
        
        return super().post(request, *args, **kwargs)
    
    def form_valid(self, form):
        '''バリデーションを通った時
        '''
        # 招待を検査
        invt_id = self.kwargs['invt_id'];
        invts = Invitation.objects.filter(id=invt_id)
        if len(invts) < 1:
            return self.form_invalid(form)
        invt = invts[0]
        
        # 保存するレコードを取得する
        new_disc_user = form.save(commit=False)
        
        # 正しいグループがセットされているか
        if new_disc_user.discussion != invt.discussion:
            return self.form_invalid(form)
        
        # 正しいユーザがセットされているか
        if new_disc_user.user != invt.invitee:
            return self.form_invalid(form)
        
        # 招待を削除
        invt.delete()
        
        messages.success(self.request, str(invt.discussion) + " に参加しました。")
        return super().form_valid(form)
    
    def form_invalid(self, form):
        '''参加に失敗した時
        '''
        messages.warning(self.request, "参加できませんでした。")
        return super().form_invalid(form)
    
    def discussion_to_join(self):
        '''招待されているか検査し、参加できるグループを返す
        '''
        # 招待がなければ 404 エラーを投げる
        invt_id = self.kwargs['invt_id'];
        invts = Invitation.objects.filter(id=invt_id)
        if len(invts) < 1:
            raise Http404
        invt = invts[0]
        
        # 招待が期限切れなら 404 エラーを投げる
        now = datetime.now(timezone.utc)
        if now > invt.exp_dt:
            raise Http404
        
        # アクセス中のユーザが invitee でなければ PermissionDenied
        user = self.request.user
        if user != invt.invitee:
            raise PermissionDenied
        
        return invt.discussion
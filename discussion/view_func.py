from django.core.exceptions import PermissionDenied
from .models import DiscUser


def accessing_disc_user(view, disc_id=None):
    '''アクセス情報から対応する DiscUser を取得する
    
    Parameters
    ----------
    view : View
        アクセス情報の取得元の View
    disc_id : int
        URLconf に disc_id が無い場合に指定する
    '''
    if not disc_id:
        disc_id=view.kwargs['disc_id']
    disc_users = DiscUser.objects.filter(
        discussion__pk=disc_id, user=view.request.user)
    if len(disc_users) < 1:
        return None
    return disc_users[0]


def test_edit_permission(view, disc_id=None):
    '''編集権を検査する
    
    Returns
    -------
    disc_user : DiscUser
        編集権を持っているアクセス中の DiscUser
    '''
    # アクセス情報からグループユーザを取得する
    disc_user = accessing_disc_user(view, disc_id=disc_id)
    if not disc_user:
        raise PermissionDenied
    
    # 所有権または編集権を持っていなければアクセス拒否
    if not (disc_user.is_owner or disc_user.is_editor):
        raise PermissionDenied
    
    return disc_user


def test_owner_permission(view, disc_id=None):
    '''所有権を検査する
    
    Returns
    -------
    disc_user : DiscUser
        所有権を持っているアクセス中の DiscUser
    '''
    # アクセス情報からグループユーザを取得する
    disc_user = accessing_disc_user(view, disc_id=disc_id)
    if not disc_user:
        raise PermissionDenied
    
    # 所有権または編集権を持っていなければアクセス拒否
    if not (disc_user.is_owner):
        raise PermissionDenied
    
    return disc_user
from datetime import datetime, timezone
from django.conf import settings
from django.db import models


class Discussion(models.Model):
    '''グループ
    '''
    name = models.CharField('グループ名', max_length=50)
    
    class Meta:
        verbose_name = verbose_name_plural = 'グループ'
    
    def __str__(self):
        return self.name


class DiscUser(models.Model):
    '''グループごとのユーザと権限
    '''
    discussion = models.ForeignKey(Discussion, verbose_name='グループ',
        on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
        verbose_name='ユーザ', on_delete=models.CASCADE)
    is_owner = models.BooleanField('所有権', default=False)
    is_editor = models.BooleanField('編集権', default=False)
    
    class Meta:
        verbose_name = verbose_name_plural = 'グループユーザ'
    
    def __str__(self):
        first_name = self.user.first_name
        last_name = self.user.last_name
        
        # 姓と名からフルネームを生成
        if (len(first_name) < 1) and (len(last_name) < 1):
            full_name = ''
        elif len(first_name) < 1:
            full_name = last_name
        elif len(last_name) < 1:
            full_name = first_name
        else:
            full_name = f'{last_name}, {first_name}'
        
        # フルネーム (なければユーザ名) を返す
        if len(full_name) > 0:
            return full_name
        else:
            return self.user.username


class Invitation(models.Model):
    '''グループへの招待
    '''
    discussion = models.ForeignKey(Discussion, verbose_name='グループ',
        on_delete=models.CASCADE)
    inviter = models.ForeignKey(settings.AUTH_USER_MODEL,
        verbose_name='招待する人',
        related_name='inviter', on_delete=models.CASCADE)
    invitee = models.ForeignKey(settings.AUTH_USER_MODEL,
        verbose_name='招待される人',
        related_name='invitee', on_delete=models.CASCADE)
    exp_dt = models.DateTimeField(verbose_name='期限')
    
    class Meta:
        verbose_name = verbose_name_plural = 'グループへの招待'
        ordering = ['exp_dt']
    
    def __str__(self):
        return f'{self.invitee} さんへの {self.discussion} への招待'
    
    def expired(self):
        '''この招待が期限切れかどうかを返す
        '''
        now = datetime.now(timezone.utc)
        return now > self.exp_dt
from django.contrib import admin
from .models import Discussion, DiscUser, Invitation
from .forms import DiscUserAdminForm


class DiscUserAdmin(admin.ModelAdmin):
    '''管理サイトでグループユーザを表示する時の設定
    '''
    list_display = ('__str__', 'discussion', 'user', 'is_owner', 'is_editor')
    list_filter = ('discussion',)
    
    # バリデーションのためのカスタムフォーム
    form = DiscUserAdminForm
    
    # fields は Form の Meta でも定義しているが、表示順を維持するため
    fields = ('discussion', 'user', 'is_owner', 'is_editor')

    def add_view(self,request,extra_content=None):
        '''追加フォームでは全 field が変更できる
        '''
        self.readonly_fields = ()
        return super(DiscUserAdmin,self).add_view(request)

    def change_view(self,request,object_id,extra_content=None):
        '''変更フォームではグループとユーザは変更できない
        '''
        self.readonly_fields = ('discussion','user')
        return super(DiscUserAdmin, self).change_view(request, object_id)


admin.site.register(Discussion)
admin.site.register(DiscUser, DiscUserAdmin)
admin.site.register(Invitation)
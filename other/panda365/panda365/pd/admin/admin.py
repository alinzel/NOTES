from pd.admin.base import ModelView


class AdminUserAdmin(ModelView):
    column_list = (
        'id',
        'email',
        'active',
        'confirmed_at',
        'roles',
    )

    def is_visible(self):
        return self.has_roles('dev')


class AdminRoleAdmin(ModelView):
    can_create = True
    can_delete = True
    column_list = (
        'id',
        'name',
        'description',
    )

    def is_visible(self):
        return self.has_roles('dev')

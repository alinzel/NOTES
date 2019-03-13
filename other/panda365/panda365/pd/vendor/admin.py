from pd.admin.base import ModelView
from pd.admin.format import format_imgs


class VendorAdmin(ModelView):
    can_create = True
    form_columns = (
        'name',
        'logo_url',
    )

    def format_logo_url(view, ctx, model, name):
        return format_imgs(model.logo_url)

    column_formatters = dict(
        logo_url=format_logo_url,
    )

from marshmallow import fields
from pd.api.schema import ModelSchema
from .models import Vendor, VendorLink


class VendorSchema(ModelSchema):

    class Meta:
        model = Vendor
        fields = ['name', 'logo_url']


class VendorLinkSchema(ModelSchema):

    class Meta:
        model = VendorLink
        fields = [
            'vendor', 'price', 'currency', 'url'
        ]
    vendor = fields.Nested(VendorSchema)

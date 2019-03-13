from enum import Enum


class Country(Enum):
    ID = 'ID'  # Indonisia
    MY = 'MY'  # Malaysia


Country.ID.admin_label = 'Indonisia'
Country.MY.admin_label = 'Malaysia'

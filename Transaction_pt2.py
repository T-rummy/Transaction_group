import random
from datetime import date

class Transaction:
    _used_ids = set()

    def __init__(self, name, amount, date, category):
        self.transaction_id = self._generate_id()
        self.name = name
        self.amount = float(amount)
        self.date = date
        self.category = category

    def _generate_id(self):
        new_id = random.randint(1000, 9999)
        while new_id in Transaction._used_ids:
            new_id = random.randint(1000, 9999)
        Transaction._used_ids.add(new_id)
        return new_id

    def get_info(self):
        return {
            'Id': self.transaction_id,
            'Name': self.name,
            'Amount': self.amount,
            'Date': self.date,
            'Category': self.category
        }

class FoodTransaction(Transaction):
    def __init__(self, name, amount, date, category, subcategory, location):
        super().__init__(name, amount, date, category)
        self.subcategory = subcategory
        self.location = location

    def get_info(self):
        info = super().get_info()
        info['Subcategory'] = self.subcategory
        info['Location'] = self.location
        return info

class TravelTransaction(Transaction):
    def __init__(self, name, amount, date, category, destination, transport_mode):
        super().__init__(name, amount, date, category)
        self.destination = destination
        self.transport_mode = transport_mode

    def get_info(self):
        info = super().get_info()
        info['Destination'] = self.destination
        info['Transport_Mode'] = self.transport_mode
        return info

class TransportationTransaction(Transaction):
    def __init__(self, name, amount, date, category, transport_type, location):
        super().__init__(name, amount, date, category)
        self.transport_type = transport_type
        self.location = location

    def get_info(self):
        info = super().get_info()
        info['Transport_Type'] = self.transport_type
        info['Location'] = self.location
        return info

class BillsUtilitiesTransaction(Transaction):
    def __init__(self, name, amount, date, category, bill_type, provider):
        super().__init__(name, amount, date, category)
        self.bill_type = bill_type
        self.provider = provider

    def get_info(self):
        info = super().get_info()
        info['Bill_Type'] = self.bill_type
        info['Provider'] = self.provider
        return info

class AcademicTransaction(Transaction):
    def __init__(self, name, amount, date, category, academic_type, institution):
        super().__init__(name, amount, date, category)
        self.academic_type = academic_type
        self.institution = institution

    def get_info(self):
        info = super().get_info()
        info['Academic_Type'] = self.academic_type
        info['Institution'] = self.institution
        return info

class HealthTransaction(Transaction):
    def __init__(self, name, amount, date, category, health_type, provider):
        super().__init__(name, amount, date, category)
        self.health_type = health_type
        self.provider = provider

    def get_info(self):
        info = super().get_info()
        info['Health_Type'] = self.health_type
        info['Provider'] = self.provider
        return info

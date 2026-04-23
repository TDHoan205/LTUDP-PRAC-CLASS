from models.resignation import Resignation

class ResignationService:
    def __init__(self):
        self.resignations = []

    def create_resignation(self, resignation_id, employee, resignation_date, reason, compensation_amount=0):
        resignation = Resignation(resignation_id, employee, resignation_date, reason, compensation_amount)
        self.resignations.append(resignation)
        return resignation

    def get_resignation(self, resignation_id):
        for resignation in self.resignations:
            if resignation.resignation_id == resignation_id:
                return resignation
        return None

    def approve_resignation(self, resignation_id):
        resignation = self.get_resignation(resignation_id)
        if resignation:
            return resignation.approve_resignation()
        return False

    def complete_resignation(self, resignation_id):
        resignation = self.get_resignation(resignation_id)
        if resignation:
            return resignation.complete_resignation()
        return False

    def set_compensation(self, resignation_id, amount):
        resignation = self.get_resignation(resignation_id)
        if resignation:
            return resignation.set_compensation(amount)
        return False

    def get_resignations_by_status(self, status):
        return [r for r in self.resignations if r.status == status]

    def get_employee_resignation_history(self, employee_id):
        return [
            r for r in self.resignations
            if getattr(r.employee, "employee_id", getattr(r.employee, "id", None)) == employee_id
        ]

    def calculate_total_compensation(self):
        return sum(r.compensation_amount for r in self.resignations if r.status == "Completed")

    def get_all_resignations(self):
        return self.resignations

    def get_resignation_statistics(self):
        pending = len(self.get_resignations_by_status("Pending"))
        approved = len(self.get_resignations_by_status("Approved"))
        completed = len(self.get_resignations_by_status("Completed"))

        return {
            'total_resignations': len(self.resignations),
            'pending': pending,
            'approved': approved,
            'completed': completed,
            'total_compensation': self.calculate_total_compensation()
        }
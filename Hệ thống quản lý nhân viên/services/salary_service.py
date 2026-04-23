from datetime import datetime

class SalaryService:
    def __init__(self):
        self.salary_records = []

    def create_salary_reduction(self, employee_id, old_salary, new_salary, reason, effective_date):
        salary_record = {
            'employee_id': employee_id,
            'old_salary': old_salary,
            'new_salary': new_salary,
            'reduction_amount': old_salary - new_salary,
            'reduction_percentage': ((old_salary - new_salary) / old_salary * 100) if old_salary > 0 else 0,
            'reason': reason,
            'effective_date': effective_date,
            'created_date': datetime.now(),
            'status': 'Active'
        }
        self.salary_records.append(salary_record)
        return salary_record

    def get_employee_salary_reduction(self, employee_id):
        return [record for record in self.salary_records if record['employee_id'] == employee_id]

    def get_salary_reduction_by_date(self, effective_date):
        return [record for record in self.salary_records if record['effective_date'] == effective_date]

    def reverse_salary_reduction(self, employee_id, original_salary):
        records = self.get_employee_salary_reduction(employee_id)
        if records:
            latest_record = records[-1]
            if latest_record['status'] == 'Active':
                latest_record['status'] = 'Reversed'
                
                new_record = {
                    'employee_id': employee_id,
                    'old_salary': latest_record['new_salary'],
                    'new_salary': original_salary,
                    'reduction_amount': latest_record['new_salary'] - original_salary,
                    'reduction_percentage': ((latest_record['new_salary'] - original_salary) / latest_record['new_salary'] * 100) if latest_record['new_salary'] > 0 else 0,
                    'reason': 'Reverse salary reduction',
                    'effective_date': datetime.now().strftime('%Y-%m-%d'),
                    'created_date': datetime.now(),
                    'status': 'Reversed'
                }
                self.salary_records.append(new_record)
                return new_record
        return None

    def get_all_salary_reductions(self):
        return self.salary_records

    def get_salary_statistics(self):
        active_reductions = [r for r in self.salary_records if r['status'] == 'Active']

        total_reduction_amount = sum(r['reduction_amount'] for r in active_reductions)
        average_reduction_percentage = (
            sum(r['reduction_percentage'] for r in active_reductions) / len(active_reductions)
            if active_reductions else 0
        )

        return {
            'total_reductions_applied': len(active_reductions),
            'total_reduction_amount': total_reduction_amount,
            'average_reduction_percentage': round(average_reduction_percentage, 2),
            'total_records': len(self.salary_records)
        }

    def get_employees_with_salary_reduction(self):
        employee_ids = set()
        for record in self.salary_records:
            if record['status'] == 'Active':
                reversals = [r for r in self.salary_records 
                            if r['employee_id'] == record['employee_id'] and r['status'] == 'Reversed']
                if not reversals:
                    employee_ids.add(record['employee_id'])
        return list(employee_ids)
from myapp.models import Transaction
items = []
for i in range(50000): 
    items.append(Transaction(sender_id=1, receiver_id=2, amount=1, description=f'txn {i+1}'))
Transaction.objects.bulk_create(items)
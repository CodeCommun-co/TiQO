

def LabelsSerializer(labels):
    dict_by_parents = {label: [] for label in labels if not label.parent}
    for label in labels:
        if label.parent:
            dict_by_parents[label.parent].append(label)

    return dict_by_parents


# Classer les transaction dans un dictionnaire par compte(Iban) et par Side (crédit/débit)
def TransactionsSerializer(transactions):
    dict_by_account = {transaction.iban: {"C":[], "D":[]} for transaction in transactions}
    for transaction in transactions:
        dict_by_account[transaction.iban][transaction.side].append(transaction)

    return dict_by_account
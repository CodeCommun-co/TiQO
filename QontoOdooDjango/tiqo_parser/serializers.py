

def LabelsSerializer(labels):
    dict_by_parents = {label: [] for label in labels if not label.parent}
    for label in labels:
        if label.parent:
            dict_by_parents[label.parent].append(label)

    return dict_by_parents


def LabelsSerializer(labels):
    dict_by_parents = {label: [] for label in labels if not label.parent_id}
    for label in labels:
        if label.parent_id:
            dict_by_parents[label.parent_id].append(label)

    return dict_by_parents
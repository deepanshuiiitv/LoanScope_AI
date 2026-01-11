def clear_sample_documents(folder_path="sample_documents"):
    import os
    for f in os.listdir(folder_path):
        path = os.path.join(folder_path, f)
        if os.path.isfile(path):
            os.remove(path)

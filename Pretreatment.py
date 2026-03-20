import gdown
folder_url = 'https://drive.google.com/drive/folders/15hhq0OywBt77uy9iydunzXsnyWMxZPhe?usp=drive_link'
gdown.download_folder(folder_url, output='ehime_fc_data', quiet=False, use_cookies=False)
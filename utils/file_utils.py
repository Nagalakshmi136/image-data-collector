import os

def create_dir(dir_path: str)-> str:
    """Create directory if it doesn't exist.

    Parameters:
    ----------- 
    dir_path: `str`
        desired directory path.

    Return:
    -------                 
    str         
        path of the directory created.  
    """
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)
    return dir_path
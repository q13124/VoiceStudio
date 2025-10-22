import shutil

def which_path(cmd: str) -> str | None:
    p = shutil.which(cmd)
    return p

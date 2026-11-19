import shutil
from concurrent.futures import ThreadPoolExecutor

_executor = ThreadPoolExecutor(max_workers=2)
def copy_async(source, target):
    return _executor.submit(shutil.copy2, source, target)

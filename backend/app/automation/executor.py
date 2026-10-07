from . import actions

DISPATCH = {
    "open_app": actions.open_app,
    "open_url": actions.open_url,
    "open_folder": actions.open_folder,
    "search_files": actions.search_files,
    "create_folder": actions.create_folder,
    "create_file": actions.create_file,
    "rename_file": actions.rename_file,
    "copy_file": actions.copy_file,
    "move_file": actions.move_file,
    "delete_file": actions.delete_file,
}

def execute(action: str, params: dict):
    fn = DISPATCH.get(action)
    if fn is None:
        raise ValueError(f"Unsupported automation action: {action}")
    return fn(**params)

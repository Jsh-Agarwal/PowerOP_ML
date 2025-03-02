from azureml.core import Workspace

def test_ml_connection():
    try:
        ws = Workspace.from_config('ml_config.json')
        print("ML Workspace Connection Successful!")
        print(f"Workspace name: {ws.name}")
        print(f"Resource group: {ws.resource_group}")
        print(f"Location: {ws.location}")
        return True
    except Exception as e:
        print(f"Error connecting to ML workspace: {str(e)}")
        return False

if __name__ == "__main__":
    test_ml_connection()

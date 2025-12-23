import requests
import time

BASE_URL = "http://127.0.0.1:8013"

# Sequential actions to get box_1 out of ASRS
ACTIONS = [
    "MoveArmToBoxInitialPosition",
    "moveBoxOutOfShelf",
    "moveBoxAndArmToOutput",
    "moveBoxToOutput",
    "MoveBoxOutOfASRS",
]

BOX_ID = "box_1"




def execute_action(box_id: str, action: str) -> dict:
    """Call the execute-action API endpoint"""
    url = f"{BASE_URL}/api/models/execute-action"
    payload = {"boxId": box_id, "action": action}

    response = requests.post(url, json=payload)
    response.raise_for_status()
    return response.json()


def main():
    print(f"Executing get-out sequence for {BOX_ID}")
    print("=" * 50)

    for i, action in enumerate(ACTIONS, 1):
        print(f"\n[{i}/{len(ACTIONS)}] Executing: {action}")

        result = execute_action(BOX_ID, action)
        print(f"  Status: {result['status']}")
        print(f"  Queue Length: {result['queueLength']}")

        # Small delay between actions
        time.sleep(0.5)

    print("\n" + "=" * 50)
    print("All actions queued successfully!")


if __name__ == "__main__":
    main()

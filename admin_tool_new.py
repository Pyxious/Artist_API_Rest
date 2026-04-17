import requests

# URL of your API - Ensure this matches your XAMPP folder
URL = "http://localhost/school-app/api.php"
ADMIN_KEY = "1"
REQUEST_TIMEOUT = 10


def get_headers():
    return {"X-Admin-Token": ADMIN_KEY, "Content-Type": "application/json"}


def parse_response(response):
    try:
        return response.json()
    except ValueError:
        return {"error": "Invalid server response"}


def main():
    logged_in = False

    while True:
        if not logged_in:
            print("\n" + "=" * 45)
            print("       ART MARKETPLACE: PUBLIC PORTAL")
            print("=" * 45)
            print("1. Search/Verify Artist")
            print("2. Submit Registration Request")
            print("3. Switch to Admin Login")
            print("4. Exit")
            choice = input("\nSelect an option: ")

            if choice == "1":
                u = input("Enter username to verify: ")
                res = requests.get(
                    f"{URL}?action=verify&username={u}",
                    timeout=REQUEST_TIMEOUT,
                )
                data = parse_response(res)
                if res.status_code == 200 and "user" in data:
                    print(f"\n[OK] VERIFIED: @{data['user']['username']} is registered.")
                    print(f"Bio: {data['user']['bio']}")
                else:
                    print(
                        f"\n[ERROR] NOT FOUND: "
                        f"{data.get('error', 'Artist is not in our database.')}"
                    )

            elif choice == "2":
                u = input("Desired Username: ")
                b = input("Enter your Bio: ")
                res = requests.post(
                    f"{URL}?action=request",
                    json={"username": u, "bio": b},
                    timeout=REQUEST_TIMEOUT,
                )
                data = parse_response(res)
                if res.status_code == 201:
                    print(f"\n[OK] Success: {data.get('message')}")
                else:
                    print(f"\n[ERROR] Error: {data.get('error')}")

            elif choice == "3":
                key = input("Enter Admin Secret Key: ")
                if key == ADMIN_KEY:
                    logged_in = True
                    print("\nAdmin Access Granted.")
                else:
                    print("\nIncorrect Key. Access Denied.")

            elif choice == "4":
                break

        else:
            print("      OFFICIAL ADMIN DASHBOARD")
            print("1. View All Approved Artists")
            print("2. View All Pending Applications")
            print("3. APPROVE A USER (Numbered List)")
            print("4. EDIT ARTIST BIO (Numbered List)")
            print("5. DELETE AN ARTIST (Numbered List)")
            print("6. Logout to Public Menu")
            choice = input("\nAdmin Choice: ")

            if choice == "1":
                res = requests.get(URL, headers=get_headers(), timeout=REQUEST_TIMEOUT)
                print("\n[OK] APPROVED ARTISTS:", parse_response(res))

            elif choice == "2":
                res = requests.get(
                    f"{URL}?action=pending",
                    headers=get_headers(),
                    timeout=REQUEST_TIMEOUT,
                )
                print("\nPENDING REQUESTS:", parse_response(res))

            elif choice == "3":
                print("\nFetching pending applications...")
                res = requests.get(
                    f"{URL}?action=pending",
                    headers=get_headers(),
                    timeout=REQUEST_TIMEOUT,
                )
                pending = parse_response(res)

                if not isinstance(pending, list) or len(pending) == 0:
                    print("\n--- No users are waiting for approval ---")
                else:
                    print("\n--- SELECT USER TO APPROVE ---")
                    for i, user in enumerate(pending, 1):
                        print(f"[{i}] @{user['username']} | Bio: {user['bio']}")

                    try:
                        idx = int(input("\nEnter NUMBER to approve (0 to cancel): ")) - 1
                        if idx >= 0:
                            target = pending[idx]["username"]
                            res_app = requests.post(
                                f"{URL}?action=approve&username={target}",
                                headers=get_headers(),
                                timeout=REQUEST_TIMEOUT,
                            )
                            print(f"Server: {parse_response(res_app).get('message')}")
                    except (ValueError, IndexError):
                        print("[ERROR] Invalid selection.")

            elif choice == "4":
                print("\nFetching approved artists for editing...")
                res = requests.get(URL, headers=get_headers(), timeout=REQUEST_TIMEOUT)
                approved = parse_response(res)

                if not isinstance(approved, list) or len(approved) == 0:
                    print("\n--- The approved list is empty ---")
                else:
                    print("\n--- SELECT ARTIST TO EDIT ---")
                    for i, user in enumerate(approved, 1):
                        print(f"[{i}] @{user['username']} | Current Bio: {user['bio']}")

                    try:
                        idx = int(input("\nEnter NUMBER to edit (0 to cancel): ")) - 1
                        if idx >= 0:
                            target = approved[idx]["username"]
                            new_bio = input(f"Enter NEW bio for @{target}: ")
                            res_edit = requests.put(
                                URL,
                                headers=get_headers(),
                                json={"username": target, "bio": new_bio},
                                timeout=REQUEST_TIMEOUT,
                            )
                            print(f"Server: {parse_response(res_edit).get('message')}")
                    except (ValueError, IndexError):
                        print("[ERROR] Invalid selection.")

            elif choice == "5":
                print("\nFetching approved artists for deletion...")
                res = requests.get(URL, headers=get_headers(), timeout=REQUEST_TIMEOUT)
                approved = parse_response(res)

                if not isinstance(approved, list) or len(approved) == 0:
                    print("\n--- The approved list is empty ---")
                else:
                    print("\n--- SELECT ARTIST TO DELETE ---")
                    for i, user in enumerate(approved, 1):
                        print(f"[{i}] @{user['username']}")

                    try:
                        idx = int(input("\nEnter NUMBER to delete (0 to cancel): ")) - 1
                        if idx >= 0:
                            target = approved[idx]["username"]
                            confirm = input(f"Are you sure you want to delete @{target}? (y/n): ")
                            if confirm.lower() == "y":
                                res_del = requests.delete(
                                    f"{URL}?username={target}",
                                    headers=get_headers(),
                                    timeout=REQUEST_TIMEOUT,
                                )
                                print(f"Server: {parse_response(res_del).get('message')}")
                    except (ValueError, IndexError):
                        print("[ERROR] Invalid selection.")

            elif choice == "6":
                logged_in = False
                print("[LOCKED] Logged out.")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"[ERROR] Connection Error: {e}")

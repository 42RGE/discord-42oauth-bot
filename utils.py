import requests

def change_user_nickname(token: str, user_id: str, server_id: str, nickname: str, usual_first_name: str) -> bool:
    url = f'https://discordapp.com/api/v8/guilds/{server_id}/members/{user_id}'
    headers = {
        'Authorization': f'Bot {token}'
    }
    data = {
        "nick": f'{nickname} ({usual_first_name})'
    }
    response = requests.patch(url, headers=headers, json=data)
    if response.status_code in [200, 204]:
        return True
    print(f'Error changing nickname for user {user_id} in server with ID {server_id}')
    return False

def add_user_to_server(token: str, user_id: str, server_id: str, access_token: str) -> bool:
    url = f'https://discordapp.com/api/v8/guilds/{server_id}/members/{user_id}'
    headers = {
        'Authorization': f'Bot {token}'
    }
    data = {
        "access_token": access_token
    }
    response = requests.put(url, headers=headers, json=data)
    if response.status_code == 201:
        print(f'User {user_id} added to server with ID {server_id}')
        return True
    else:
        print(f'Error adding user {user_id} to server with ID {server_id}')
        return False

def remove_user_from_server(token: str, user_id: str, server_id: str) -> bool:
    url = f'https://discordapp.com/api/v8/guilds/{server_id}/members/{user_id}'
    headers = {
        'Authorization': f'Bot {token}'
    }
    response = requests.delete(url, headers=headers)
    if response.status_code == 204:
        print(f'User {user_id} removed from server with ID {server_id}')
        return True
    else:
        print(f'Error removing user {user_id} from server with ID {server_id}')
        return False

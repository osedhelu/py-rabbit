from typing import Dict


class UserProvider:
    def __init__(self):
        self._users: Dict[str, Dict] = {
            "123": {"id": "123", "name": "Juan Pérez", "phone": "555-1234"},
            "456": {"id": "456", "name": "María García", "phone": "555-5678"},
        }

    def get_user(self, user_id: str) -> Dict:
        """Obtiene la información de un usuario"""
        return self._users.get(
            user_id, {"id": user_id, "name": "Usuario no encontrado", "phone": "N/A"}
        )

    def add_user(self, user_id: str, user_data: Dict) -> bool:
        """Añade un nuevo usuario"""
        if user_id in self._users:
            return False
        self._users[user_id] = user_data
        return True

    def update_user(self, user_id: str, user_data: Dict) -> bool:
        """Actualiza la información de un usuario"""
        if user_id not in self._users:
            return False
        self._users[user_id].update(user_data)
        return True

    def delete_user(self, user_id: str) -> bool:
        """Elimina un usuario"""
        if user_id not in self._users:
            return False
        del self._users[user_id]
        return True

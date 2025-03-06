import firebase_admin
from firebase_admin import credentials, firestore
from typing import List, Dict, Optional


class FirebaseManager:
    _default_app = None  # Class-level variable to track the default app initialization

    def __init__(self, credential_path: str, collection_name: str = "rus_clients"):
        """
        Initialize Firebase app and Firestore client.
        Avoids multiple initializations by checking if the app already exists.
        """
        if FirebaseManager._default_app is None:
            self.cred = credentials.Certificate(
                {
                    "type": "service_account",
                    "project_id": "refacturador-rus",
                    "private_key_id": "7bd90d84153cf12fa59ce8327a63f3e3a9521805",
                    "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvAIBADANBgkqhkiG9w0BAQEFAASCBKYwggSiAgEAAoIBAQCmh1IdFyFkv/Gv\nB6FcFh24oQzg1whrSwG/aIT7kdo3OjQUTMQtz537ka4GYFhhQhFV9ti/oNdKER9K\nFoaTTPs/uagcdrT0FHsHKZHunT5+3gtg+Q/FWlsiUDhbmNb4uTZvBSVoXw041qDZ\n7C5bqZoPpB560ATfzZzp2wklPrdOfO8x0nSLl0CjnljTMYg8W98/6J8nIi78Hwcg\n1HSz12mpRysJwZTb7q6UYzG38n0kIEyMjgKzHHOe/r1MilTIdzfaeE3bsoKm5sDN\n4UXpvN+9TY+/jRkGQtqOX6WD2PJ7BJZIUKjO+pa3senW04MsHSNnvGGdug9V2QuT\n9lZxbAYVAgMBAAECggEAQGn7gzEdQ6FTVQa4jawoVvBE0PucUBQ1WtqNBdpG9DHZ\nTzjacXXrgBG7pM/Dn+s0VXIkKQuH+yhgWAIakAOo899WfZwVJox9gim8PvYn5F7z\nO9FbHlVzBvTMt/GIxbCus4bkD1kk/iVXFrRawi36X651879fA0q/NV36TaPSt9LP\ngX6OkoOAyPHbMBvXvpXsDooxOVbJYN5vjWKjBwTUKKvhZuHu4zyLVlGBUwfsxT5l\nsqeh4e3SbrAdfbpQLtl7guiYYEzqVXNFqK8rPxtrM4Q7d40a05Tku/cvt/e40SoI\nzttN997joMumxzLwqGM7ckfHBM9Dm6R6v8tpPBXviQKBgQDA7l47dQH9LKCZLfIX\nwcUf8nOYThOT06ahBYGZktVUdG8KhPxWtCanPrf1Fc5V4dTbk7gDOWORDWwPz3nJ\n1GMR6FyPxfx1GwvkloDoapu4P7Fo9DROqPDK/FKI6WWR39VNbDEzDCW6Hroke8aQ\nXVWlvzX10x8Ib24KAk3AWV/KbwKBgQDc925TIcBZ8JehShZW56MZ+8boozYLRsSe\ndXZHG1q3dLUf3VeS+NQZznCbnZWQF02c83M1NF4s8y5BVXrh1Iiz7an1YDSpulUv\nBoLNXcbzRXelK66QeOmtpUegVpf3gtF3/cAKOBaHKpjjezpFw7uD/CZE4rfdSNvD\na1e/Hp7JuwKBgDrjh1fWqzi/+nVHFPIzbxwFQUtn6YnhvKbBq4FY1EznDU3EsdE1\nQ+cgub3RXh3QxMwRFsXFKqMH2cgpqB72+RZqOnaYFCsailLHralDgSyIJHrIr36j\nCnyq7/ZiZ2JTVCRBtfLC7nEVF/Qy47UFCDODXdEfFAXbHVdoxJrFrPt5AoGAGgrf\nadTUgsUkWdINh/iM9IcEDm8N845HphVZ9092BaEvp63CoIPLG6+E/hI4il70usbG\nkUK2xr1yeijE7tDJu8sK+Ox5yHc5iu1NhT7EL+/EBid7z3Mwt1J/epo6FuXIIkg5\n1fp+TTfsBQOE/qvu8cNKD1xZJy9rF0ETemb1d/kCgYBRmY4o1gOBalFswYx5Nz6h\nv3DRnHYjGZ6C4EDqUKt9zCvHQOL5Ag8Bk1gJAx/Fy846R14SuHEVvIXeXFcghZbF\nl3A+rgZqVs4G7IeikDfaA5hrGvYNLZX56SQrhtxnVqEdEBY7JZMHF78+4CxVM4Kf\nyxoGxd8t/uZx3rlAvZEPDQ==\n-----END PRIVATE KEY-----\n",
                    "client_email": "firebase-adminsdk-er1po@refacturador-rus.iam.gserviceaccount.com",
                    "client_id": "110611772453345093141",
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                    "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk-er1po%40refacturador-rus.iam.gserviceaccount.com",
                    "universe_domain": "googleapis.com",
                }
            )
            FirebaseManager._default_app = firebase_admin.initialize_app(self.cred)
        else:
            print("Firebase app is already initialized. Skipping re-initialization.")

        self.db = firestore.client()
        self.collection = self.db.collection(collection_name)

    def _validate_user_data(self, bonificacion: int, intervalo: int) -> None:
        """Validates fields according to business constraints."""
        if not 0 <= bonificacion <= 15:
            raise ValueError("Bonificación debe estar entre 0 y 15")
        if intervalo % 100 != 0:
            raise ValueError("Intervalo debe ser múltiplo de 100")

    def create_user(
        self,
        username: str,
        password: str,
        codigos: List[int],
        bonificacion: int,
        intervalo: int,
        usuario: str,
        genero: str,
    ) -> str:
        """Creates a new user with validations."""
        try:
            self._validate_user_data(bonificacion, intervalo)
            user_data = {
                "username": username,
                "password": password,
                "codigos": codigos,
                "bonificacion": bonificacion,
                "intervalo": intervalo,
                "usuario": usuario,
                "genero": genero,
            }
            doc_ref = self.collection.document()
            doc_ref.set(user_data)
            return doc_ref.id
        except Exception as e:
            raise RuntimeError(f"Error creando usuario: {str(e)}") from e

    def login(self, username: str, password: str) -> Optional[Dict]:
        """Authenticates a user and returns their data."""
        try:
            query = (
                self.collection.where(
                    filter=firestore.FieldFilter("username", "==", username)
                )
                .limit(1)
                .get()
            )
            if not query:
                return None
            user_data = query[0].to_dict()
            if user_data.get("password") == password:
                return {"id": query[0].id, **user_data}
            return None
        except Exception as e:
            raise RuntimeError(f"Error en login: {str(e)}") from e

    def get_all_users(self) -> List[Dict]:
        """Retrieves all registered users."""
        try:
            return [{"id": doc.id, **doc.to_dict()} for doc in self.collection.stream()]
        except Exception as e:
            raise RuntimeError(f"Error obteniendo usuarios: {str(e)}") from e

    def delete_all_users(self) -> None:
        """Deletes all documents in the collection."""
        try:
            for doc in self.collection.stream():
                doc.reference.delete()
        except Exception as e:
            raise RuntimeError(f"Error eliminando usuarios: {str(e)}") from e

    def get_user_by_id(self, user_id: str) -> Optional[Dict]:
        """Retrieves a user by their document ID."""
        try:
            doc = self.collection.document(user_id).get()
            return {"id": doc.id, **doc.to_dict()} if doc.exists else None
        except Exception as e:
            raise RuntimeError(f"Error obteniendo usuario: {str(e)}") from e

    def find_user_by_username(self, username: str) -> Optional[Dict]:
        """Searches for a user by their username."""
        try:
            query = (
                self.collection.where(
                    filter=firestore.FieldFilter("username", "==", username)
                )
                .limit(1)
                .get()
            )
            return {"id": query[0].id, **query[0].to_dict()} if query else None
        except Exception as e:
            raise RuntimeError(f"Error buscando usuario: {str(e)}") from e


# Example usage
if __name__ == "__main__":
    try:
        firebase = FirebaseManager("fbase.json")
        # Clear test data
        firebase.delete_all_users()

        # Create users
        user1_id = firebase.create_user(
            username="14761494",
            password="jde426",
            codigos=[4162],
            bonificacion=15,
            intervalo=300,
            usuario="Blatner Mirta",
            genero="F",
        )
        user2_id = firebase.create_user(
            username="34512119",
            password="Cuervo65",
            codigos=[15968],
            bonificacion=15,
            intervalo=300,
            usuario="Toval Agostina",
            genero="F",
        )
        user3_id = firebase.create_user(
            username="16910346",
            password="ringuito10",
            codigos=[1147, 4726],
            bonificacion=15,
            intervalo=300,
            usuario="Toval Juan Carlos",
            genero="M",
        )

        # Retrieve all users
        print("Usuarios registrados:")
        for user in firebase.get_all_users():
            print(user)

        # Authenticate a user
        logged_user = firebase.login("16910346", "ringuito10")
        if logged_user:
            print(f"\nUsuario autenticado: {logged_user['usuario']}")
    except Exception as e:
        print(f"Error: {str(e)}")

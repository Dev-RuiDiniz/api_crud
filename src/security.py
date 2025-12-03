from datetime import datetime, timedelta
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt

# --- Configurações de Segurança ---
# NOTA: Em produção, estas chaves devem ser lidas de variáveis de ambiente (.env)
SECRET_KEY = "sua_chave_secreta_muito_segura_e_longa"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30 

# Esquema de Autenticação OAuth2 (indica onde buscar o token: Header Authorization)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token") # tokenUrl é um placeholder aqui


# --- Funções JWT ---

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Cria um novo JWT assinado."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    
    # Codifica o payload usando a chave secreta
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token(token: str = Depends(oauth2_scheme)):
    """
    Middleware de dependência que decodifica e valida o JWT.
    
    :param token: O token JWT extraído do header 'Authorization: Bearer <token>'
    :raises HTTPException: 401 Unauthorized se o token for inválido ou expirar
    :returns: O payload (dados) do token se a validação for bem-sucedida.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Credenciais inválidas ou token expirado",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # 1. Decodifica o token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        # 2. Extrai o ID do usuário ou qualquer dado que você está usando como 'subject'
        # Assumimos que o payload contém o 'sub' (subject/user_id)
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
            
        # Retorna o user_id ou payload completo para uso no endpoint
        return user_id 
        
    except JWTError:
        # Captura erros de assinatura, formato inválido ou expiração
        raise credentials_exception
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from jose import JWTError, jwt
from ..database import get_db
from ..models import User
from ..auth import verify_password, get_password_hash, create_access_token, SECRET_KEY, ALGORITHM
from ..schemas import UserCreate, UserResponse, Token, TokenData

router = APIRouter(prefix="/auth", tags=["auth"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

async def get_current_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Não foi possível validar as credenciais",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    
    result = await db.execute(select(User).where(User.username == token_data.username))
    user = result.scalars().first()
    if user is None:
        raise credentials_exception
    return user

@router.post("/register", response_model=UserResponse, status_code=201)
async def register(user: UserCreate, db: AsyncSession = Depends(get_db)):
    # Verificar se o usuário já existe pelo username OU email
    result = await db.execute(
        select(User).where(
            (User.username == user.username) | (User.email == user.email)
        )
    )
    if result.scalars().first():
        raise HTTPException(status_code=400, detail="Usuário ou email já cadastrado")

    # Mapeamento simples para garantir que o cargo seja aceito pelo banco
    role_map = {
        "Médico": "doctor",
        "Paciente": "patient",
        "Administrador": "admin"
    }
    final_role = role_map.get(user.role, user.role.lower())
    
    hashed_password = get_password_hash(user.password)
    db_user = User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password,
        role=final_role
    )
    db.add(db_user)
    await db.flush()  # Usa flush para obter o ID do banco antes do commit final
    await db.refresh(db_user)
    return db_user

@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.username == form_data.username))
    user = result.scalars().first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Usuário ou senha incorretos")
    
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=UserResponse)
async def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user
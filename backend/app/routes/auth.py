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
    try:
        print(f"DEBUG: Iniciando registro para usuário: {user.username} com cargo: {user.role}")
        
        # Verificar se o usuário já existe pelo username OU email
        result = await db.execute(
            select(User).where(
                (User.username == user.username) | (User.email == user.email)
            )
        )
        if result.scalars().first():
            print(f"!!! ERRO NO REGISTRO !!!: Usuário ou email já cadastrado")
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
        await db.commit()
        await db.refresh(db_user)
        print(f"DEBUG: Usuário {db_user.username} registrado com sucesso (ID: {db_user.id})")
        return db_user
    except HTTPException as he:
        # Re-levanta exceções que já são HTTP (como o 400 acima)
        raise he
    except Exception as e:
        print(f"!!! ERRO CRÍTICO NO REGISTRO !!!: {str(e)}")
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Erro interno no servidor: {str(e)}")

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

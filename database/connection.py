from sqlmodel import create_engine, SQLModel, Session

engine = create_engine("sqlite:///database.db", echo=True)

def conn():
    from models.models import Post, Comment  # 모델 임포트
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session

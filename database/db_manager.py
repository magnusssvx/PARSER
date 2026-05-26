"""
Менеджер базы данных для судебных решений.
Поддерживает PostgreSQL и ClickHouse через SQLAlchemy.
"""

import os
from typing import List, Optional
from datetime import datetime
from sqlalchemy import create_engine, Column, String, DateTime, Text, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

from models.document import CourtDecision

Base = declarative_base()


class CourtDecisionDB(Base):
    """Модель таблицы для хранения судебных решений."""
    
    __tablename__ = 'court_decisions'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    decision_number = Column(String(100), nullable=False, index=True)
    decision_date = Column(DateTime, nullable=False, index=True)
    case_number = Column(String(100), nullable=False)
    court_location = Column(String(200), nullable=False)
    judge = Column(String(200), nullable=False)
    full_text = Column(Text, nullable=False)
    source_file = Column(String(500), nullable=True)
    url = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=datetime.now)
    
    def to_court_decision(self) -> CourtDecision:
        """Преобразует запись БД в объект CourtDecision."""
        return CourtDecision(
            decision_number=self.decision_number,
            decision_date=self.decision_date,
            case_number=self.case_number,
            court_location=self.court_location,
            judge=self.judge,
            full_text=self.full_text,
            source_file=self.source_file,
            url=self.url
        )


class DatabaseManager:
    """Менеджер для работы с базой данных."""
    
    def __init__(self, db_type: str = 'sqlite', **kwargs):
        """
        Инициализирует подключение к БД.
        
        Args:
            db_type: Тип БД ('sqlite', 'postgresql' или 'clickhouse')
            **kwargs: Параметры подключения
        """
        self.db_type = db_type
        self.engine = None
        self.SessionLocal = None
        
        if db_type == 'sqlite':
            self._init_sqlite(**kwargs)
        elif db_type == 'postgresql':
            self._init_postgresql(**kwargs)
        elif db_type == 'clickhouse':
            self._init_clickhouse(**kwargs)
        else:
            raise ValueError(f"Неподдерживаемый тип БД: {db_type}")
    
    def _init_sqlite(self, database: str = 'court_decisions.db'):
        """Инициализирует подключение к SQLite (для тестирования)."""
        import os
        
        # Создаем путь к файлу БД
        db_path = os.path.join(os.path.dirname(__file__), '..', database)
        connection_string = f"sqlite:///{db_path}"
        
        self.engine = create_engine(connection_string, echo=False)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        
        # Создаем таблицы
        Base.metadata.create_all(bind=self.engine)
        print(f"Подключено к SQLite: {db_path}")
    
    def _init_postgresql(self, 
                         host: str = 'localhost',
                         port: int = 5432,
                         database: str = 'court_decisions',
                         username: str = 'postgres',
                         password: str = 'postgres'):
        """Инициализирует подключение к PostgreSQL."""
        connection_string = f"postgresql+psycopg2://{username}:{password}@{host}:{port}/{database}"
        self.engine = create_engine(connection_string, echo=False)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        
        # Создаем таблицы
        Base.metadata.create_all(bind=self.engine)
        print(f"Подключено к PostgreSQL: {host}:{port}/{database}")
    
    def _init_clickhouse(self,
                         host: str = 'localhost',
                         port: int = 9000,
                         database: str = 'court_decisions',
                         username: str = 'default',
                         password: str = ''):
        """Инициализирует подключение к ClickHouse."""
        try:
            from clickhouse_sqlalchemy import make_session, get_declarative_base
            from clickhouse_sqlalchemy.drivers.http import connector
            
            connection_string = f'clickhouse+http://{username}:{password}@{host}:{port}/{database}'
            self.engine = create_engine(connection_string)
            self.SessionLocal = sessionmaker(bind=self.engine)
            
            # Для ClickHouse нужно использовать специальную базу
            clickhouse_base = get_declarative_base()
            
            # Переопределяем модель для ClickHouse
            class CourtDecisionCH(clickhouse_base):
                __tablename__ = 'court_decisions'
                
                id = Column(Integer, primary_key=True)
                decision_number = Column(String(100))
                decision_date = Column(DateTime)
                case_number = Column(String(100))
                court_location = Column(String(200))
                judge = Column(String(200))
                full_text = Column(Text)
                source_file = Column(String(500))
                url = Column(String(500))
                created_at = Column(DateTime, default=datetime.now)
            
            # Создаем таблицу
            clickhouse_base.metadata.create_all(bind=self.engine)
            print(f"Подключено к ClickHouse: {host}:{port}/{database}")
            
        except ImportError:
            print("Для работы с ClickHouse установите clickhouse-sqlalchemy")
            raise
    
    def save_decision(self, decision: CourtDecision) -> bool:
        """Сохраняет одно решение в БД."""
        try:
            session = self.SessionLocal()
            
            # Проверяем, существует ли уже такое решение
            existing = session.query(CourtDecisionDB).filter_by(
                decision_number=decision.decision_number,
                case_number=decision.case_number
            ).first()
            
            if existing:
                print(f"Решение {decision.decision_number} уже существует в БД")
                session.close()
                return False
            
            # Создаем новую запись
            db_decision = CourtDecisionDB(
                decision_number=decision.decision_number,
                decision_date=decision.decision_date,
                case_number=decision.case_number,
                court_location=decision.court_location,
                judge=decision.judge,
                full_text=decision.full_text,
                source_file=decision.source_file,
                url=decision.url
            )
            
            session.add(db_decision)
            session.commit()
            session.close()
            
            print(f"Решение {decision.decision_number} сохранено в БД")
            return True
            
        except Exception as e:
            print(f"Ошибка при сохранении решения в БД: {e}")
            return False
    
    def save_decisions(self, decisions: List[CourtDecision]) -> int:
        """Сохраняет список решений в БД."""
        saved_count = 0
        
        for decision in decisions:
            if self.save_decision(decision):
                saved_count += 1
        
        print(f"Сохранено {saved_count} из {len(decisions)} решений")
        return saved_count
    
    def get_all_decisions(self) -> List[CourtDecision]:
        """Получает все решения из БД."""
        try:
            session = self.SessionLocal()
            db_decisions = session.query(CourtDecisionDB).all()
            decisions = [d.to_court_decision() for d in db_decisions]
            session.close()
            return decisions
        except Exception as e:
            print(f"Ошибка при получении решений из БД: {e}")
            return []
    
    def get_decision_by_number(self, decision_number: str) -> Optional[CourtDecision]:
        """Находит решение по номеру."""
        try:
            session = self.SessionLocal()
            db_decision = session.query(CourtDecisionDB).filter_by(
                decision_number=decision_number
            ).first()
            
            if db_decision:
                decision = db_decision.to_court_decision()
            else:
                decision = None
            
            session.close()
            return decision
        except Exception as e:
            print(f"Ошибка при поиске решения: {e}")
            return None
    
    def search_decisions(self, 
                        court_location: Optional[str] = None,
                        judge: Optional[str] = None,
                        start_date: Optional[datetime] = None,
                        end_date: Optional[datetime] = None) -> List[CourtDecision]:
        """Ищет решения по критериям."""
        try:
            session = self.SessionLocal()
            query = session.query(CourtDecisionDB)
            
            if court_location:
                query = query.filter(CourtDecisionDB.court_location.ilike(f"%{court_location}%"))
            
            if judge:
                query = query.filter(CourtDecisionDB.judge.ilike(f"%{judge}%"))
            
            if start_date:
                query = query.filter(CourtDecisionDB.decision_date >= start_date)
            
            if end_date:
                query = query.filter(CourtDecisionDB.decision_date <= end_date)
            
            db_decisions = query.all()
            decisions = [d.to_court_decision() for d in db_decisions]
            session.close()
            return decisions
        except Exception as e:
            print(f"Ошибка при поиске решений: {e}")
            return []
    
    def get_statistics(self) -> dict:
        """Возвращает статистику по базе данных."""
        try:
            session = self.SessionLocal()
            
            total = session.query(CourtDecisionDB).count()
            unique_courts = session.query(CourtDecisionDB.court_location).distinct().count()
            unique_judges = session.query(CourtDecisionDB.judge).distinct().count()
            
            # Самые активные суды
            from sqlalchemy import func
            court_stats = session.query(
                CourtDecisionDB.court_location,
                func.count(CourtDecisionDB.id).label('count')
            ).group_by(CourtDecisionDB.court_location).order_by(func.count(CourtDecisionDB.id).desc()).limit(5).all()
            
            session.close()
            
            return {
                'total_decisions': total,
                'unique_courts': unique_courts,
                'unique_judges': unique_judges,
                'top_courts': [{'court': court, 'count': count} for court, count in court_stats]
            }
        except Exception as e:
            print(f"Ошибка при получении статистики: {e}")
            return {}
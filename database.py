"""
Database Module - Persistence SQLite
=====================================
Stockage des paires coïntégrées, positions et historique des signaux.
"""

from datetime import datetime
from typing import Optional, List, Dict
from pathlib import Path
import json

from sqlalchemy import create_engine, Column, Integer, Float, String, DateTime, Boolean, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from loguru import logger

from config import config

Base = declarative_base()


class CointegrationPair(Base):
    """Table des paires coïntégrées."""
    __tablename__ = "cointegrated_pairs"
    
    id = Column(Integer, primary_key=True)
    pair_id = Column(String(100), unique=True, index=True)
    symbol1 = Column(String(50), nullable=False)
    symbol2 = Column(String(50), nullable=False)
    hedge_ratio = Column(Float, nullable=False)
    half_life = Column(Float, nullable=False)
    pvalue = Column(Float, nullable=False)
    spread_mean = Column(Float, nullable=False)
    spread_std = Column(Float, nullable=False)
    test_method = Column(String(50), default="engle_granger")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_validation = Column(DateTime)
    breakdown_count = Column(Integer, default=0)
    notes = Column(Text)


class Position(Base):
    """Table des positions ouvertes."""
    __tablename__ = "positions"
    
    id = Column(Integer, primary_key=True)
    pair_id = Column(String(100), index=True)
    symbol1 = Column(String(50))
    symbol2 = Column(String(50))
    state = Column(String(20))  # flat, long_spread, short_spread
    entry_zscore = Column(Float)
    entry_hedge_ratio = Column(Float)
    entry_price1 = Column(Float)
    entry_price2 = Column(Float)
    entry_time = Column(DateTime)
    scale_level = Column(Integer, default=0)
    half_life = Column(Float)
    breakdown_count = Column(Integer, default=0)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class SignalHistory(Base):
    """Historique des signaux."""
    __tablename__ = "signal_history"
    
    id = Column(Integer, primary_key=True)
    pair_id = Column(String(100), index=True)
    signal_type = Column(String(50))
    symbol1 = Column(String(50))
    symbol2 = Column(String(50))
    zscore = Column(Float)
    hedge_ratio = Column(Float)
    price1 = Column(Float)
    price2 = Column(Float)
    reason = Column(Text)
    timestamp = Column(DateTime, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class Database:
    """Interface avec la base de données SQLite."""
    
    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = db_path or config.database.db_path
        self.engine = create_engine(f"sqlite:///{self.db_path}")
        Base.metadata.create_all(self.engine)
        self.SessionLocal = sessionmaker(bind=self.engine)
        logger.info(f"Database initialized: {self.db_path}")
    
    def get_session(self) -> Session:
        return self.SessionLocal()
    
    # ==========================================================================
    # COINTEGRATED PAIRS
    # ==========================================================================
    
    def save_pair(
        self,
        pair_id: str,
        symbol1: str,
        symbol2: str,
        hedge_ratio: float,
        half_life: float,
        pvalue: float,
        spread_mean: float,
        spread_std: float,
        test_method: str = "engle_granger"
    ) -> CointegrationPair:
        """Sauvegarde ou met à jour une paire coïntégrée."""
        session = self.get_session()
        try:
            pair = session.query(CointegrationPair).filter_by(pair_id=pair_id).first()
            
            if pair:
                pair.hedge_ratio = hedge_ratio
                pair.half_life = half_life
                pair.pvalue = pvalue
                pair.spread_mean = spread_mean
                pair.spread_std = spread_std
                pair.test_method = test_method
                pair.last_validation = datetime.utcnow()
                pair.is_active = True
            else:
                pair = CointegrationPair(
                    pair_id=pair_id,
                    symbol1=symbol1,
                    symbol2=symbol2,
                    hedge_ratio=hedge_ratio,
                    half_life=half_life,
                    pvalue=pvalue,
                    spread_mean=spread_mean,
                    spread_std=spread_std,
                    test_method=test_method,
                    last_validation=datetime.utcnow()
                )
                session.add(pair)
            
            session.commit()
            session.refresh(pair)
            logger.debug(f"Saved pair: {pair_id}")
            return pair
        finally:
            session.close()
    
    def get_pair(self, pair_id: str) -> Optional[CointegrationPair]:
        """Récupère une paire par ID."""
        session = self.get_session()
        try:
            return session.query(CointegrationPair).filter_by(pair_id=pair_id).first()
        finally:
            session.close()
    
    def get_active_pairs(self) -> List[CointegrationPair]:
        """Récupère toutes les paires actives."""
        session = self.get_session()
        try:
            return session.query(CointegrationPair).filter_by(is_active=True).all()
        finally:
            session.close()
    
    def deactivate_pair(self, pair_id: str, reason: str = ""):
        """Désactive une paire (breakdown)."""
        session = self.get_session()
        try:
            pair = session.query(CointegrationPair).filter_by(pair_id=pair_id).first()
            if pair:
                pair.is_active = False
                pair.notes = reason
                session.commit()
                logger.info(f"Deactivated pair: {pair_id} - {reason}")
        finally:
            session.close()
    
    def increment_breakdown_count(self, pair_id: str):
        """Incrémente le compteur de breakdown."""
        session = self.get_session()
        try:
            pair = session.query(CointegrationPair).filter_by(pair_id=pair_id).first()
            if pair:
                pair.breakdown_count += 1
                session.commit()
        finally:
            session.close()
    
    def reset_breakdown_count(self, pair_id: str):
        """Reset le compteur de breakdown."""
        session = self.get_session()
        try:
            pair = session.query(CointegrationPair).filter_by(pair_id=pair_id).first()
            if pair:
                pair.breakdown_count = 0
                session.commit()
        finally:
            session.close()
    
    # ==========================================================================
    # POSITIONS
    # ==========================================================================
    
    def save_position(
        self,
        pair_id: str,
        symbol1: str,
        symbol2: str,
        state: str,
        entry_zscore: float = 0,
        entry_hedge_ratio: float = 0,
        entry_price1: float = None,
        entry_price2: float = None,
        entry_time: datetime = None,
        scale_level: int = 0,
        half_life: float = 20
    ) -> Position:
        """Sauvegarde ou met à jour une position."""
        session = self.get_session()
        try:
            position = session.query(Position).filter_by(pair_id=pair_id).first()
            
            if position:
                position.state = state
                position.entry_zscore = entry_zscore
                position.entry_hedge_ratio = entry_hedge_ratio
                position.entry_price1 = entry_price1
                position.entry_price2 = entry_price2
                position.entry_time = entry_time
                position.scale_level = scale_level
                position.half_life = half_life
            else:
                position = Position(
                    pair_id=pair_id,
                    symbol1=symbol1,
                    symbol2=symbol2,
                    state=state,
                    entry_zscore=entry_zscore,
                    entry_hedge_ratio=entry_hedge_ratio,
                    entry_price1=entry_price1,
                    entry_price2=entry_price2,
                    entry_time=entry_time,
                    scale_level=scale_level,
                    half_life=half_life
                )
                session.add(position)
            
            session.commit()
            session.refresh(position)
            return position
        finally:
            session.close()
    
    def get_position(self, pair_id: str) -> Optional[Position]:
        """Récupère une position."""
        session = self.get_session()
        try:
            return session.query(Position).filter_by(pair_id=pair_id).first()
        finally:
            session.close()
    
    def get_open_positions(self) -> List[Position]:
        """Récupère les positions ouvertes."""
        session = self.get_session()
        try:
            return session.query(Position).filter(Position.state != "flat").all()
        finally:
            session.close()
    
    def close_position(self, pair_id: str):
        """Ferme une position (met l'état à flat)."""
        session = self.get_session()
        try:
            position = session.query(Position).filter_by(pair_id=pair_id).first()
            if position:
                position.state = "flat"
                position.scale_level = 0
                position.breakdown_count = 0
                session.commit()
        finally:
            session.close()
    
    # ==========================================================================
    # SIGNAL HISTORY
    # ==========================================================================
    
    def save_signal(
        self,
        pair_id: str,
        signal_type: str,
        symbol1: str,
        symbol2: str,
        zscore: float,
        hedge_ratio: float,
        timestamp: datetime,
        price1: float = None,
        price2: float = None,
        reason: str = ""
    ) -> SignalHistory:
        """Enregistre un signal dans l'historique."""
        session = self.get_session()
        try:
            signal = SignalHistory(
                pair_id=pair_id,
                signal_type=signal_type,
                symbol1=symbol1,
                symbol2=symbol2,
                zscore=zscore,
                hedge_ratio=hedge_ratio,
                price1=price1,
                price2=price2,
                reason=reason,
                timestamp=timestamp
            )
            session.add(signal)
            session.commit()
            session.refresh(signal)
            logger.debug(f"Saved signal: {signal_type} for {pair_id}")
            return signal
        finally:
            session.close()
    
    def get_signal_history(
        self,
        pair_id: Optional[str] = None,
        limit: int = 100
    ) -> List[SignalHistory]:
        """Récupère l'historique des signaux."""
        session = self.get_session()
        try:
            query = session.query(SignalHistory)
            if pair_id:
                query = query.filter_by(pair_id=pair_id)
            return query.order_by(SignalHistory.timestamp.desc()).limit(limit).all()
        finally:
            session.close()
    
    def get_recent_signals(self, hours: int = 24) -> List[SignalHistory]:
        """Récupère les signaux des dernières heures."""
        from datetime import timedelta
        session = self.get_session()
        try:
            cutoff = datetime.utcnow() - timedelta(hours=hours)
            return session.query(SignalHistory).filter(
                SignalHistory.timestamp >= cutoff
            ).order_by(SignalHistory.timestamp.desc()).all()
        finally:
            session.close()
    
    # ==========================================================================
    # EXPORT / IMPORT
    # ==========================================================================
    
    def export_pairs_to_csv(self, filepath: str):
        """Exporte les paires vers un fichier CSV."""
        import pandas as pd
        
        session = self.get_session()
        try:
            pairs = session.query(CointegrationPair).all()
            data = [{
                "pair_id": p.pair_id,
                "symbol1": p.symbol1,
                "symbol2": p.symbol2,
                "hedge_ratio": p.hedge_ratio,
                "half_life": p.half_life,
                "pvalue": p.pvalue,
                "is_active": p.is_active,
                "last_validation": p.last_validation
            } for p in pairs]
            
            df = pd.DataFrame(data)
            df.to_csv(filepath, index=False)
            logger.info(f"Exported {len(pairs)} pairs to {filepath}")
        finally:
            session.close()
    
    def get_statistics(self) -> Dict:
        """Retourne des statistiques sur la base de données."""
        session = self.get_session()
        try:
            return {
                "total_pairs": session.query(CointegrationPair).count(),
                "active_pairs": session.query(CointegrationPair).filter_by(is_active=True).count(),
                "open_positions": session.query(Position).filter(Position.state != "flat").count(),
                "total_signals": session.query(SignalHistory).count(),
            }
        finally:
            session.close()


# Instance globale
db = Database()


if __name__ == "__main__":
    import sys
    logger.remove()
    logger.add(sys.stdout, level="INFO")
    
    # Test
    db = Database(Path("./test_pairs.db"))
    
    # Save a pair
    pair = db.save_pair(
        pair_id="SPY_QQQ",
        symbol1="SPY",
        symbol2="QQQ",
        hedge_ratio=0.85,
        half_life=15.5,
        pvalue=0.02,
        spread_mean=5.2,
        spread_std=2.1
    )
    print(f"Saved pair: {pair.pair_id}")
    
    # Save a signal
    signal = db.save_signal(
        pair_id="SPY_QQQ",
        signal_type="open_long_spread",
        symbol1="SPY",
        symbol2="QQQ",
        zscore=-2.1,
        hedge_ratio=0.85,
        timestamp=datetime.utcnow(),
        reason="Test signal"
    )
    print(f"Saved signal: {signal.signal_type}")
    
    # Stats
    print("\n=== Statistics ===")
    print(db.get_statistics())
    
    # Cleanup
    Path("./test_pairs.db").unlink(missing_ok=True)

from sqlalchemy import Column, Integer, String, DateTime
from base import Base
import datetime
import uuid

class BulletEfficiency(Base):
    """Bullet Efficiency"""

    __tablename__ = "bullet_efficiency"

    id = Column(Integer, primary_key=True)
    player_id = Column(String(250), nullable=False)
    gun_id = Column(String(50), nullable=False)
    round_start_magazine_count = Column(Integer, nullable = False)
    round_end_magazine_count = Column(Integer, nullable = False)
    gun_cost = Column(Integer, nullable=False)
    trace_id = Column(String(100), nullable=False)
    date_created = Column(DateTime, nullable=False)

    def __init__(self, player_id, gun_id, round_start_magazine_count, round_end_magazine_count, gun_cost, trace_id):
        """ Initializes a bullet efficiency reading """
        self.player_id = player_id
        self.gun_id = gun_id
        self.round_start_magazine_count = round_start_magazine_count
        self.round_end_magazine_count = round_end_magazine_count
        self.gun_cost = gun_cost
        self.trace_id = trace_id
        self.date_created = datetime.datetime.now()

    def to_dict(self):  
        """ Dictionary representation of a bullet efficiency reading """

        dict = {}
        dict['id'] = self.id
        dict['player_id'] = self.player_id
        dict['gun_id'] = self.gun_id
        dict['round_start_magazine_count'] = self.round_start_magazine_count
        dict['round_end_magazine_count'] = self.round_end_magazine_count
        dict['gun_cost'] = self.gun_cost
        dict['trace_id'] = self.trace_id
        dict['date_created'] = self.date_created

        return dict
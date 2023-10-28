from sqlalchemy import Column, Integer, String, DateTime
from base import Base
import datetime
import uuid
class AbilityEfficiency(Base):
    """Ability Efficiency"""

    __tablename__ = "ability_efficiency"

    id = Column(Integer, primary_key=True)
    player_id = Column(String(250), nullable=False)
    agent_id = Column(String(50), nullable=False)
    round_start_ability_count = Column(Integer, nullable = False)
    round_end_ability_count = Column(Integer, nullable = False)
    ability_cost = Column(Integer, nullable=False)
    trace_id = Column(String(100), nullable=False)
    date_created = Column(DateTime, nullable=False)

    def __init__(self, player_id, agent_id, round_start_ability_count, round_end_ability_count, ability_cost, trace_id):
        """ Initializes a ability efficiency reading """
        self.player_id = player_id
        self.agent_id = agent_id
        self.round_start_ability_count = round_start_ability_count
        self.round_end_ability_count = round_end_ability_count
        self.ability_cost = ability_cost

        self.trace_id = trace_id
        self.date_created = datetime.datetime.now()

    def to_dict(self):
        """ Dictionary representation of a ability efficiency reading """

        dict = {}
        dict['id'] = self.id
        dict['player_id'] = self.player_id
        dict['agent_id'] = self.agent_id
        dict['round_start_ability_count'] = self.round_start_ability_count
        dict['round_end_ability_count'] = self.round_end_ability_count
        dict['ability_cost'] = self.ability_cost
        dict['trace_id'] = self.trace_id
        dict['date_created'] = self.date_created

        return dict
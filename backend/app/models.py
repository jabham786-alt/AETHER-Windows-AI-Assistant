from datetime import datetime,timezone
from sqlalchemy import String,Text,DateTime,ForeignKey
from sqlalchemy.orm import Mapped,mapped_column
from backend.app.database import Base

class Conversation(Base):
 __tablename__="conversations";id:Mapped[str]=mapped_column(String(36),primary_key=True);title:Mapped[str]=mapped_column(String(200),default="New conversation");created_at:Mapped[datetime]=mapped_column(DateTime,default=lambda:datetime.now(timezone.utc))

class Message(Base):
 __tablename__="messages";id:Mapped[str]=mapped_column(String(36),primary_key=True);conversation_id:Mapped[str]=mapped_column(ForeignKey("conversations.id"));role:Mapped[str]=mapped_column(String(20));content:Mapped[str]=mapped_column(Text);created_at:Mapped[datetime]=mapped_column(DateTime,default=lambda:datetime.now(timezone.utc))

class AutomationAction(Base):
 __tablename__="automation_actions"
 id:Mapped[str]=mapped_column(String(36),primary_key=True)
 action:Mapped[str]=mapped_column(String(50))
 risk:Mapped[str]=mapped_column(String(10))
 status:Mapped[str]=mapped_column(String(20))
 details:Mapped[str]=mapped_column(Text)
 created_at:Mapped[datetime]=mapped_column(DateTime,default=lambda:datetime.now(timezone.utc))

class Memory(Base):
 __tablename__="memories"
 id:Mapped[str]=mapped_column(String(36),primary_key=True)
 category:Mapped[str]=mapped_column(String(40),default="general")
 content:Mapped[str]=mapped_column(Text)
 source:Mapped[str]=mapped_column(String(40),default="user")
 created_at:Mapped[datetime]=mapped_column(DateTime,default=lambda:datetime.now(timezone.utc))
 updated_at:Mapped[datetime]=mapped_column(DateTime,default=lambda:datetime.now(timezone.utc),onupdate=lambda:datetime.now(timezone.utc))

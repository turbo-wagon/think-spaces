from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import Agent, Space
from ..schemas import AgentCreate, AgentRead, AgentUpdate

router = APIRouter(prefix="/agents", tags=["agents"])


@router.get("/", response_model=List[AgentRead])
def list_agents(
    space_id: Optional[int] = Query(default=None),
    db: Session = Depends(get_db),
) -> List[Agent]:
    query = db.query(Agent)
    if space_id is not None:
        query = query.filter(Agent.space_id == space_id)
    return query.order_by(Agent.created_at.desc()).all()


@router.post("/", response_model=AgentRead, status_code=status.HTTP_201_CREATED)
def create_agent(agent_in: AgentCreate, db: Session = Depends(get_db)) -> Agent:
    space_exists = db.query(Space.id).filter(Space.id == agent_in.space_id).first()
    if space_exists is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Space not found")

    agent = Agent(**agent_in.model_dump())
    db.add(agent)
    db.commit()
    db.refresh(agent)
    return agent


@router.get("/{agent_id}", response_model=AgentRead)
def get_agent(agent_id: int, db: Session = Depends(get_db)) -> Agent:
    agent = db.query(Agent).filter(Agent.id == agent_id).first()
    if agent is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Agent not found")
    return agent


@router.put("/{agent_id}", response_model=AgentRead)
def update_agent(
    agent_id: int, agent_in: AgentUpdate, db: Session = Depends(get_db)
) -> Agent:
    agent = db.query(Agent).filter(Agent.id == agent_id).first()
    if agent is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Agent not found")

    for field, value in agent_in.model_dump(exclude_unset=True).items():
        setattr(agent, field, value)

    db.commit()
    db.refresh(agent)
    return agent


@router.delete("/{agent_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_agent(agent_id: int, db: Session = Depends(get_db)) -> None:
    agent = db.query(Agent).filter(Agent.id == agent_id).first()
    if agent is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Agent not found")

    db.delete(agent)
    db.commit()

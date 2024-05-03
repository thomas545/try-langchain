from uuid import uuid4
from typing import Annotated
from fastapi import APIRouter, Header, UploadFile, File, Response
from brain.rags import run_graph_workflow
from schemas.conversations import StartConversation
from repositories.conversations import ConversationRepositories, TicketRepositories

ConvoRouters = APIRouter(prefix="/conversations", tags=["conversations"])


@ConvoRouters.post("/chat/")
async def start_conversation_api(
    data: StartConversation, user: Annotated[str | None, Header()] = None
):
    query = data.query
    ticket_id = uuid4().hex
    # TODO create Ticket & conversation
    convo_repo = ConversationRepositories()
    ticket_repo = TicketRepositories()
    ticket_obj = ticket_repo.create(user_id=user, ticket_ref=ticket_id, subject=query, created_by=user)
    convo_obj = convo_repo.create(user_id=user, ticket_id=str(ticket_obj.get("_id")), query=query)

    # Run workflow to get ansert
    response = run_graph_workflow(user, query)
    resource = response.get("resource", None)
    if resource:
        response.pop("resource")

    convo_obj.update(response=response, resource_id=resource.get("_id"))
    
    return {"response": response}
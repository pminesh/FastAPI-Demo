from . import core_models, schemas
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, status, APIRouter, Response
from ..database import get_db
from .oauth2 import require_user
router = APIRouter()

# Create role
@router.post('/create_role/', status_code=status.HTTP_201_CREATED, response_model=schemas.RoleResponse)
def create_role(post: schemas.RoleBase, db: Session = Depends(get_db),user_id: str = Depends(require_user)):
    print('user_id: ', user_id)
    new_role = core_models.Role(**post.dict())
    db.add(new_role)
    db.commit()
    db.refresh(new_role)
    return new_role

# Search role
@router.get('/serach_roles/',response_model=schemas.ListRoleResponse)
def get_roles(db: Session = Depends(get_db), search: str = '',user_id: str = Depends(require_user)):
    print('user_id: ', user_id)

    roles = db.query(core_models.Role).group_by(core_models.Role.id).filter(
        core_models.Role.role_name.contains(search)).all()
    return {'status': 'success', 'results': len(roles), 'roles': roles}

# Get all role
@router.get('/get_all_roles/',response_model=schemas.ListRoleResponse)
def get_roles(db: Session = Depends(get_db),user_id: str = Depends(require_user)):
    print('owner_id: ', user_id)

    roles = db.query(core_models.Role).all()
    return {'status': 'success', 'results': len(roles), 'roles': roles}

# Delete role
@router.delete('/delete_role/{id}')
def delete_role(id: str, db: Session = Depends(get_db),user_id: str = Depends(require_user)):
    user = db.query(core_models.User).filter(core_models.User.id == user_id).first()
    
    role_query = db.query(core_models.Role).filter(core_models.Role.id == id)

    if user.role.role_name != 'Super Admin':
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail='You are not allowed to perform this action')
    
    role = role_query.first()
    if not role:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'No role with this id: {id} found')
    role_query.delete(synchronize_session=False)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)

# Update role
@router.put('/update_role/{id}', response_model=schemas.RoleResponse)
def update_role(id: str, post: schemas.UpdateRoleSchema, db: Session = Depends(get_db),user_id: str = Depends(require_user)):
    print('user_id: ', user_id)
    post_query = db.query(core_models.Role).filter(core_models.Role.id == id)
    updated_post = post_query.first()

    if not updated_post:
        raise HTTPException(status_code=status.HTTP_200_OK,
                            detail=f'No post with this id: {id} found')
    post_query.update(post.dict(exclude_unset=True), synchronize_session=False)
    db.commit()
    return updated_post
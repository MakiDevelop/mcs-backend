from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.db.session import get_db
from app.dependencies.auth import get_current_admin_user
from app.models.category import Category
from app.models.content import Content
from app.schemas.category import CategoryCreate, CategoryOut, CategoryUpdate
from app.services.audit import record_audit_log

settings = get_settings()
router = APIRouter(prefix=f"{settings.api_prefix}/categories", tags=["Categories"])


@router.get("", response_model=list[CategoryOut])
def list_categories(db: Session = Depends(get_db), current_user=Depends(get_current_admin_user)) -> list[CategoryOut]:
    return db.query(Category).order_by(Category.order_index.asc()).all()


@router.post("", response_model=CategoryOut, status_code=status.HTTP_201_CREATED)
def create_category(
    payload: CategoryCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_admin_user),
) -> CategoryOut:
    category = Category(**payload.model_dump())
    db.add(category)
    db.flush()
    record_audit_log(
        db,
        user=current_user,
        action="create_category",
        target_id=str(category.id),
        ip_address=request.client.host if request.client else None,
    )
    db.commit()
    db.refresh(category)
    return category


@router.put("/{category_id}", response_model=CategoryOut)
def update_category(
    category_id: int,
    payload: CategoryUpdate,
    request: Request,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_admin_user),
) -> CategoryOut:
    category = db.get(Category, category_id)
    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")

    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(category, key, value)

    db.add(category)
    record_audit_log(
        db,
        user=current_user,
        action="update_category",
        target_id=str(category.id),
        ip_address=request.client.host if request.client else None,
    )
    db.commit()
    db.refresh(category)
    return category


@router.delete("/{category_id}")
def delete_category(
    category_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_admin_user),
) -> dict:
    category = db.get(Category, category_id)
    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")

    has_content = db.query(Content).filter(Content.category_id == category_id, Content.is_deleted.is_(False)).first()
    if has_content:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Category has contents")

    db.delete(category)
    record_audit_log(
        db,
        user=current_user,
        action="delete_category",
        target_id=str(category.id),
        ip_address=request.client.host if request.client else None,
    )
    db.commit()
    return {"detail": "Category deleted"}

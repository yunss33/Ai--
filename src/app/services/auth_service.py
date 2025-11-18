#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
认证业务服务

封装登录 / 注册等与 User 模型相关的业务逻辑：
- authenticate_user: 校验用户名与密码
- login: 执行登录并返回访问令牌
- register_user: 注册新用户并返回用户与访问令牌
"""
from __future__ import annotations

from datetime import datetime
from typing import Optional, Tuple

from sqlalchemy.orm import Session

from app.core.security import create_access_token, get_password_hash, verify_password
from app.models.user import User


def get_user_by_username(db: Session, username: str) -> Optional[User]:
    return (
        db.query(User)
        .filter(User.username == username, User.is_deleted.is_(False))
        .first()
    )


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    return (
        db.query(User)
        .filter(User.email == email, User.is_deleted.is_(False))
        .first()
    )


def authenticate_user(
    db: Session,
    username: str,
    password: str,
) -> Optional[User]:
    """校验用户名和密码，成功返回 User，否则返回 None"""
    user = get_user_by_username(db, username)
    if user is None:
        return None
    if not user.status or user.is_deleted:
        return None
    if not verify_password(password, user.password):
        return None
    return user


def login(db: Session, username: str, password: str) -> str:
    """
    执行登录逻辑：
    - 校验用户名密码
    - 更新 last_login_at
    - 生成访问令牌并返回
    """
    user = authenticate_user(db, username, password)
    if user is None:
        raise ValueError("用户名或密码错误")

    user.last_login_at = datetime.utcnow()
    db.add(user)
    db.commit()

    return create_access_token(user_id=user.id, role=user.role)


def register_user(
    db: Session,
    *,
    username: str,
    password: str,
    real_name: str,
    email: str,
    phone: Optional[str] = None,
) -> Tuple[User, str]:
    """
    注册新用户：
    - 确保用户名 / 邮箱唯一
    - 对密码进行安全哈希
    - 默认角色为 student
    - 返回 (User, access_token)
    """
    if get_user_by_username(db, username) is not None:
        raise ValueError("用户名已存在")
    if email and get_user_by_email(db, email) is not None:
        raise ValueError("邮箱已被使用")

    hashed = get_password_hash(password)

    user = User(
        username=username,
        password=hashed,
        real_name=real_name,
        email=email,
        phone=phone,
        role="student",
        status=True,
        is_deleted=False,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    token = create_access_token(user_id=user.id, role=user.role)
    return user, token


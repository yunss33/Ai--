#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
认证与安全相关工具

这个文件主要回答两个问题：
1. 密码怎么安全地存进数据库？（PBKDF2-SHA256 + 随机盐，只存哈希）
2. 登录之后，后端怎么识别「当前是谁」？（itsdangerous 生成 access_token，FastAPI 依赖统一解析）
"""
from __future__ import annotations

import hashlib
import hmac
import os
import time
from datetime import timedelta
from typing import Any, Dict, Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from itsdangerous import BadSignature, SignatureExpired, Serializer
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.database import get_db
from app.models.user import User


settings = get_settings()

# FastAPI 文档推荐的 OAuth2 Password Bearer 方式：
# - 前端在请求头里带：Authorization: Bearer <access_token>
# - 这里的 oauth2_scheme 会自动帮我们把 token 字符串取出来
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


# ========================
# 一、密码哈希与校验
# ========================

_HASH_NAME = "sha256"          # 底层哈希算法
_PBKDF2_ITERATIONS = 100_000   # 迭代次数：越大越安全，但越耗时
_SALT_SIZE = 16                # 随机盐长度（字节）


def get_password_hash(password: str) -> str:
    """
    使用 PBKDF2-SHA256 生成密码哈希，写入数据库的就是这里返回的字符串。

    实现思路：
    1. 为每个密码生成一个随机 salt（防止彩虹表攻击）；
    2. 使用 hashlib.pbkdf2_hmac 做多次迭代计算；
    3. 把「算法名 / 迭代次数 / salt / hash」用 `$` 拼在一起，方便后续验证。

    返回格式示例：
        pbkdf2_sha256$100000$<salt_hex>$<hash_hex>
    """
    if not password:
        raise ValueError("密码不能为空")

    # 随机盐，对同一密码多次调用也会得到不同结果
    salt = os.urandom(_SALT_SIZE)
    dk = hashlib.pbkdf2_hmac(
        _HASH_NAME,
        password.encode("utf-8"),
        salt,
        _PBKDF2_ITERATIONS,
    )

    return "pbkdf2_{algo}${it}${salt}${dk}".format(
        algo=_HASH_NAME,
        it=_PBKDF2_ITERATIONS,
        salt=salt.hex(),
        dk=dk.hex(),
    )


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    校验明文密码是否与数据库中的哈希匹配。

    处理流程：
    1. 从 hashed_password 中解析出算法、迭代次数、salt 和原始哈希；
    2. 用同样的参数对用户当前输入的 plain_password 再做一次 PBKDF2；
    3. 使用 hmac.compare_digest 做常量时间比较，避免时间侧信道攻击。
    """
    try:
        method, it_str, salt_hex, dk_hex = hashed_password.split("$", 3)
        if not method.startswith("pbkdf2_"):
            return False
        iterations = int(it_str)
        salt = bytes.fromhex(salt_hex)
        expected = bytes.fromhex(dk_hex)
    except Exception:
        # 格式不对，直接视为校验失败
        return False

    new_dk = hashlib.pbkdf2_hmac(
        _HASH_NAME,
        plain_password.encode("utf-8"),
        salt,
        iterations,
    )
    return hmac.compare_digest(new_dk, expected)


# ========================
# 二、访问令牌生成与解析
# ========================


def _get_token_serializer() -> Serializer:
    """
    构造 itsdangerous 的序列化器：
    - 使用 settings.secret_key 作为签名密钥；
    - dumps(payload) 得到的字符串就是前端拿到的 access_token。
    """
    return Serializer(settings.secret_key)


def create_access_token(
    user_id: int,
    role: str,
    expires_delta: Optional[timedelta] = None,
) -> str:
    """
    创建访问令牌（access_token）。

    载荷包含：
    - user_id：用户主键
    - role：当前角色（student / admin）
    - iat：签发时间（秒级时间戳）
    - exp：过期时间（秒级时间戳）
    """
    now = int(time.time())
    if expires_delta is None:
        expires_delta = timedelta(minutes=settings.access_token_expires_minutes)
    exp_seconds = int(expires_delta.total_seconds())

    payload: Dict[str, Any] = {
        "user_id": user_id,
        "role": role,
        "iat": now,
        "exp": now + exp_seconds,
    }

    s = _get_token_serializer()
    token = s.dumps(payload)
    if isinstance(token, bytes):
        return token.decode("utf-8")
    return token


def decode_token(token: str) -> Optional[Dict[str, Any]]:
    """
    解析并验证访问令牌，成功返回 payload 字典，失败返回 None。

    验证内容：
    - 签名是否有效（防止伪造）；
    - 是否已过期（exp < 当前时间）。
    """
    if not token:
        return None

    s = _get_token_serializer()
    try:
        payload = s.loads(token)
    except (BadSignature, SignatureExpired):
        # 签名不合法或已过期
        return None
    except Exception:
        return None

    exp = payload.get("exp")
    try:
        if exp is None or int(exp) < int(time.time()):
            return None
    except Exception:
        return None

    return payload


# ========================
# 三、FastAPI 依赖：当前用户 / 管理员
# ========================


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    """
    FastAPI 依赖：获取当前登录用户。

    实现步骤：
    1. 通过 oauth2_scheme 从请求头中提取 Bearer token；
    2. 使用 decode_token 验证并解析令牌；
    3. 从 payload 中拿到 user_id，查询数据库中的 User 记录；
    4. 确认用户存在、未被逻辑删除、状态为启用；
    5. 返回 User 实体，供业务路由直接使用。
    """
    payload = decode_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效或已过期的访问令牌",
        )

    user_id = payload.get("user_id")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="令牌中缺少用户标识",
        )

    user: Optional[User] = (
        db.query(User)
        .filter(User.id == int(user_id), User.is_deleted.is_(False))
        .first()
    )
    if user is None or not user.status:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户不存在或已被禁用",
        )

    return user


def get_current_admin(current_user: User = Depends(get_current_user)) -> User:
    """
    FastAPI 依赖：获取当前管理员用户。

    在 get_current_user 的基础之上再检查一次 role 是否为 "admin"。
    """
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="当前用户无管理员权限",
        )
    return current_user


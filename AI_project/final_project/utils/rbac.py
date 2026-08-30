"""Streamlit and API authorization helpers."""

from __future__ import annotations

import streamlit as st

from utils.roles import can_access_page, get_role_config, normalize_job_role


def current_job_role() -> str:
    return normalize_job_role(st.session_state.get("job_role") or st.session_state.get("user_type"))


def current_user_id() -> str | None:
    return st.session_state.get("user_id")


def require_login() -> None:
    if not st.session_state.get("logged_in"):
        st.error("You must be signed in.")
        st.stop()


def require_page(page_key: str) -> None:
    require_login()
    role = current_job_role()
    if not can_access_page(role, page_key):
        st.error(f"Your role ({role}) is not authorized to open this page.")
        st.stop()


def require_capability(flag: str) -> None:
    require_login()
    cfg = get_role_config(current_job_role())
    if not cfg.get(flag):
        st.error("You are not authorized to perform this action.")
        st.stop()

from flask import Blueprint, request, jsonify
from src.models.models import db, Task
from src.middleware.auth import require_auth

tasks_bp = Blueprint("tasks", __name__)


@tasks_bp.get("/")
@require_auth
def list_tasks():
    tasks = Task.query.filter_by(user_id=request.user_id).all()
    return jsonify([t.to_dict() for t in tasks]), 200


@tasks_bp.post("/")
@require_auth
def create_task():
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Request body must be JSON"}), 400

    title = data.get("title", "").strip()
    if not title:
        return jsonify({"error": "title is required"}), 400

    task = Task(
        title=title,
        description=data.get("description", ""),
        user_id=request.user_id,
    )
    db.session.add(task)
    db.session.commit()
    return jsonify(task.to_dict()), 201


@tasks_bp.get("/<int:task_id>")
@require_auth
def get_task(task_id):
    task = Task.query.filter_by(id=task_id, user_id=request.user_id).first()
    if not task:
        return jsonify({"error": "Task not found"}), 404
    return jsonify(task.to_dict()), 200


@tasks_bp.patch("/<int:task_id>")
@require_auth
def update_task(task_id):
    task = Task.query.filter_by(id=task_id, user_id=request.user_id).first()
    if not task:
        return jsonify({"error": "Task not found"}), 404

    data = request.get_json(silent=True) or {}
    if "title" in data:
        task.title = data["title"].strip()
    if "description" in data:
        task.description = data["description"]
    if "done" in data:
        task.done = bool(data["done"])

    db.session.commit()
    return jsonify(task.to_dict()), 200


@tasks_bp.delete("/<int:task_id>")
@require_auth
def delete_task(task_id):
    task = Task.query.filter_by(id=task_id, user_id=request.user_id).first()
    if not task:
        return jsonify({"error": "Task not found"}), 404

    db.session.delete(task)
    db.session.commit()
    return jsonify({"message": "Task deleted"}), 200

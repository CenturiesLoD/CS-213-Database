from .routes import staff_bp
from .admin_routes import admin_bp
from .operator_routes import operator_bp
print("!! Import successful")

__all__ = ["staff_bp", "admin_bp", "operator_bp"]
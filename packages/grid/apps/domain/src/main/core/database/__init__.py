# stdlib
import os

# third party
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy_mixins import AllFeaturesMixin

db = SQLAlchemy()


class BaseModel(db.Model, AllFeaturesMixin):
    __abstract__ = True
    pass


# grid relative
from .tables.metadata import StorageMetadata
from .tables.groups import Group
from .tables.usergroup import UserGroup
from .tables.request import Request
from .tables.roles import Role
from .tables.roles import create_role
from .tables.setup import SetupConfig
from .tables.bin_obj import ObjectMetadata
from .tables.json_obj import DatasetGroup
from .tables.setup import create_setup
from .tables.user import User
from .tables.user import create_user
from .tables.bin_obj import BinObject
from .tables.json_obj import JsonObject
from .utils import expand_user_object
from .utils import model_to_json


def set_database_config(app, test_config=None, verbose=False):
    """Set configs to use SQL Alchemy library.

    Args:
        app: Flask application.
        test_config : Dictionary containing SQLAlchemy configs for test purposes.
        verbose : Level of flask application verbosity.
    Returns:
        app: Flask application.
    Raises:
        RuntimeError : If DATABASE_URL or test_config didn't initialize, RuntimeError exception will be raised.
    """
    db_url = os.environ.get("DATABASE_URL")
    migrate = Migrate(app, db)
    if test_config is None:
        if db_url:
            app.config.from_mapping(
                SQLALCHEMY_DATABASE_URI=db_url, SQLALCHEMY_TRACK_MODIFICATIONS=False
            )
        else:
            raise RuntimeError(
                "Invalid database address : Set DATABASE_URL environment var or add test_config parameter at create_app method."
            )
    else:
        app.config["SQLALCHEMY_DATABASE_URI"] = test_config["SQLALCHEMY_DATABASE_URI"]
        app.config["TESTING"] = (
            test_config["TESTING"] if test_config.get("TESTING") else True
        )
        app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = (
            test_config["SQLALCHEMY_TRACK_MODIFICATIONS"]
            if test_config.get("SQLALCHEMY_TRACK_MODIFICATIONS")
            else False
        )
    app.config["SQLALCHEMY_BINDS"] = {"bin_store": "sqlite:////tmp/binstore.db"}
    app.config["VERBOSE"] = verbose
    db.init_app(app)


def seed_db():
    global db

    new_role = Role(
        name="User",
        can_triage_requests=False,
        can_edit_settings=False,
        can_create_users=False,
        can_create_groups=False,
        can_edit_roles=False,
        can_manage_infrastructure=False,
        can_upload_data=False,
    )
    db.session.add(new_role)

    new_role = Role(
        name="Compliance Officer",
        can_triage_requests=True,
        can_edit_settings=False,
        can_create_users=False,
        can_create_groups=False,
        can_edit_roles=False,
        can_manage_infrastructure=False,
        can_upload_data=False,
    )
    db.session.add(new_role)

    new_role = Role(
        name="Administrator",
        can_triage_requests=True,
        can_edit_settings=True,
        can_create_users=True,
        can_create_groups=True,
        can_edit_roles=False,
        can_manage_infrastructure=False,
        can_upload_data=True,
    )
    db.session.add(new_role)

    new_role = Role(
        name="Owner",
        can_triage_requests=True,
        can_edit_settings=True,
        can_create_users=True,
        can_create_groups=True,
        can_edit_roles=True,
        can_manage_infrastructure=True,
        can_upload_data=True,
    )
    db.session.add(new_role)

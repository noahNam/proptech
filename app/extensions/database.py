from functools import partial

from flask import current_app
from flask_migrate import Migrate
from flask_sqlalchemy import (
    SQLAlchemy,
    get_state,
)
from sqlalchemy.orm import Session, scoped_session


class CustomSQLAlchemy(SQLAlchemy):
    def __init__(self, *args, **kwargs):
        SQLAlchemy.__init__(self, *args, **kwargs)
        self.session.using_bind = lambda s: self.session().using_bind(s)

    def create_scoped_session(self, options=None):
        if options is None:
            options = {}

        scopefunc = options.pop("scopefunc", None)
        options.setdefault("query_cls", self.Query)
        return scoped_session(
            # session_factory -> CustomSession 클래스 생성
            partial(CustomSession, self, **options),
            scopefunc=scopefunc,
        )


class CustomSession(Session):
    def __init__(
        self,
        db_: CustomSQLAlchemy,
        autocommit=False,
        autoflush=True,
        bind=None,
        binds=None,
        **kwargs
    ):
        # parameter : bind, binds = None -> 사용 하지 않지만 명시적 표시 필요
        self.app = db_.get_app()
        self.db = db_
        self._bind_name = None

        Session.__init__(
            self,
            autocommit=autocommit,
            autoflush=autoflush,
            bind=db_.engine,
            binds=db_.get_binds(self.app),
            **kwargs,
        )

    def get_bind(self, mapper=None, clause=None, **kwargs):
        try:
            state = get_state(self.app)
        except (AssertionError, AttributeError, TypeError) as err:
            current_app.logger.info(
                "Cannot get configuration. default bind. Error:" + err
            )
            return Session.get_bind(self, mapper, clause, **kwargs)

            # SQLALCHEMY_BINDS 설정이 없다면, 기본 SQLALCHEMY_DATABASE_URI 사용
        if not state or not self.app.config["SQLALCHEMY_BINDS"]:
            return Session.get_bind(self, mapper, clause, **kwargs)

            # 명시적 bind 설정
        if self._bind_name:
            return state.db.get_engine(self.app, bind=self._bind_name)
        else:
            # 명시적 bind 설정이 없다면 default 연결
            return Session.get_bind(self, mapper, clause, **kwargs)

    def using_bind(self, name):
        """
            새로운 session 객체 생성 후 bind 정보 업데이트
        """
        if (
            self.app.config.get("TESTING")
            or self.app.config.get("ENV") == "development"
        ):
            # 테스트 중 혹은 개발 서버일 때 using_bind("read_only")를 통해 reader bind 호출시, 동일한 기존 세션 반환
            # session: app.extensions.database.session, Not self
            return session
        bind_session = CustomSession(self.db)
        vars(bind_session).update(vars(self))
        bind_session._bind_name = name
        return bind_session


db = CustomSQLAlchemy()
migrate = Migrate()
session: CustomSession = db.session

class AuthRouter:
    def db_for_read(self, model, **hints):
        if model._meta.app_label in ('auth', 'sessions'):
            return 'pid_db'
        return None

    def db_for_write(self, model, **hints):
        if model._meta.app_label in ('auth', 'sessions'):
            return 'pid_db'
        return None

    def allow_relation(self, obj1, obj2, **hints):
        if (
            obj1._meta.app_label in ('auth', 'sessions') or
            obj2._meta.app_label in ('auth', 'sessions')
        ):
            return True
        return None

    def allow_migrate(self, db, app_label, **hints):
        if app_label in ('auth', 'sessions'):
            return db == 'pid_db'
        return db == 'default'
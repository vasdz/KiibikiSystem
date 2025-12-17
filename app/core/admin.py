from sqladmin import ModelView, Admin
from app.modules.auth.models import User
from app.modules.ledger.models import Transaction
from app.modules.proofs.models import Proof
from app.modules.audit.models import AuditLog

# 1. Настройка отображения Юзеров
class UserAdmin(ModelView, model=User):
    column_list = [User.id, User.username, User.full_name, User.role, User.balance]
    column_searchable_list = [User.username, User.full_name]
    column_sortable_list = [User.id, User.balance]
    icon = "fa-solid fa-user"
    name = "Студент/Сотрудник"
    name_plural = "Пользователи"

# 2. Настройка отображения Транзакций (Леджера)
class TransactionAdmin(ModelView, model=Transaction):
    column_list = [Transaction.id, Transaction.amount, Transaction.reason, Transaction.created_at]
    column_default_sort = ("created_at", True) # Сортировка по свежести
    can_create = False # Транзакции создавать руками НЕЛЬЗЯ (только через крипто-API)
    can_edit = False   # Блокчейн нельзя править!
    can_delete = False # Удалять историю нельзя
    icon = "fa-solid fa-link"
    name = "Транзакция"
    name_plural = "Реестр (Ledger)"

# 3. Настройка отображения Файлов (Proofs)
class ProofAdmin(ModelView, model=Proof):
    column_list = [Proof.id, Proof.user_id, Proof.filename, Proof.status, Proof.created_at]
    column_sortable_list = [Proof.created_at, Proof.status]
    column_labels = {Proof.user_id: "ID Студента", Proof.filename: "Имя файла"}
    icon = "fa-solid fa-file-contract"
    name = "Доказательство"
    name_plural = "Загруженные файлы"

# 4. Настройка Журнала Безопасности (Audit)
class AuditAdmin(ModelView, model=AuditLog):
    column_list = [AuditLog.id, AuditLog.timestamp, AuditLog.action, AuditLog.details, AuditLog.actor_id]
    column_default_sort = ("timestamp", True)
    column_searchable_list = [AuditLog.action, AuditLog.details]
    can_create = False
    can_edit = False
    can_delete = False # Логи удалять нельзя!
    icon = "fa-solid fa-shield-halved"
    name = "Запись лога"
    name_plural = "Журнал Безопасности"

# 5. Функция инициализации
def setup_admin(app, engine):
    admin = Admin(app, engine, title="Kiibiki Admin Panel")
    admin.add_view(UserAdmin)
    admin.add_view(TransactionAdmin)
    admin.add_view(ProofAdmin)
    admin.add_view(AuditAdmin)
